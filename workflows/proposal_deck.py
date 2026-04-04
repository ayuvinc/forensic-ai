"""Proposal deck workflow — DeckStoryboard + per-slide prompt pack."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from rich.console import Console
from rich.prompt import Prompt

from config import ANTHROPIC_API_KEY, SONNET
from schemas.case import CaseIntake
from schemas.presentation import DeckMasterPrompt, DeckStoryboard, SlideSpec
from tools.file_tools import append_audit_event, case_dir


AUDIENCES = {
    "1": "CFO",
    "2": "CEO / Board",
    "3": "Legal Counsel",
    "4": "Audit Committee",
    "5": "UAE Regulator",
    "6": "Insurance Adjuster",
}


def run_proposal_deck_workflow(
    intake: CaseIntake,
    registry=None,
    hook_engine=None,
    console: Optional[Console] = None,
    on_progress: Optional[Callable[[str], None]] = None,
) -> DeckStoryboard:
    """Generate DeckStoryboard, master prompt, and per-slide prompts."""
    if console is None:
        console = Console()
    if on_progress is None:
        on_progress = lambda msg: console.print(f"  [cyan]{msg}[/cyan]")

    console.print("\n  [bold]Proposal deck configuration[/bold]")
    aud_keys = list(AUDIENCES.keys())
    for k, v in AUDIENCES.items():
        console.print(f"    {k}. {v}")
    aud_choice = Prompt.ask("  Primary audience", choices=aud_keys, default="1")
    audience = AUDIENCES[aud_choice]

    deck_objective = Prompt.ask(
        "  Deck objective (what decision should this drive?)",
        default=f"Engage {intake.client_name} for {intake.workflow.replace('_', ' ')} services",
    )
    decision_required = Prompt.ask(
        "  Decision required from audience",
        default="Approve engagement and sign service agreement",
    )
    slide_count = int(Prompt.ask("  Approximate slide count", default="12"))

    on_progress("Generating storyboard...")
    storyboard = _generate_storyboard(
        intake, audience, deck_objective, decision_required, slide_count
    )

    # Persist storyboard
    cdir = case_dir(intake.case_id)
    sb_path = cdir / "deck_storyboard.v1.json"
    _atomic_write(sb_path, storyboard.model_dump_json(indent=2))
    on_progress(f"Storyboard saved → {sb_path}")

    # Generate master prompt
    on_progress("Generating master prompt...")
    master = _generate_master_prompt(intake, storyboard, audience)
    mp_path = cdir / "deck_master_prompt.v1.md"
    _atomic_write(mp_path, _render_master_prompt(master))
    on_progress(f"Master prompt saved → {mp_path}")

    # Generate per-slide prompts
    on_progress(f"Generating {len(storyboard.slides)} slide prompts...")
    for spec in storyboard.slides:
        slide_prompt = _generate_slide_prompt(spec, storyboard, intake)
        prompt_path = cdir / f"slide_{spec.slide_number:02d}_prompt.md"
        _atomic_write(prompt_path, slide_prompt)

    on_progress(f"Slide prompts saved to {cdir}/")
    append_audit_event(intake.case_id, {
        "event": "deliverable_generated",
        "agent": "proposal_deck",
        "workflow": "proposal_deck",
        "slides_written": len(storyboard.slides),
        "status": "ok",
    })
    return storyboard


def _generate_storyboard(
    intake: CaseIntake,
    audience: str,
    deck_objective: str,
    decision_required: str,
    slide_count: int,
) -> DeckStoryboard:
    """Sonnet single-turn: generate full DeckStoryboard."""
    import anthropic

    prompt = f"""You are a forensic consulting partner creating a presentation storyboard.

CLIENT: {intake.client_name}
INDUSTRY: {intake.industry}
JURISDICTION: {intake.primary_jurisdiction}
WORKFLOW: {intake.workflow.replace('_', ' ').title()}
SCOPE: {intake.description}
AUDIENCE: {audience}
OBJECTIVE: {deck_objective}
DECISION REQUIRED: {decision_required}
SLIDES: approximately {slide_count}

Generate a JSON DeckStoryboard with this exact structure:
{{
  "case_id": "{intake.case_id}",
  "deck_objective": "...",
  "audience": "{audience}",
  "decision_required": "...",
  "key_messages": ["message 1", "message 2", "message 3"],
  "slides": [
    {{
      "slide_number": 1,
      "title": "...",
      "purpose": "...",
      "key_message": "...",
      "content_bullets": ["bullet 1", "bullet 2"],
      "evidence_needed": ["evidence item 1"],
      "suggested_visual": "description of visual",
      "speaker_notes": "talking points for presenter",
      "risks_or_gaps": ["potential weakness"]
    }}
  ],
  "open_questions": ["question 1"]
}}

