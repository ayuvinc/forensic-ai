# workflows/policy_sop_cobuild.py — Sprint-IA-04 (BA-IA-09)
#
# Co-build orchestrator for Policy/SOP workflows.
# The Streamlit page (04_Policy_SOP.py) drives the interactive loop;
# this module provides the four stateless API-call functions and the
# final assembly function.
#
# CLI path (run.py) still uses workflows/policy_sop.py (single-pass) — untouched.

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional

import anthropic

from config import ANTHROPIC_API_KEY, HAIKU, SONNET
from schemas.artifacts import FinalDeliverable
from schemas.case import CaseIntake
from schemas.policy_sop_cobuild import CoBuildState
from tools.file_tools import append_audit_event, write_artifact, write_final_report


# ── helpers ───────────────────────────────────────────────────────────────────

def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def _strip_html(text: str) -> str:
    """Remove HTML/script tags from user-supplied text before model injection."""
    return re.sub(r"<[^>]+>", "", text)


# ── Step 3: propose section structure ─────────────────────────────────────────

def propose_structure(
    intake: CaseIntake,
    params: dict,
    aic_context: str = "",
    custom_scope: Optional[dict] = None,
) -> list[str]:
    """Sonnet call — returns 6–14 section title strings for this document type.

    Args:
        intake: CaseIntake with client, jurisdiction, description.
        params: dict with doc_type, doc_subtype, gap_analysis.
        aic_context: joined answers from the AIC questions stage.
        custom_scope: answers from the custom scoping conversation (custom type only).
    """
    doc_type = params.get("doc_type", "policy")
    doc_subtype = params.get("doc_subtype", "aml_cft_policy")
    gap_analysis = params.get("gap_analysis", "new")

    custom_block = ""
    if custom_scope:
        custom_block = "\n".join(
            f"- {k.replace('_', ' ').title()}: {v}"
            for k, v in custom_scope.items()
        )
        custom_block = f"\nCUSTOM DOCUMENT SCOPE:\n{custom_block}"

    aic_block = f"\nADDITIONAL CONTEXT FROM CONSULTANT:\n{aic_context}" if aic_context.strip() else ""

    system = (
        f"You are a senior forensic and compliance consultant drafting a {doc_type} "
        f"for a client in the {intake.industry or 'financial services'} sector."
    )

    user = f"""Propose a logical section structure for the following document.

DOCUMENT TYPE: {doc_subtype.replace('_', ' ').title()}
CLIENT: {intake.client_name}
JURISDICTION: {intake.primary_jurisdiction}
MODE: {"Gap analysis of existing document" if gap_analysis == "gap" else "New document"}
DESCRIPTION: {intake.description or "No additional description provided."}
{custom_block}{aic_block}

Return ONLY a numbered list of section titles, one per line, with no additional text.
Example format:
1. Purpose and Scope
2. Definitions
3. Policy Statement

Include between 6 and 14 sections appropriate for this document type and jurisdiction.
Do not include section numbers in your titles — the calling code will add them."""

    resp = _client().messages.create(
        model=SONNET,
        max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    raw = resp.content[0].text.strip()

    # Parse numbered list — strip leading "N." or "N)" prefixes
    titles = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # Remove "1. ", "1) ", "• ", "- " prefixes
        cleaned = re.sub(r"^[\d]+[.)]\s*", "", line).strip()
        cleaned = re.sub(r"^[-•]\s*", "", cleaned).strip()
        if cleaned:
            titles.append(cleaned)

    # Guard: must return 6–14 titles; truncate or pad if model misbehaves
    titles = titles[:14]
    if len(titles) < 6:
        titles += [f"Section {i}" for i in range(len(titles) + 1, 7)]

    return titles


# ── Step 4a: draft one section ────────────────────────────────────────────────

def draft_section(
    section_title: str,
    sections_list: list[str],
    prior_approved_bodies: list[str],
    doc_type: str,
    doc_subtype: str,
    intake: CaseIntake,
    model: str = HAIKU,
) -> str:
    """Haiku call — draft a single section body.

    Args:
        section_title: Title of the section to draft.
        sections_list: Full ordered list of all section titles (for context).
        prior_approved_bodies: Bodies of already-approved sections (gives continuity).
        doc_type: "policy" | "sop"
        doc_subtype: e.g. "whistleblower_policy"
        intake: CaseIntake for client/jurisdiction context.
        model: Defaults to HAIKU; can be overridden to SONNET.
    """
    # Truncate prior context to keep prompt lean
    prior_context = "\n\n".join(prior_approved_bodies)
    if len(prior_context) > 1500:
        prior_context = prior_context[-1500:]

    sections_outline = "\n".join(f"- {t}" for t in sections_list)

    user = f"""You are drafting one section of a {doc_type} document.

DOCUMENT: {doc_subtype.replace('_', ' ').title()}
CLIENT: {intake.client_name}
JURISDICTION: {intake.primary_jurisdiction}

FULL DOCUMENT OUTLINE:
{sections_outline}

SECTIONS ALREADY DRAFTED (for continuity):
{prior_context or "None yet — this is the first section."}

NOW DRAFT THIS SECTION:
{section_title}

Write the section body only — do not repeat the section title as a heading.
Use Markdown formatting (bullet points, numbered steps where appropriate).
Be specific, professional, and jurisdiction-aware.
Aim for 150–400 words."""

    resp = _client().messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": user}],
    )
    return resp.content[0].text.strip()


# ── Step 4b: revise one section with instructions ─────────────────────────────

