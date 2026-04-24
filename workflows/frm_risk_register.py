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
from typing import Callable, Optional, List

from rich.console import Console
from rich.prompt import Prompt

from config import get_model
from core.hook_engine import HookEngine, HookVetoError
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


def run_frm_pipeline(
    intake: CaseIntake,
    selected_modules: list[int],
    registry: ToolRegistry,
    hook_engine: HookEngine,
    document_manager: Optional[DocumentManager] = None,
    on_progress: Optional[Callable[[str], None]] = None,
) -> tuple[list[RiskItem], list, list[int], str]:
    """Run Junior→PM→Partner for each selected module.

    Returns (risk_items, citations, completed_modules, exec_summary).

    Does NOT call _frm_approve_flag_rewrite_loop — the caller decides when and
    how to present items for review (CLI: inline after Module 2; Streamlit: card
    UI for all items after pipeline completes).

    Does NOT write the final report — call run_frm_finalize() with the reviewed
    items to produce the deliverable.
    """
    if on_progress is None:
        on_progress = lambda msg: None  # no-op default; caller provides real callback

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

    # Use a fallback console for error printing only (not progress — that goes via on_progress)
    from rich.console import Console as _Console
    _err_console = _Console()

    total_modules = len(selected_modules)
    for module_idx, module_num in enumerate(selected_modules, start=1):
        module_name = FRM_MODULES.get(module_num, f"Module {module_num}")
        on_progress(f"[Module {module_idx}/{total_modules}] {module_name}...")

        # FR-02: inject stakeholder context when engagement_id is set
        stakeholder_context = ""
        if getattr(intake, "engagement_id", None):
            try:
                from tools.project_manager import ProjectManager as _PM
                stakeholder_context = _PM().get_stakeholder_context(intake.engagement_id)
            except Exception:
                pass

        # FR-06: recommendation_depth from intake drives how detailed recommendations are
        rec_depth = getattr(intake, "recommendation_depth", None) or "structured"
        _DEPTH_INSTRUCTIONS = {
            "structured":  "Recommendations must align with COSO/ACFE/ISO 37001 framework references. Each recommendation should cite the relevant control objective.",
            "executive":   "Recommendations should be high-level (2–3 sentences max each). Avoid technical implementation detail — focus on strategic action and accountability.",
            "detailed":    "Recommendations must include step-by-step implementation guidance, responsible parties, estimated timeline, and success metrics where applicable.",
        }
        depth_instruction = _DEPTH_INSTRUCTIONS.get(rec_depth, _DEPTH_INSTRUCTIONS["structured"])

        context = {
            "case_id": intake.case_id,
            "workflow": "frm_risk_register",
            "frm_module": module_num,
            "frm_module_name": module_name,
            "prior_research": prior_research,
            "artifact_type": f"frm_m{module_num}_junior_output",
            "role": "junior",
            "schema_cls": None,
            "intake": intake.model_dump(),
            "generate_arabic": intake.language == "ar",
            "client_name": intake.client_name,
            "recommendation_depth": rec_depth,                  # FR-06
            "recommendation_instruction": depth_instruction,   # FR-06: injected into prompt
            "stakeholder_context": stakeholder_context,        # FR-02
        }

        module_intake = intake.model_copy(update={
            "description": (
                f"FRM Module {module_num}: {module_name}. "
                f"Original scope: {intake.description}. "
                f"Prior modules completed: {completed_modules}. "
                + (_prior_research_summary(prior_research) if prior_research else "")
            ),
            "workflow": "frm_risk_register",
        })

        try:
            on_progress(f"  Consultant drafting Module {module_num}...")
            try:
                junior_output = junior(module_intake.model_dump(), {**context, "role": "junior"})
            except HookVetoError as _schema_err:
                # validate_schema blocked the draft (e.g. empty findings). Retry once with error injected.
                on_progress(f"  Schema validation failed — retrying Module {module_num}...")
                try:
                    junior_output = junior(module_intake.model_dump(), {
                        **context,
                        "role": "junior",
                        "schema_retry": True,
                        "schema_error": str(_schema_err),
                    })
                except HookVetoError:
                    on_progress(f"  Skipping Module {module_num} — could not generate findings after retry.")
                    continue

            on_progress(f"  PM reviewing Module {module_num}...")
            pm_output = pm(junior_output["output"], {**context, "role": "pm"})

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
            partner(pm_output["output"], {
                **context,
                "role": "partner",
                "junior_output": junior_output["output"],
            })

            module_risks = _extract_risk_items(junior_output["output"], module_num, module_name)
            all_risk_items.extend(module_risks)
            all_citations.extend(junior_output["output"].get("citations", []))
            completed_modules.append(module_num)

            prior_research[module_name] = {
                "summary": junior_output["output"].get("summary", ""),
                "key_findings": [
                    r.get("title", "") for r in junior_output["output"].get("findings", [])
                ][:5],
            }

        except (PipelineError, RevisionLimitError) as e:
            _err_console.print(f"  [red]Module {module_num} failed: {e}[/red]")
            on_progress(f"  Skipping Module {module_num} due to error.")
            continue

    on_progress("Generating executive summary...")
    exec_summary = _generate_executive_summary(intake, all_risk_items, completed_modules, registry)

    return all_risk_items, all_citations, completed_modules, exec_summary