Include standard forensic proposal slides: firm intro, scope summary, methodology, team, timeline, fees.
Tailor to {audience} concerns. Return ONLY valid JSON.
"""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=SONNET,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    import re
    match = re.search(r'\{.*\}', resp.content[0].text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            slides = [SlideSpec(**s) for s in data.get("slides", [])]
            return DeckStoryboard(
                case_id=intake.case_id,
                deck_objective=data.get("deck_objective", deck_objective),
                audience=audience,
                decision_required=data.get("decision_required", decision_required),
                key_messages=data.get("key_messages", []),
                slides=slides,
                open_questions=data.get("open_questions", []),
            )
        except Exception:
            pass

    # Fallback minimal storyboard
    return DeckStoryboard(
        case_id=intake.case_id,
        deck_objective=deck_objective,
        audience=audience,
        decision_required=decision_required,
        key_messages=[],
        slides=[],
        open_questions=["Storyboard generation failed — regenerate manually"],
    )


def _generate_master_prompt(
    intake: CaseIntake,
    storyboard: DeckStoryboard,
    audience: str,
) -> DeckMasterPrompt:
    return DeckMasterPrompt(
        case_id=intake.case_id,
        audience=audience,
        target_tool="claude_ppt",
        system_prompt=(
            f"You are building a professional forensic consulting presentation for {audience}. "
            f"The firm is GoodWork Forensic Consulting. "
            f"Client: {intake.client_name}. "
            "Use professional, evidence-based language. Avoid jargon. "
            "Each slide should have a clear single message."
        ),
        user_prompt=(
            f"Create a {len(storyboard.slides)}-slide presentation following the storyboard below. "
            f"Objective: {storyboard.deck_objective}. "
            f"Decision needed: {storyboard.decision_required}."
        ),
        step_prompts=[
            f"Slide {s.slide_number}: {s.title} — {s.key_message}"
            for s in storyboard.slides
        ],
        attachment_guidance=(
            "Attach: firm profile, relevant case studies, team CVs, "
            "regulatory reference documents."
        ),
        usage_notes=(
            "Use this master prompt with Claude Projects or Claude API. "
            "Reference individual slide prompts (slide_NN_prompt.md) for detailed instructions."
        ),
    )


def _render_master_prompt(master: DeckMasterPrompt) -> str:
    lines = [
        "# Deck Master Prompt",
        f"**Case:** {master.case_id}",
        f"**Audience:** {master.audience}",
        f"**Target tool:** {master.target_tool}",
        "",
        "## System Prompt",
        "",
        master.system_prompt,
        "",
        "## User Prompt",
        "",
        master.user_prompt,
        "",
        "## Step-by-Step Slide Prompts",
        "",
    ]
    for i, sp in enumerate(master.step_prompts, 1):
        lines.append(f"{i}. {sp}")
    lines += [
        "",
        "## Attachment Guidance",
        "",
        master.attachment_guidance,
        "",
        "## Usage Notes",
        "",
        master.usage_notes,
    ]
    return "\n".join(lines)


def _generate_slide_prompt(
    spec: SlideSpec,
    storyboard: DeckStoryboard,
    intake: CaseIntake,
) -> str:
    lines = [
        f"# Slide {spec.slide_number}: {spec.title}",
        "",
        f"**Purpose:** {spec.purpose}",
        f"**Key message:** {spec.key_message}",
        f"**Audience:** {storyboard.audience}",
        "",
        "## Content",
        "",
    ]
    for bullet in spec.content_bullets:
        lines.append(f"- {bullet}")
    if spec.evidence_needed:
        lines += ["", "## Evidence Required", ""]
        for e in spec.evidence_needed:
            lines.append(f"- {e}")
    if spec.suggested_visual:
        lines += ["", f"## Visual Suggestion", "", spec.suggested_visual]
    if spec.speaker_notes:
        lines += ["", "## Speaker Notes", "", spec.speaker_notes]
    if spec.risks_or_gaps:
        lines += ["", "## Risks / Gaps to Address", ""]
        for r in spec.risks_or_gaps:
            lines.append(f"- {r}")
    return "\n".join(lines)


def _atomic_write(path: Path, content: str) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)