def revise_section(
    section_title: str,
    current_body: str,
    instructions: str,
    doc_type: str,
    doc_subtype: str,
    intake: CaseIntake,
    model: str = HAIKU,
) -> str:
    """Haiku call — revise a section body based on Maher's instructions.

    Instructions are HTML-stripped and capped at 500 chars before injection.
    """
    # Security: sanitize free-text instructions before model injection
    safe_instructions = _strip_html(instructions)[:500]

    user = f"""You are revising one section of a {doc_type} document based on consultant feedback.

DOCUMENT: {doc_subtype.replace('_', ' ').title()}
CLIENT: {intake.client_name}
JURISDICTION: {intake.primary_jurisdiction}

SECTION TITLE: {section_title}

CURRENT DRAFT:
{current_body}

REVISION INSTRUCTIONS:
{safe_instructions}

Rewrite the section body incorporating the instructions.
Return the revised section body only — no heading, no preamble."""

    resp = _client().messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": user}],
    )
    return resp.content[0].text.strip()


# ── Step 5: assemble and write final report ────────────────────────────────────

def assemble_and_write(
    co_build_state: CoBuildState,
    intake: CaseIntake,
    registry=None,
    hook_engine=None,
) -> FinalDeliverable:
    """Assemble all approved section bodies into a final report and write to disk.

    Fires one summary audit event with section count and action breakdown.
    Does not make any model API calls — pure assembly.
    """
    doc_subtype = co_build_state.doc_subtype
    doc_type = co_build_state.doc_type

    # Build Markdown document
    header = (
        f"# {doc_subtype.replace('_', ' ').title()}\n"
        f"**Client:** {intake.client_name}  \n"
        f"**Jurisdiction:** {intake.primary_jurisdiction}  \n"
        f"**Date:** {datetime.now(timezone.utc).strftime('%d %B %Y')}  \n"
        f"\n---\n\n"
    )

    sections_md = ""
    for i, section in enumerate(co_build_state.sections, start=1):
        sections_md += f"## {i}. {section.section_title}\n\n"
        sections_md += section.body.strip() + "\n\n"

    content = header + sections_md.strip()

    report_path = write_final_report(intake.case_id, content, "en", workflow="policy_sop")

    # Summarise what actions Maher took across all sections
    action_counts: dict[str, int] = {"approved": 0, "edited": 0, "regenerated": 0}
    for s in co_build_state.sections:
        if s.status in action_counts:
            action_counts[s.status] += 1

    append_audit_event(intake.case_id, {
        "event": "cobuild_complete",
        "agent": "policy_sop_cobuild",
        "workflow": "policy_sop",
        "doc_subtype": doc_subtype,
        "section_count": len(co_build_state.sections),
        "actions": action_counts,
        "status": "ok",
    })

    write_artifact(intake.case_id, "policy_sop_cobuild", "deliverable", {
        "case_id": intake.case_id,
        "workflow": "policy_sop",
        "doc_type": doc_type,
        "doc_subtype": doc_subtype,
        "gap_analysis": co_build_state.gap_analysis,
        "section_count": len(co_build_state.sections),
        "actions": action_counts,
        "report_path": str(report_path),
        "delivery_date": datetime.now(timezone.utc).isoformat(),
    })

    return FinalDeliverable(
        case_id=intake.case_id,
        workflow="policy_sop",
        approved_by="consultant",
        language=intake.language,
        content_en=content,
        citations=[],
        revision_history=[0],
        delivery_date=datetime.now(timezone.utc),
    )


# ── Step 5 (gap analysis): identify gaps in existing document ──────────────────

def identify_gaps(
    intake: CaseIntake,
    params: dict,
    uploaded_doc_text: str,
    standard_sections: list[str],
) -> dict[str, str | None]:
    """Sonnet call — returns a mapping of section_title → existing text or None.

    Used in gap_analysis mode when Maher has uploaded an existing document.
    Sections with existing text are pre-populated in the co-build loop.

    Args:
        uploaded_doc_text: Full text of the uploaded existing document.
        standard_sections: The proposed section titles from propose_structure().

    Returns:
        dict mapping each section title to extracted existing text, or None if absent.
    """
    doc_subtype = params.get("doc_subtype", "")
    sections_list = "\n".join(f"- {t}" for t in standard_sections)

    # Truncate uploaded doc to keep prompt within context limits
    doc_excerpt = uploaded_doc_text[:6000] if len(uploaded_doc_text) > 6000 else uploaded_doc_text

    user = f"""You are analyzing an existing {doc_subtype.replace('_', ' ')} document to identify which sections are already present.

REQUIRED SECTIONS FOR THE NEW DOCUMENT:
{sections_list}

EXISTING DOCUMENT TEXT:
{doc_excerpt}

For each required section, extract the relevant existing text if it is present in the document.
If a section is NOT present or has only minimal coverage, return null for that section.

Respond with a JSON object where:
- Keys are the exact section titles from the list above
- Values are either the extracted existing text (string) or null

Return ONLY valid JSON. No preamble or explanation."""

    resp = _client().messages.create(
        model=SONNET,
        max_tokens=4096,
        messages=[{"role": "user", "content": user}],
    )
    raw = resp.content[0].text.strip()

    # Parse JSON; on failure return all-None (safe fallback — treat as new document)
    try:
        import json
        # Strip markdown code fences if model added them
        if raw.startswith("```"):
            raw = re.sub(r"```[a-z]*\n?", "", raw).strip().rstrip("```").strip()
        result = json.loads(raw)
        # Ensure all keys from standard_sections are present
        return {title: result.get(title) for title in standard_sections}
    except Exception:
        return {title: None for title in standard_sections}