def run_frm_finalize(
    intake: CaseIntake,
    risk_items: list[RiskItem],
    citations: list,
    completed_modules: list[int],
    exec_summary: str,
    context: Optional[dict] = None,
) -> FRMDeliverable:
    """Assemble deliverable from reviewed items and write the final report.

    Called after the review loop (CLI: inline; Streamlit: card UI).
    Writes final_report.en.md and final_report.en.docx, advances state to DELIVERABLE_WRITTEN.

    RD-06: builds section_overrides (Risk Register Table + summary sections) for BaseReportBuilder.
    P9-08d: runs AI review pass if context["ai_review_enabled"] is True (default).
    """
    from tools.file_tools import mark_deliverable_written

    _context = context or {}

    content_en = _render_risk_register(intake, risk_items, exec_summary, completed_modules)

    # P9-08d: AI review pass after pipeline, before report write
    if _context.get("ai_review_enabled", True):
        try:
            from agents.reviewer.review_agent import ReviewAgent
            reviewer = ReviewAgent()
            # Build a pseudo-draft dict from risk_items for the reviewer
            draft_for_review = {
                "findings": [
                    {
                        "title": r.risk_id,
                        "description": r.description,
                        "citations": [c.model_dump() if hasattr(c, "model_dump") else c
                                      for c in (r.regulatory_references or [])],
                    }
                    for r in risk_items
                ]
            }
            reviewer(draft_for_review, {
                **_context,
                "case_id": intake.case_id,
                "workflow": "frm_risk_register",
            })
        except Exception:
            pass

    # RD-06: build section_overrides for structured .docx via BaseReportBuilder
    section_overrides = _build_frm_section_overrides(intake, risk_items, exec_summary, completed_modules)

    deliverable = FRMDeliverable(
        case_id=intake.case_id,
        modules_completed=completed_modules,
        risk_register=[r.model_dump() if hasattr(r, "model_dump") else r for r in risk_items],
        executive_summary=exec_summary,
        content_en=content_en,
        citations=citations,
        delivery_date=datetime.now(timezone.utc),
    )

    write_final_report(
        intake.case_id, content_en, "en",
        workflow="frm_risk_register",
        section_overrides=section_overrides,
    )
    mark_deliverable_written(intake.case_id, "frm_risk_register")

    return deliverable


def run_frm_workflow(
    intake: CaseIntake,
    selected_modules: list[int],
    registry: ToolRegistry,
    hook_engine: HookEngine,
    document_manager: Optional[DocumentManager] = None,
    console: Optional[Console] = None,
    on_progress: Optional[Callable[[str], None]] = None,
) -> FRMDeliverable:
    """CLI entry point — pipeline + Module 2 inline review + finalize.

    Signature unchanged. run.py calls this; behaviour is identical to pre-split.
    Streamlit pages call run_frm_pipeline() + run_frm_finalize() directly.
    """
    if console is None:
        console = Console()
    if on_progress is None:
        on_progress = lambda msg: console.print(f"  [cyan]{msg}[/cyan]")

    _validate_module_order(selected_modules)

    risk_items, citations, completed_modules, exec_summary = run_frm_pipeline(
        intake, selected_modules, registry, hook_engine, document_manager, on_progress
    )

    # CLI-only: interactive review loop for Module 2 items
    # (Streamlit applies review to all modules via card UI — see pages/6_FRM.py)
    if 2 in completed_modules:
        from agents.junior_analyst.agent import JuniorAnalyst
        junior = JuniorAnalyst(registry, hook_engine, document_manager, "frm_risk_register")
        module_intake = intake.model_copy(update={"workflow": "frm_risk_register"})
        context = {
            "case_id": intake.case_id,
            "workflow": "frm_risk_register",
            "frm_module": 2,
            "frm_module_name": FRM_MODULES[2],
        }
        m2_items = [r for r in risk_items if r.risk_id.startswith("M2-")]
        other_items = [r for r in risk_items if not r.risk_id.startswith("M2-")]
        reviewed_m2 = _frm_approve_flag_rewrite_loop(console, m2_items, junior, module_intake, context)
        risk_items = reviewed_m2 + other_items

    return run_frm_finalize(intake, risk_items, citations, completed_modules, exec_summary)


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


