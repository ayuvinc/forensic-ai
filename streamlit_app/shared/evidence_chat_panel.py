"""Evidence Chat Panel — persistent collapsible chat panel (CONV-02).

Injected on all engagement pages as a shared component. NOT a standalone page.

Usage (at the bottom of any engagement page):
    from streamlit_app.shared.evidence_chat_panel import render_evidence_chat_panel
    render_evidence_chat_panel(st, case_id)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def render_evidence_chat_panel(st, case_id: Optional[str]) -> None:
    """Render the persistent collapsible evidence chat panel.

    The panel is a no-op when no case is active (case_id is None or empty).
    Uses st.session_state for per-session conversation history and EvidenceChat instance.
    """
    if not case_id:
        return

    # Lazy import to avoid circular imports at module load
    from tools.document_manager import DocumentManager
    from workflows.evidence_chat import EvidenceChat

    # ── Initialise session state ──────────────────────────────────────────────
    _cem_key     = f"cem_{case_id}"
    _history_key = f"cem_history_{case_id}"
    _doc_sel_key = f"cem_doc_sel_{case_id}"

    if _cem_key not in st.session_state:
        st.session_state[_cem_key] = EvidenceChat()
    if _history_key not in st.session_state:
        st.session_state[_history_key] = []
    if _doc_sel_key not in st.session_state:
        st.session_state[_doc_sel_key] = []

    cem: EvidenceChat = st.session_state[_cem_key]
    history: list[dict] = st.session_state[_history_key]

    # ── Panel container ───────────────────────────────────────────────────────
    with st.expander("Evidence Chat (CEM)", expanded=False):
        st.warning(
            "Evidence Exploration Mode — outputs are not reviewed deliverables. "
            "Use the Investigation pipeline for reviewed reports.",
            icon="⚠",
        )

        # Two-column layout: left = doc selector, right = chat
        col_docs, col_chat = st.columns([1, 2])

        # ── Left panel: document selector ─────────────────────────────────────
        with col_docs:
            st.markdown("**Documents**")
            try:
                dm = DocumentManager(case_id)
                index = dm.get_index()
                docs = index.documents
            except Exception:
                docs = []

            if not docs:
                st.caption("No documents registered for this engagement.")
                selected_ids: list[str] = []
            else:
                selected_ids = []
                for doc in docs:
                    # Embedding status badge
                    try:
                        from tools.embedding_engine import EmbeddingEngine
                        eng = EmbeddingEngine(case_id)
                        chunk_n = eng.chunk_count(doc.doc_id)
                        badge = f" [{chunk_n} chunks]" if chunk_n > 0 else " [not indexed]"
                    except Exception:
                        badge = ""

                    checked = st.checkbox(
                        f"{doc.filename}{badge}",
                        key=f"cem_doc_{case_id}_{doc.doc_id}",
                    )
                    if checked:
                        selected_ids.append(doc.doc_id)

            st.session_state[_doc_sel_key] = selected_ids

            # End conversation button
            if history and st.button("End Conversation", key=f"cem_end_{case_id}"):
                saved_path = cem.session_end(case_id)
                st.success(f"Conversation saved to {saved_path.name}")
                # Reset for next session
                st.session_state[_cem_key] = EvidenceChat()
                st.session_state[_history_key] = []
                st.rerun()

        # ── Right panel: chat interface ────────────────────────────────────────
        with col_chat:
            # History trimming notice
            if len(history) > 100:
                st.info(
                    "Older turns have been trimmed from context. Full transcript saved to Working Papers."
                )

            # Render conversation history
            for turn in history:
                role    = turn.get("role", "user")
                content = turn.get("content", "")
                with st.chat_message(role):
                    st.write(content)

                    # Action buttons — only on assistant turns
                    if role == "assistant":
                        _render_action_buttons(st, case_id, content, turn.get("_idx", 0))

            # Chat input
            user_input = st.chat_input(
                "Ask about the evidence...",
                key=f"cem_input_{case_id}",
            )
            if user_input:
                with st.chat_message("user"):
                    st.write(user_input)

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        # Pass a copy of history without the _idx metadata keys
                        api_history = [
                            {"role": h["role"], "content": h["content"]}
                            for h in history
                            if h.get("role") in ("user", "assistant")
                        ]
                        reply = cem.chat(
                            case_id=case_id,
                            message=user_input,
                            selected_doc_ids=selected_ids,
                            conversation_history=api_history,
                        )
                    st.write(reply)
                    _render_action_buttons(st, case_id, reply, len(history))

                # Append to history with a local index for button key uniqueness
                idx = len(history)
                history.append({"role": "user", "content": user_input, "_idx": idx})
                history.append({"role": "assistant", "content": reply, "_idx": idx + 1})
                st.session_state[_history_key] = history
                st.rerun()


def _render_action_buttons(st, case_id: str, content: str, idx: int) -> None:
    """Render Save as Lead / Save as Key Fact / Save as Red Flag buttons for an assistant turn."""
    from tools.project_manager import ProjectManager
    pm = ProjectManager()

    btn_cols = st.columns(4)

    with btn_cols[0]:
        if st.button("Save as Lead", key=f"cem_lead_{case_id}_{idx}"):
            try:
                _append_leads_register(case_id, content)
                _write_audit(case_id, "EVIDENCE_CHAT_LEAD_SAVED", {"excerpt": content[:200]})
                st.success("Saved as lead.")
            except Exception as exc:
                st.error(f"Save failed: {exc}")

    with btn_cols[1]:
        if st.button("Save as Key Fact", key=f"cem_fact_{case_id}_{idx}"):
            try:
                pm.add_key_fact(case_id, {
                    "fact":   content[:500],
                    "source": "Evidence Chat (CEM)",
                    "date":   datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                })
                st.success("Saved as key fact.")
            except Exception as exc:
                st.error(f"Save failed: {exc}")

    with btn_cols[2]:
        if st.button("Save as Red Flag", key=f"cem_rf_{case_id}_{idx}"):
            severity = st.selectbox(
                "Severity",
                ["high", "medium", "low"],
                key=f"cem_rf_sev_{case_id}_{idx}",
            )
            if st.button("Confirm Red Flag", key=f"cem_rf_confirm_{case_id}_{idx}"):
                try:
                    pm.add_red_flag(case_id, {
                        "description": content[:500],
                        "severity":    severity,
                        "source":      "Evidence Chat (CEM)",
                    })
                    st.success("Saved as red flag.")
                except Exception as exc:
                    st.error(f"Save failed: {exc}")

    with btn_cols[3]:
        if st.button("Flag Response", key=f"cem_flag_{case_id}_{idx}"):
            _write_audit(case_id, "EVIDENCE_CHAT_RESPONSE_FLAGGED", {
                "excerpt": content[:200],
                "flagged_at": datetime.now(timezone.utc).isoformat(),
            })
            st.info("Response flagged in transcript.")


def _append_leads_register(case_id: str, content: str) -> None:
    """Append a lead to D_Working_Papers/leads_register.json."""
    from tools.file_tools import case_dir
    import os
    wp_dir = case_dir(case_id) / "D_Working_Papers"
    wp_dir.mkdir(parents=True, exist_ok=True)
    leads_path = wp_dir / "leads_register.json"
    leads: list[dict] = []
    if leads_path.exists():
        try:
            leads = json.loads(leads_path.read_text(encoding="utf-8"))
        except Exception:
            leads = []
    leads.append({
        "description": content[:500],
        "status":      "open",
        "source":      "Evidence Chat (CEM)",
        "added_at":    datetime.now(timezone.utc).isoformat(),
    })
    tmp = leads_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(leads, indent=2), encoding="utf-8")
    os.replace(tmp, leads_path)


def _write_audit(case_id: str, event: str, detail: dict) -> None:
    """Write a single audit event for CEM actions."""
    try:
        from tools.file_tools import append_audit_event
        append_audit_event(case_id, {"event": event, **detail})
    except Exception:
        pass
