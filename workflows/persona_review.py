"""Persona review workflow — review deliverable from multiple persona perspectives."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from core.hook_engine import HookEngine
from core.tool_registry import ToolRegistry
from schemas.artifacts import PersonaReviewOutput
from schemas.case import CaseIntake
from tools.file_tools import case_dir, append_audit_event


AVAILABLE_PERSONAS = {
    "1": ("CFO", "cfo"),
    "2": ("Legal Counsel", "lawyer"),
    "3": ("UAE Regulator", "regulator"),
    "4": ("Insurance Adjuster", "insurance_adjuster"),
    "5": ("All personas", "all"),
}


def run_persona_review_workflow(
    intake: CaseIntake,
    registry: ToolRegistry,
    hook_engine: HookEngine,
    console: Optional[Console] = None,
    on_progress: Optional[Callable[[str], None]] = None,
) -> list[PersonaReviewOutput]:
    """Review a deliverable from selected persona perspectives."""
    if console is None:
        console = Console()
    if on_progress is None:
        on_progress = lambda msg: console.print(f"  [cyan]{msg}[/cyan]")

    # Get deliverable to review
    console.print("\n  [bold]Select deliverable to review[/bold]")
    cdir = case_dir(intake.case_id)
    reports = list(cdir.glob("final_report.*.md")) + list(cdir.glob("*.md"))

    if not reports:
        deliverable_text = Prompt.ask(
            "  No reports found in case folder. Paste report content (or path to file)"
        )
        if Path(deliverable_text).exists():
            deliverable_text = Path(deliverable_text).read_text(encoding="utf-8")
    else:
        console.print("  Available reports:")
        for i, r in enumerate(reports, 1):
            console.print(f"    {i}. {r.name}")
        choice = Prompt.ask("  Select report", default="1")
        try:
            deliverable_text = reports[int(choice) - 1].read_text(encoding="utf-8")
        except (IndexError, ValueError):
            console.print("[red]Invalid selection.[/red]")
            return []

    # Select personas
    console.print("\n  [bold]Select personas:[/bold]")
    for k, (label, _) in AVAILABLE_PERSONAS.items():
        console.print(f"    {k}. {label}")
    persona_choice = Prompt.ask("  Select persona(s)", default="5")

    selected_ids = []
    if persona_choice == "5":
        selected_ids = ["cfo", "lawyer", "regulator", "insurance_adjuster"]
    else:
        _, pid = AVAILABLE_PERSONAS.get(persona_choice, ("", "cfo"))
        selected_ids = [pid]

    # Run reviews
    results = []
    context = {
        "case_id": intake.case_id,
        "workflow": "persona_review",
        "intake": intake.model_dump(),
    }

    for persona_id in selected_ids:
        on_progress(f"Running {persona_id} review...")
        try:
            persona = _load_persona(persona_id, registry, hook_engine)
            result = persona.review(deliverable_text, context)
            results.append(result)
            _display_review(console, result)
        except Exception as e:
            console.print(f"  [red]{persona_id} review failed: {e}[/red]")

    # Save results
    if results:
        _save_reviews(intake.case_id, results)
        on_progress(f"Reviews saved to {cdir}/persona_reviews.json")

    return results


def _load_persona(persona_id: str, registry: ToolRegistry, hook_engine: HookEngine):
    """Load and instantiate a persona."""
    if persona_id == "cfo":
        from personas.cfo.persona import CFOPersona
        return CFOPersona(registry, hook_engine)
    elif persona_id == "lawyer":
        from personas.lawyer.persona import LawyerPersona
        return LawyerPersona(registry, hook_engine)
    elif persona_id == "regulator":
        from personas.regulator.persona import RegulatorPersona
        return RegulatorPersona(registry, hook_engine)
    elif persona_id == "insurance_adjuster":
        from personas.insurance_adjuster.persona import InsuranceAdjusterPersona
        return InsuranceAdjusterPersona(registry, hook_engine)
    raise ValueError(f"Unknown persona: {persona_id}")


def _display_review(console: Console, review: PersonaReviewOutput) -> None:
    verdict_color = {
        "pass": "green",
        "conditional_pass": "yellow",
        "fail": "red",
    }.get(review.overall_verdict, "white")

    lines = [
        f"[bold]{review.persona.upper()}[/bold] — [{verdict_color}]{review.overall_verdict.upper()}[/{verdict_color}]",
        f"Perspective: {review.perspective}",
    ]
    if review.objections:
        lines.append(f"\nObjections ({len(review.objections)}):")
        for obj in review.objections[:3]:
            lines.append(f"  • {obj}")
    if review.regulatory_gaps:
        lines.append(f"\nRegulatory gaps ({len(review.regulatory_gaps)}):")
        for gap in review.regulatory_gaps[:3]:
            lines.append(f"  • {gap}")
    lines.append(f"\nRecommendation: {review.recommendation}")

    console.print(Panel("\n".join(lines), border_style=verdict_color))


def _save_reviews(case_id: str, reviews: list[PersonaReviewOutput]) -> None:
    import os
    cdir = case_dir(case_id)
    path = cdir / "persona_reviews.json"
    tmp = path.with_suffix(".tmp")
    data = [r.model_dump() for r in reviews]
    tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, path)
    append_audit_event(case_id, {
        "event": "persona_reviews_completed",
        "personas": [r.persona for r in reviews],
        "verdicts": {r.persona: r.overall_verdict for r in reviews},
    })
