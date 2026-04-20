"""EvidenceChat — conversational evidence exploration (CONV-01).

Single Sonnet turn per message. Context capped at config.CEM_CONTEXT_CHARS.
Output is not a reviewed deliverable — for exploration only.

Usage:
    cem = EvidenceChat()
    response = cem.chat(
        case_id="project-alpha",
        message="What does the bank statement show?",
        selected_doc_ids=[],          # empty = all registered docs
        conversation_history=[],
    )
    cem.session_end(case_id)          # saves transcript to D_Working_Papers/
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import anthropic

import config
from tools.file_tools import append_audit_event, case_dir

_SYSTEM_PROMPT = """You are a forensic evidence review assistant.

Your role is to help the consultant explore documents registered for this engagement.

STRICT RULES:
1. Only present findings and observations directly supported by the registered documents.
2. For every observation, state the source document (by filename) and quote or paraphrase the relevant passage.
3. You may explain forensic concepts, fraud typologies, and accounting patterns as background context.
4. Do NOT present inferences as conclusions. Use qualified language: "evidence suggests", "it appears", "consistent with".
5. Do NOT answer questions about topics outside the registered documents unless they are general forensic/accounting concepts.
6. All outputs are PRELIMINARY — not reviewed deliverables.
7. If a question cannot be answered from the registered documents, say so explicitly."""

_WATERMARK = "EVIDENCE EXPLORATION SESSION — PRELIMINARY — NOT FOR CLIENT REVIEW"


class EvidenceChat:
    """Conversational evidence exploration over registered case documents.

    Each instance tracks the current session transcript so session_end() can
    flush the full conversation to D_Working_Papers/ as a markdown file.
    """

    def __init__(self, anthropic_client: Optional[anthropic.Anthropic] = None) -> None:
        self._client = anthropic_client or anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        # In-memory transcript for this session: list of {"role", "content", "timestamp"}
        self._transcript: list[dict] = []
        self._session_ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # ── Public API ─────────────────────────────────────────────────────────────

    def chat(
        self,
        case_id: str,
        message: str,
        selected_doc_ids: list[str],
        conversation_history: list[dict],
    ) -> str:
        """Send one message to Sonnet and return the assistant reply.

        Args:
            case_id: Active project slug or legacy UUID.
            message: The consultant's question.
            selected_doc_ids: If non-empty, retrieval is scoped to these doc_ids only.
            conversation_history: Prior turns — list of {"role": "user"|"assistant", "content": str}.
                Oldest entries are dropped first if context cap is approached.
        """
        context_block = self._build_context(case_id, message, selected_doc_ids)

        # Trim history to fit within context cap
        history = _trim_history(conversation_history, context_block, config.CEM_CONTEXT_CHARS)

        messages = history + [{"role": "user", "content": message}]

        # Inject context as the first user message if history is empty, otherwise prepend
        if context_block:
            # Always include the document context as a system-level injection via the first turn
            context_message = (
                f"[DOCUMENT CONTEXT — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}]\n\n"
                f"{context_block}\n\n"
                f"[END DOCUMENT CONTEXT]\n\n"
                f"Consultant question: {message}"
            )
            # Replace the last user message with one that includes context
            messages[-1] = {"role": "user", "content": context_message}

        response = self._client.messages.create(
            model=config.SONNET,
            max_tokens=2048,
            system=_SYSTEM_PROMPT,
            messages=messages,
        )
        reply = response.content[0].text.strip()

        # Record in session transcript
        ts = datetime.now(timezone.utc).isoformat()
        self._transcript.append({"role": "user", "content": message, "timestamp": ts})
        self._transcript.append({"role": "assistant", "content": reply, "timestamp": ts})

        return reply

    def session_end(self, case_id: str) -> Path:
        """Flush the full conversation transcript to D_Working_Papers/.

        Returns the path of the written file. Safe to call with an empty transcript.
        """
        cdir = case_dir(case_id)
        wp_dir = cdir / "D_Working_Papers"
        wp_dir.mkdir(parents=True, exist_ok=True)

        filename = f"evidence_chat_{self._session_ts}.md"
        out_path = wp_dir / filename

        content = _render_transcript(case_id, self._session_ts, self._transcript)

        tmp = out_path.with_suffix(".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, out_path)

        append_audit_event(case_id, {
            "event":      "EVIDENCE_CHAT_SAVED",
            "filename":   filename,
            "turn_count": len(self._transcript) // 2,
        })

        return out_path

    def session_end_recovered(self, case_id: str) -> Path:
        """Emergency save on mid-session app close — uses a distinct filename."""
        cdir = case_dir(case_id)
        wp_dir = cdir / "D_Working_Papers"
        wp_dir.mkdir(parents=True, exist_ok=True)

        recovered_ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"evidence_chat_{recovered_ts}_recovered.md"
        out_path = wp_dir / filename

        content = _render_transcript(case_id, recovered_ts, self._transcript)

        tmp = out_path.with_suffix(".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, out_path)

        return out_path

    # ── Context assembly ──────────────────────────────────────────────────────

    def _build_context(self, case_id: str, query: str, selected_doc_ids: list[str]) -> str:
        """Assemble document context for the current turn, capped at CEM_CONTEXT_CHARS."""
        parts: list[str] = []
        remaining = config.CEM_CONTEXT_CHARS

        # 1. Document index summary
        idx_summary = _load_document_index_summary(case_id, selected_doc_ids)
        if idx_summary:
            parts.append(f"## Registered Documents\n{idx_summary}")
            remaining -= len(idx_summary)

        # 2. key_facts.json + red_flags.json
        kf_rf = _load_key_facts_and_flags(case_id)
        if kf_rf and remaining > 500:
            chunk = kf_rf[:remaining - 200]
            parts.append(chunk)
            remaining -= len(chunk)

        # 3. Relevant chunks — EmbeddingEngine first, fallback to keyword match
        if remaining > 500:
            doc_context = _retrieve_doc_context(case_id, query, selected_doc_ids, remaining - 100)
            if doc_context:
                parts.append(f"## Relevant Passages\n{doc_context}")

        return "\n\n".join(parts)


# ── Module-level helpers ───────────────────────────────────────────────────────

def _load_document_index_summary(case_id: str, selected_doc_ids: list[str]) -> str:
    """Return a compact DocumentIndex summary, filtered by selected_doc_ids if provided."""
    try:
        from tools.document_manager import DocumentManager
        dm = DocumentManager(case_id)
        index = dm.get_index()
        docs = index.documents
        if selected_doc_ids:
            docs = [d for d in docs if d.doc_id in selected_doc_ids]
        lines = [
            f"- [{d.doc_id}] {d.filename} ({d.char_count:,} chars)"
            + (f" — {d.summary[:120]}..." if d.summary else "")
            for d in docs
        ]
        return "\n".join(lines) if lines else ""
    except Exception:
        return ""


def _load_key_facts_and_flags(case_id: str) -> str:
    """Load key_facts.json and red_flags.json from D_Working_Papers/."""
    cdir = case_dir(case_id)
    wp_dir = cdir / "D_Working_Papers"
    parts: list[str] = []

    kf_path = wp_dir / "key_facts.json"
    if kf_path.exists():
        try:
            facts = json.loads(kf_path.read_text(encoding="utf-8"))
            if facts:
                lines = [f"- {f.get('fact', '')} (source: {f.get('source', '')})" for f in facts[:20]]
                parts.append("## Key Facts\n" + "\n".join(lines))
        except Exception:
            pass

    rf_path = wp_dir / "red_flags.json"
    if rf_path.exists():
        try:
            flags = json.loads(rf_path.read_text(encoding="utf-8"))
            if flags:
                lines = [f"- [{f.get('severity', '').upper()}] {f.get('description', '')}" for f in flags[:20]]
                parts.append("## Red Flags\n" + "\n".join(lines))
        except Exception:
            pass

    return "\n\n".join(parts)


def _retrieve_doc_context(
    case_id: str, query: str, selected_doc_ids: list[str], max_chars: int
) -> str:
    """Try EmbeddingEngine.retrieve() first; fallback to DocumentManager.find_relevant_docs()."""
    try:
        from tools.embedding_engine import EmbeddingEngine
        eng = EmbeddingEngine(case_id)
        chunks = eng.retrieve(query, case_id=case_id, top_k=5)
        if chunks:
            texts: list[str] = []
            total = 0
            for chunk in chunks:
                # ChunkResult has .text and .doc_id attributes
                if selected_doc_ids and chunk.doc_id not in selected_doc_ids:
                    continue
                snippet = f"[{chunk.doc_id}] {chunk.text[:800]}"
                if total + len(snippet) > max_chars:
                    break
                texts.append(snippet)
                total += len(snippet)
            if texts:
                return "\n\n".join(texts)
    except Exception:
        pass

    # Fallback: keyword-ranked full-doc excerpts
    try:
        from tools.document_manager import DocumentManager
        dm = DocumentManager(case_id)
        relevant = dm.find_relevant_docs(query)
        if selected_doc_ids:
            relevant = [d for d in relevant if d.doc_id in selected_doc_ids]
        texts: list[str] = []
        total = 0
        for doc in relevant[:5]:
            excerpt = (doc.summary or "")[:800]
            snippet = f"[{doc.doc_id}] {doc.filename}: {excerpt}"
            if total + len(snippet) > max_chars:
                break
            texts.append(snippet)
            total += len(snippet)
        return "\n\n".join(texts)
    except Exception:
        return ""


def _trim_history(
    history: list[dict], context_block: str, cap: int
) -> list[dict]:
    """Drop oldest turns from history until total chars fit within cap."""
    context_len = len(context_block)
    history_chars = sum(len(h.get("content", "")) for h in history)

    while history and context_len + history_chars > cap and len(history) >= 2:
        # Drop oldest pair (user + assistant)
        dropped_user = history.pop(0)
        dropped_asst = history.pop(0) if history else None
        history_chars -= len(dropped_user.get("content", ""))
        if dropped_asst:
            history_chars -= len(dropped_asst.get("content", ""))

    return history


def _render_transcript(case_id: str, session_ts: str, transcript: list[dict]) -> str:
    """Render the session transcript as a markdown document."""
    header = (
        f"<!-- {_WATERMARK} -->\n\n"
        f"# Evidence Exploration Session — {_WATERMARK}\n\n"
        f"**Case:** {case_id}  \n"
        f"**Session started:** {session_ts.replace('_', ' ')} UTC  \n"
        f"**Turns:** {len(transcript) // 2}\n\n---\n\n"
    )
    body_parts: list[str] = []
    for turn in transcript:
        role = turn.get("role", "unknown").capitalize()
        content = turn.get("content", "")
        ts = turn.get("timestamp", "")
        body_parts.append(f"**{role}** _{ts}_\n\n{content}")

    return header + "\n\n---\n\n".join(body_parts)
