"""WorkpaperGenerator — interim workpaper generation (BA-WORK-01).

Generates a structured interim workpaper from accumulated case materials.
Single Sonnet call. Output: D_Working_Papers/interim_workpaper.v{N}.md

AK decisions (2026-04-19):
  - Trigger: any point after Junior draft exists — Maher-initiated, never auto
  - Structure: 9 sections, Maher confirms opt-in/opt-out at generation time
  - Promotion: workpapers can be promoted to F_Final/ with PROMOTED_FROM_WORKPAPER flag
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import anthropic

from config import ANTHROPIC_API_KEY, SONNET
from tools.file_tools import append_audit_event, case_dir


_WATERMARK = "PRELIMINARY — INTERNAL USE ONLY — NOT FOR CLIENT DISTRIBUTION"

_SYSTEM_PROMPT = """You are a senior forensic consultant generating an interim workpaper.

LANGUAGE STANDARD: ACFE Internal Review
  - Narrative style. Qualified language for inferences ('evidence suggests', 'it appears').
  - Cite every claim to a registered document by doc_id and filename.
  - Past tense. Third person. No pronouns.
  - If no documentary support exists for a finding, label it:
    ANALYTICAL INFERENCE — no documentary evidence found yet

OUTPUT FORMAT: Structured Markdown with exactly the sections provided in the user prompt.
Do not add sections, do not remove sections, do not reorder sections.
Each finding must include: description, evidence citation (doc_id + filename), and implication.
Keep it professional, concise, and actionable."""


def _next_version(wp_dir: Path) -> int:
    """Return next available version number so existing workpapers are never overwritten."""
    pattern = re.compile(r"interim_workpaper\.v(\d+)\.md$")
    existing = [
        int(m.group(1))
        for f in wp_dir.iterdir() if (m := pattern.match(f.name))
    ]
    return max(existing, default=0) + 1


class WorkpaperGenerator:
    """Generates interim workpapers from accumulated case materials.

    Usage:
        gen = WorkpaperGenerator()
        path = gen.generate(case_id="project-alpha-frm", source_artifacts={...})
    """

    def __init__(self, anthropic_client: Optional[anthropic.Anthropic] = None) -> None:
        self._client = anthropic_client or anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def generate(self, case_id: str, source_artifacts: dict) -> Path:
        """Generate an interim workpaper and write to D_Working_Papers/.

        source_artifacts dict keys (all optional):
          materials_reviewed  — list of {"doc_id", "filename"} dicts from DocumentIndex
          key_facts           — list of {"fact", "source", "date"} dicts
          red_flags           — list of {"description", "severity"} dicts
          junior_findings     — list of findings from JuniorDraft (if pipeline ran)
          open_leads          — list of {"description", "status"} dicts
          open_questions      — list of strings from JuniorDraft
          session_count       — int
          document_count      — int

        Returns Path to the written workpaper file.
        """
        cdir = case_dir(case_id)
        wp_dir = cdir / "D_Working_Papers"
        wp_dir.mkdir(parents=True, exist_ok=True)

        user_prompt = self._build_prompt(case_id, source_artifacts)
        content = self._call_sonnet(user_prompt)

        version = _next_version(wp_dir)
        wp_path = wp_dir / f"interim_workpaper.v{version}.md"

        # Prepend watermark header before writing
        watermark_header = (
            f"<!-- {_WATERMARK} -->\n\n"
            f"# INTERIM WORKPAPER — {_WATERMARK}\n\n"
            f"**Case:** {case_id}  \n"
            f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  \n"
            f"**Version:** v{version}\n\n---\n\n"
        )
        final_content = watermark_header + content

        tmp = wp_path.with_suffix(".tmp")
        tmp.write_text(final_content, encoding="utf-8")
        os.replace(tmp, wp_path)

        # Audit event — append to case audit log
        append_audit_event(case_id, {
            "event":    "WORKPAPER_GENERATED",
            "version":  version,
            "path":     str(wp_path.relative_to(cdir)),
            "model":    SONNET,
            "sections": list(source_artifacts.keys()),
        })

        return wp_path

    def _build_prompt(self, case_id: str, artifacts: dict) -> str:
        materials = artifacts.get("materials_reviewed") or []
        key_facts = artifacts.get("key_facts") or []
        red_flags = artifacts.get("red_flags") or []
        findings  = artifacts.get("junior_findings") or []
        open_leads = artifacts.get("open_leads") or []
        open_questions = artifacts.get("open_questions") or []
        session_count = artifacts.get("session_count", 0)
        doc_count     = artifacts.get("document_count", len(materials))

        mat_text = "\n".join(
            f"  - [{d.get('doc_id','')}] {d.get('filename','')}" for d in materials
        ) or "  (none registered)"

        facts_text = "\n".join(
            f"  - {f.get('fact','')} (Source: {f.get('source','')}, Date: {f.get('date','')})"
            for f in key_facts
        ) or "  (none recorded)"

        flags_text = "\n".join(
            f"  - [{f.get('severity','').upper()}] {f.get('description','')}"
            for f in sorted(red_flags, key=lambda x: {"high":0,"medium":1,"low":2}.get(x.get("severity","low"),3))
        ) or "  (none recorded)"

        findings_text = ""
        for i, f in enumerate(findings, 1):
            title = f.get("title") or f.get("finding") or f"Finding {i}"
            desc  = f.get("description") or f.get("summary") or ""
            ev    = f.get("evidence") or f.get("citations") or "No documentary citation"
            findings_text += f"\n  {i}. **{title}**\n     {desc}\n     Evidence: {ev}\n"
        if not findings_text:
            findings_text = "  (no findings from pipeline yet — enter ANALYTICAL INFERENCE items below)"

        leads_text = "\n".join(
            f"  - [{l.get('status','open').upper()}] {l.get('description','')}"
            for l in open_leads
        ) or "  (none)"

        questions_text = "\n".join(f"  - {q}" for q in open_questions) or "  (none)"

        return f"""Generate an interim workpaper for case: {case_id}

Structure the workpaper with EXACTLY these 9 sections in this order:

## 1. HEADER
Include: PRELIMINARY watermark, case ID, generation date, version number.

## 2. MATERIALS REVIEWED
Documents registered:
{mat_text}

## 3. KEY FACTS
{facts_text}

## 4. RED FLAGS
(sorted high → medium → low severity)
{flags_text}

## 5. EMERGING FINDINGS
Generate 3–7 findings from the materials and context above.
Each finding MUST: state the observation, cite at least one registered document
(use doc_id and filename), and state the implication.
If no documentary support exists, label it: ANALYTICAL INFERENCE — no documentary evidence found yet
{findings_text}

## 6. LEADS REGISTER STATUS
{leads_text}

## 7. OPEN QUESTIONS
{questions_text}

## 8. NEXT STEPS
Generate 3–5 concrete next steps based on open questions, unconfirmed leads, and gaps in the materials.
Be specific — name the document to obtain, the person to interview, or the data to analyse.

## 9. AUDIT TRAIL SUMMARY
Sessions: {session_count} | Documents: {doc_count} | Facts: {len(key_facts)} | Red flags: {len(red_flags)}

Important:
- Maintain ACFE Internal Review language standard throughout.
- Use qualified language for inferences. Past tense. Third person.
- Never overstate confidence. Never present inference as conclusion.
"""

    def _call_sonnet(self, user_prompt: str) -> str:
        resp = self._client.messages.create(
            model=SONNET,
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return resp.content[0].text.strip()