def _build_frm_section_overrides(
    intake: CaseIntake,
    risk_items: list[RiskItem],
    exec_summary: str,
    completed_modules: list[int],
) -> dict:
    """Build section_overrides dict for BaseReportBuilder .docx output (RD-06)."""
    now = datetime.now(timezone.utc).strftime("%d %B %Y")

    # Risk Register table text
    table_rows = ["| Risk ID | Category | Title | L | I | Rating | Owner |",
                  "|---------|----------|-------|---|---|--------|-------|"]
    for r in sorted(risk_items, key=lambda x: -x.risk_rating):
        label = "HIGH" if r.risk_rating >= 16 else ("MEDIUM" if r.risk_rating >= 9 else "LOW")
        table_rows.append(
            f"| {r.risk_id} | {r.category} | {r.title} | "
            f"{r.likelihood} | {r.impact} | {r.risk_rating} ({label}) | {r.risk_owner or 'TBD'} |"
        )
    risk_table_text = "\n".join(table_rows)

    # Recommendations summary
    all_recs: list[str] = []
    for r in risk_items:
        all_recs.extend(r.recommendations or [])
    recs_text = "\n".join(f"- {rec}" for rec in all_recs[:20]) or "No recommendations recorded."

    return {
        "cover": {
            "title": "Fraud Risk Management Register",
            "subtitle": f"Client: {intake.client_name}",
            "metadata": {
                "Industry": intake.industry,
                "Jurisdiction": intake.primary_jurisdiction,
                "Modules Assessed": ", ".join(
                    FRM_MODULES.get(m, str(m)) for m in completed_modules
                ),
                "Total Risks": str(len(risk_items)),
                "Date": now,
                "Prepared by": "GoodWork Forensic Consulting",
                "Classification": "CONFIDENTIAL",
            },
        },
        "sections": [
            {"level": 1, "heading": "1. Executive Summary",
             "content": exec_summary},
            {"level": 1, "heading": "2. Risk Register Summary",
             "content": (
                 f"Total risks identified: {len(risk_items)}\n"
                 f"High (≥16/25): {sum(1 for r in risk_items if r.risk_rating >= 16)}\n"
                 f"Medium (9–15/25): {sum(1 for r in risk_items if 9 <= r.risk_rating < 16)}\n"
                 f"Low (<9/25): {sum(1 for r in risk_items if r.risk_rating < 9)}"
             )},
            {"level": 1, "heading": "3. Risk Register Table",
             "content": risk_table_text},
            {"level": 1, "heading": "4. Detailed Risk Descriptions",
             "content": "\n\n".join(
                 f"{r.risk_id}: {r.title}\nRating: {r.risk_rating}/25 "
                 f"(L:{r.likelihood} × I:{r.impact})\n{r.description}"
                 for r in sorted(risk_items, key=lambda x: -x.risk_rating)
             ) or "No detailed risks."},
            {"level": 1, "heading": "5. Recommendations Summary",
             "content": recs_text},
            {"level": 1, "heading": "6. Methodology & Framework",
             "content": (
                 "This assessment was conducted in accordance with COSO 2013, "
                 "ISO 37001:2016 (Anti-Bribery Management Systems), and ACFE "
                 "Fraud Prevention standards."
             )},
            {"level": 1, "heading": "7. Partner Sign-off",
             "content": f"Approved: {now}\nPrepared by: GoodWork Forensic Consulting\n\n"
                        "This register is confidential and intended solely for the "
                        "named client. It should not be reproduced without written consent."},
        ],
    }


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
