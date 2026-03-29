"""FRM Risk Register workflow — multi-module pipeline.

Modules:
  1. Entity & Ownership Risk
  2. Financial Crime / AML Risk       ← Module 2 required by 3, 4, 7
  3. Procurement & Vendor Risk        ← requires Module 2
  4. HR & Payroll Risk                ← requires Module 2
  5. Revenue & Receivables Risk
  6. Fixed Assets & Capex Risk
  7. Management Override & Governance ← requires Module 2, 3
  8. Regulatory & Compliance Risk

Per module pipeline: Consultant Draft → PM Review → Partner Approval
Module 2: approve/flag/rewrite loop per RiskItem.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Callable, Optional

from rich.console import Console
from rich.prompt import Prompt

from config import get_model
from core.hook_engine import HookEngine
from core.orchestrator import Orchestrator, PipelineError, RevisionLimitError
from core.tool_registry import ToolRegistry
from schemas.artifacts import FRMDeliverable, FRMModuleOutput, RiskItem
from schemas.case import CaseIntake
from schemas.plugins import AgentHandoff
from tools.document_manager import DocumentManager
from tools.file_tools import case_dir, write_final_report


FRM_MODULES: dict[int, str] = {
    1: "Entity & Ownership Risk",
    2: "Financial Crime / AML Risk",
    3: "Procurement & Vendor Risk",
    4: "HR & Payroll Risk",
    5: "Revenue & Receivables Risk",
    6: "Fixed Assets & Capex Risk",
    7: "Management Override & Governance Risk",
    8: "Regulatory & Compliance Risk",
}

MODULE_DEPENDENCIES: dict[int, list[int]] = {
    3: [2],
    4: [2],
    7: [2, 3],
}


def run_frm_workflow(
    intake: CaseIntake,
    selected_modules: list[int],
    registry: ToolRegistry,
    hook_engine: HookEngine,
    document_manager: Optional[DocumentManager] = None,
    console: Optional[Console] = None,
    on_progress: Optional[Callable[[str], None]] = None,
) -> FRMDeliverable:
    """Run the FRM risk register pipeline for selected modules.

    Returns FRMDeliverable with complete risk register.
    """
    if console is None:
        console = Console()
    if on_progress is None:
        on_progress = lambda msg: console.print(f"  [cyan]{msg}[/cyan]")

    # Validate module dependencies
    _validate_module_order(selected_modules)

    from agents.junior_analyst.agent import JuniorAnalyst
    from agents.project_manager.agent import ProjectManager
    from agents.partner.agent import Partner

    junior  = JuniorAnalyst(registry, hook_engine, document_manager, "frm_risk_register")
    pm      = ProjectManager(registry, hook_engine, document_manager, "frm_risk_register")
    partner = Partner(registry, hook_engine, document_manager, "frm_risk_register")

    all_risk_items: list[RiskItem] = []
    all_citations = []
    completed_modules: list[int] = []
    prior_research: dict = {}  # shared across modules — no re-research

    for module_num in selected_modules:
        module_name = FRM_MODULES.get(module_num, f"Module {module_num}")
        on_progress(f"[Module {module_num}/{len(selected_modules)}] {module_name}...")

        context = {
            "case_id": intake.case_id,
            "workflow": "frm_risk_register",
            "frm_module": module_num,
            "frm_module_name": module_name,
            "prior_research": prior_research,
            "artifact_type": f"frm_m{module_num}_junior_output",
            "role": "junior",
            "schema_cls": None,  # FRM uses loose validation
            "intake": intake.model_dump(),
            "generate_arabic": intake.language == "ar",
            "client_name": intake.client_name,
        }

        # Build module-specific intake description
        module_intake = intake.model_copy(update={
            "description": (
                f"FRM Module {module_num}: {module_name}. "
                f"Original scope: {intake.description}. "
                f"Prior modules completed: {completed_modules}. "
                + (_prior_research_summary(prior_research) if prior_research else "")
            ),
            "workflow": "frm_risk_register",
        })

        # Run pipeline for this module
        try:
            on_progress(f"  Consultant drafting Module {module_num}...")  # "Consultant" = internal agent role
            junior_output = junior(module_intake.model_dump(), {
                **context,
                "role": "junior",
            })

            on_progress(f"  PM reviewing Module {module_num}...")
            pm_output = pm(junior_output["output"], {
                **context,
                "role": "pm",
            })

            # Handle PM revision request
            if pm_output["revision_requested"]:
                on_progress(f"  Revision requested — redrafting Module {module_num}...")
                revised_context = {
                    **context,
                    "revision_feedback": pm_output.get("revision_reason", ""),
                    "pm_feedback": pm_output.get("revision_reason", ""),
                }
                junior_output = junior(module_intake.model_dump(), revised_context)
                pm_output = pm(junior_output["output"], {**context, "role": "pm"})

            on_progress(f"  Partner reviewing Module {module_num}...")
            partner_output = partner(pm_output["output"], {
                **context,
                "role": "partner",
                "junior_output": junior_output["output"],
            })

            # Extract risk items for module 2 — run approve/flag/rewrite loop
            module_risks = _extract_risk_items(junior_output["output"], module_num, module_name)

            if module_num == 2 and console:
                module_risks = _frm_approve_flag_rewrite_loop(
                    console, module_risks, junior, module_intake, context
                )

            all_risk_items.extend(module_risks)
            all_citations.extend(junior_output["output"].get("citations", []))
            completed_modules.append(module_num)

            # Update prior_research for next module
            prior_research[module_name] = {
                "summary": junior_output["output"].get("summary", ""),
                "key_findings": [
                    r.get("title", "") for r in junior_output["output"].get("findings", [])
                ][:5],
            }

        except (PipelineError, RevisionLimitError) as e:
            console.print(f"  [red]Module {module_num} failed: {e}[/red]")
            on_progress(f"  Skipping Module {module_num} due to error.")
            continue

    # Generate executive summary
    on_progress("Generating executive summary...")
    exec_summary = _generate_executive_summary(intake, all_risk_items, completed_modules, registry)

    # Build deliverable
    content_en = _render_risk_register(intake, all_risk_items, exec_summary, completed_modules)

    deliverable = FRMDeliverable(
        case_id=intake.case_id,
        modules_completed=completed_modules,
        risk_register=all_risk_items,
        executive_summary=exec_summary,
        content_en=content_en,
        citations=all_citations,
        delivery_date=datetime.now(timezone.utc),
    )

    # Write final report
    report_path = write_final_report(intake.case_id, content_en, "en")
    on_progress(f"FRM Risk Register saved → {report_path}")

    return deliverable


# ── Approve / Flag / Rewrite loop (Module 2) ─────────────────────────────────

def _frm_approve_flag_rewrite_loop(
    console: Console,
    risk_items: list[RiskItem],
    junior: "JuniorAnalyst",
    intake: CaseIntake,
    context: dict,
) -> list[RiskItem]:
    """Interactive: consultant approves, flags, or requests rewrite per RiskItem."""
    if not risk_items:
        return risk_items

    console.print("\n[bold cyan]Module 2 Risk Item Review[/bold cyan]")
    console.print("For each risk item: [A]pprove / [F]lag / [R]ewrite\n")

    reviewed: list[RiskItem] = []
    for i, risk in enumerate(risk_items):
        console.print(f"\n[bold]Risk {i+1}/{len(risk_items)}:[/bold] {risk.title}")
        console.print(f"  Category: {risk.category}")
        console.print(f"  Rating: {risk.risk_rating}/25 (L:{risk.likelihood} × I:{risk.impact})")
        console.print(f"  Description: {risk.description[:200]}")

        choice = Prompt.ask(
            "  Action",
            choices=["a", "f", "r", "A", "F", "R"],
            default="a",
        ).lower()

        if choice == "a":
            reviewed.append(risk)
        elif choice == "f":
            note = Prompt.ask("  Flag note (shown in report)")
            flagged = risk.model_copy(update={
                "title": f"[FLAGGED] {risk.title}",
                "description": f"{risk.description}\n\nCONSULTANT FLAG: {note}",
            })
            reviewed.append(flagged)
        elif choice == "r":
            instructions = Prompt.ask("  Rewrite instructions")
            # Single-turn rewrite via Consultant (Haiku)
            revised = _rewrite_risk_item(risk, instructions, intake, junior)
            reviewed.append(revised)

    return reviewed


def _rewrite_risk_item(
    risk: RiskItem,
    instructions: str,
    intake: CaseIntake,
    junior: "JuniorAnalyst",
) -> RiskItem:
    """Haiku single-turn: rewrite a single risk item per consultant instructions."""
    import anthropic
    from config import ANTHROPIC_API_KEY, HAIKU

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt = (
        f"Rewrite this FRM risk item per the following instructions.\n\n"
        f"ORIGINAL:\n{json.dumps(risk.model_dump(), indent=2, default=str)}\n\n"
        f"INSTRUCTIONS: {instructions}\n\n"
        "Return the rewritten risk item as a JSON object with the same keys. "
        "Keep risk_id unchanged."
    )
    resp = client.messages.create(
        model=HAIKU,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    import re
    match = re.search(r'\{.*\}', resp.content[0].text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            return RiskItem(**{**risk.model_dump(), **data})
        except Exception:
            pass
    return risk


# ── Helpers ───────────────────────────────────────────────────────────────────

def _validate_module_order(selected: list[int]) -> None:
    """Raise ValueError if module dependencies are not satisfied."""
    selected_set = set(selected)
    for module, deps in MODULE_DEPENDENCIES.items():
        if module in selected_set:
            missing = [d for d in deps if d not in selected_set]
            if missing:
                raise ValueError(
                    f"Module {module} requires Module(s) {missing} to be included first."
                )


def _prior_research_summary(prior_research: dict) -> str:
    if not prior_research:
        return ""
    summaries = []
    for module_name, data in prior_research.items():
        summaries.append(
            f"[{module_name}]: {data.get('summary', '')[:200]}"
        )
    return "PRIOR MODULE RESEARCH: " + " | ".join(summaries)


def _extract_risk_items(junior_output: dict, module_num: int, module_name: str) -> list[RiskItem]:
    """Parse risk items from Junior output. Creates RiskItems from findings."""
    findings = junior_output.get("findings", [])
    items: list[RiskItem] = []

    for i, finding in enumerate(findings):
        risk_level = finding.get("risk_level", "medium")
        likelihood = {"high": 4, "medium": 3, "low": 2, "critical": 5}.get(risk_level, 3)
        impact     = {"high": 4, "medium": 3, "low": 2, "critical": 5}.get(risk_level, 3)

        items.append(RiskItem(
            risk_id=f"M{module_num}-R{i+1:02d}",
            category=module_name,
            title=finding.get("title", f"Risk {i+1}"),
            description=finding.get("description", ""),
            red_flags=[],
            likelihood=likelihood,
            likelihood_rationale=f"Based on: {finding.get('evidence', '')}",
            impact=impact,
            impact_rationale=f"Risk level assessed as {risk_level}",
            risk_rating=likelihood * impact,
            existing_controls=[],
            control_gaps=[],
            recommendations=junior_output.get("recommendations", [])[:2],
            regulatory_references=junior_output.get("citations", [])[:2],
            framework_references=["COSO 2013", "ISO 37001:2016", "ACFE Fraud Prevention"],
        ))

    return items


def _generate_executive_summary(
    intake: CaseIntake,
    risk_items: list[RiskItem],
    completed_modules: list[int],
    registry: ToolRegistry,
) -> str:
    """Haiku single-turn: generate executive summary for FRM deliverable."""
    import anthropic
    from config import ANTHROPIC_API_KEY, HAIKU

    high_risks = [r for r in risk_items if r.risk_rating >= 16]
    medium_risks = [r for r in risk_items if 9 <= r.risk_rating < 16]

    prompt = (
        f"Write a 200-word executive summary for a Fraud Risk Management register.\n"
        f"Client: {intake.client_name}, Industry: {intake.industry}\n"
        f"Modules assessed: {[FRM_MODULES.get(m, m) for m in completed_modules]}\n"
        f"Total risks identified: {len(risk_items)} "
        f"(High: {len(high_risks)}, Medium: {len(medium_risks)}, "
        f"Low: {len(risk_items) - len(high_risks) - len(medium_risks)})\n"
        f"Top risks: {[r.title for r in sorted(risk_items, key=lambda x: -x.risk_rating)[:3]]}\n\n"
        "Write professionally, referencing COSO and ISO 37001 frameworks."
    )

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        resp = client.messages.create(
            model=HAIKU,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text.strip()
    except Exception:
        return (
            f"This Fraud Risk Management Register covers {len(completed_modules)} modules "
            f"for {intake.client_name} ({intake.industry}). "
            f"A total of {len(risk_items)} risks were identified."
        )


def _render_risk_register(
    intake: CaseIntake,
    risk_items: list[RiskItem],
    exec_summary: str,
    completed_modules: list[int],
) -> str:
    """Render FRM risk register as Markdown."""
    now = datetime.now(timezone.utc).strftime("%d %B %Y")
    lines = [
        f"# Fraud Risk Management Register",
        f"**Client:** {intake.client_name}",
        f"**Industry:** {intake.industry}",
        f"**Jurisdiction:** {intake.primary_jurisdiction}",
        f"**Date:** {now}",
        f"**Prepared by:** GoodWork Forensic Consulting",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        exec_summary,
        "",
        "---",
        "",
        f"## Risk Register ({len(risk_items)} risks across {len(completed_modules)} modules)",
        "",
        "| Risk ID | Category | Title | L | I | Rating | Owner |",
        "|---------|----------|-------|---|---|--------|-------|",
    ]

    for r in sorted(risk_items, key=lambda x: -x.risk_rating):
        rating_label = "HIGH" if r.risk_rating >= 16 else ("MEDIUM" if r.risk_rating >= 9 else "LOW")
        lines.append(
            f"| {r.risk_id} | {r.category} | {r.title} | "
            f"{r.likelihood} | {r.impact} | **{r.risk_rating}** ({rating_label}) | {r.risk_owner or 'TBD'} |"
        )

    lines += ["", "---", "", "## Detailed Risk Descriptions", ""]

    for r in sorted(risk_items, key=lambda x: -x.risk_rating):
        lines += [
            f"### {r.risk_id}: {r.title}",
            f"**Category:** {r.category}",
            f"**Risk Rating:** {r.risk_rating}/25 (Likelihood: {r.likelihood}, Impact: {r.impact})",
            f"**Risk Owner:** {r.risk_owner or 'TBD'}",
            "",
            f"**Description:** {r.description}",
            "",
        ]
        if r.existing_controls:
            lines.append("**Existing Controls:**")
            lines += [f"- {c}" for c in r.existing_controls]
            lines.append("")
        if r.control_gaps:
            lines.append("**Control Gaps:**")
            lines += [f"- {g}" for g in r.control_gaps]
            lines.append("")
        if r.recommendations:
            lines.append("**Recommendations:**")
            lines += [f"- {rec}" for rec in r.recommendations]
            lines.append("")
        if r.regulatory_references:
            lines.append("**Regulatory References:**")
            for cite in r.regulatory_references:
                if hasattr(cite, "source_name"):
                    lines.append(f"- {cite.source_name}: {cite.source_url}")
                elif isinstance(cite, dict):
                    lines.append(f"- {cite.get('source_name', '')}: {cite.get('source_url', '')}")
            lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)
