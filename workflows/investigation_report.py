"""Investigation report workflow.

7 investigation types × 4 audiences.
Auto timeline, auto transcript processing, Excel analysis, email parsing.
Evidence-led narrative: procedure → finding → implication → conclusion.
Expert witness standard auto-applied when audience = legal proceedings.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from rich.console import Console
from rich.prompt import Prompt

from core.hook_engine import HookEngine
from core.orchestrator import Orchestrator
from core.tool_registry import ToolRegistry
from schemas.artifacts import FinalDeliverable
from schemas.case import CaseIntake
from tools.document_manager import DocumentManager
from tools.file_tools import write_final_report, append_audit_event


INVESTIGATION_TYPES = {
    "1": "asset_misappropriation",
    "2": "financial_statement_fraud",
    "3": "corruption_bribery",
    "4": "cyber_fraud",
    "5": "procurement_fraud",
    "6": "revenue_leakage",
    "7": "compliance_investigation",
}

AUDIENCES = {
    "1": "management",
    "2": "board",
    "3": "legal_proceedings",
    "4": "regulatory_submission",
}

TYPE_LABELS = {
    "asset_misappropriation": "Asset Misappropriation",
    "financial_statement_fraud": "Financial Statement Fraud",
    "corruption_bribery": "Corruption & Bribery",
    "cyber_fraud": "Cyber Fraud / Digital Investigation",
    "procurement_fraud": "Procurement Fraud",
    "revenue_leakage": "Revenue Leakage",
    "compliance_investigation": "Compliance Investigation",
}


def run_investigation_workflow(
    intake: CaseIntake,
    registry: ToolRegistry,
    hook_engine: HookEngine,
    document_manager: Optional[DocumentManager] = None,
    console: Optional[Console] = None,
    on_progress: Optional[Callable[[str], None]] = None,
) -> FinalDeliverable:
    """Run full investigation report pipeline."""
    if console is None:
        console = Console()
    if on_progress is None:
        on_progress = lambda msg: console.print(f"  [cyan]{msg}[/cyan]")

    # Collect investigation-specific parameters
    console.print("\n  [bold]Investigation type:[/bold]")
    for k, v in INVESTIGATION_TYPES.items():
        label = TYPE_LABELS.get(v, v)
        console.print(f"    {k}. {label}")
    inv_choice = Prompt.ask("  Select type", choices=list(INVESTIGATION_TYPES.keys()), default="1")
    inv_type = INVESTIGATION_TYPES[inv_choice]

    console.print("\n  [bold]Report audience:[/bold]")
    for k, v in AUDIENCES.items():
        console.print(f"    {k}. {v.replace('_', ' ').title()}")
    aud_choice = Prompt.ask("  Select audience", choices=list(AUDIENCES.keys()), default="1")
    audience = AUDIENCES[aud_choice]

    expert_witness = audience == "legal_proceedings"
    if expert_witness:
        console.print("  [yellow]Expert witness standard will be applied (ACFE-compliant).[/yellow]")

    # Document processing
    if document_manager:
        _process_case_documents(document_manager, inv_type, console, on_progress)

    # Build enriched description
    enriched_description = (
        f"{intake.description}\n"
        f"Investigation type: {TYPE_LABELS.get(inv_type, inv_type)}\n"
        f"Audience: {audience.replace('_', ' ').title()}\n"
        f"Expert witness standard: {'Yes' if expert_witness else 'No'}"
    )
    enriched_intake = intake.model_copy(update={"description": enriched_description})

    from agents.junior_analyst.agent import JuniorAnalyst
    from agents.project_manager.agent import ProjectManager
    from agents.partner.agent import Partner

    junior  = JuniorAnalyst(registry, hook_engine, document_manager, "investigation_report")
    pm      = ProjectManager(registry, hook_engine, document_manager, "investigation_report")
    partner = Partner(registry, hook_engine, document_manager, "investigation_report")

    def junior_fn(intake_d, ctx):
        return junior(intake_d, ctx)

    def pm_fn(j_output, ctx):
        return pm(j_output, ctx)

    def partner_fn(pm_output, ctx):
        return partner(pm_output, ctx)

    orch = Orchestrator(
        case_id=intake.case_id,
        workflow="investigation_report",
        junior_fn=junior_fn,
        pm_fn=pm_fn,
        partner_fn=partner_fn,
        on_status_change=lambda s: on_progress(f"Status: {s.value}"),
    )

    context = {
        "case_id": intake.case_id,
        "workflow": "investigation_report",
        "investigation_type": inv_type,
        "audience": audience,
        "expert_witness": expert_witness,
        "intake": enriched_intake.model_dump(),
        "generate_arabic": intake.language == "ar",
        "client_name": intake.client_name,
    }

    on_progress("Starting investigation report pipeline...")
    partner_output = orch.run(enriched_intake.model_dump())

    # Build deliverable content
    content = _render_investigation_report(
        enriched_intake, partner_output, inv_type, audience
    )
    report_path = write_final_report(intake.case_id, content, intake.language)
    on_progress(f"Investigation report saved → {report_path}")

    deliverable = FinalDeliverable(
        case_id=intake.case_id,
        workflow="investigation_report",
        approved_by="partner",
        language=intake.language,
        content_en=content,
        citations=partner_output.get("output", partner_output).get("citations", []),
        revision_history=[0],
        delivery_date=datetime.now(timezone.utc),
    )

    return deliverable


def _process_case_documents(
    doc_manager: DocumentManager,
    inv_type: str,
    console: Console,
    on_progress: Callable,
) -> None:
    """Process uploaded case documents: timeline, transcripts, Excel."""
    index = doc_manager.get_index()
    if not index.documents:
        return

    on_progress(f"Processing {len(index.documents)} case documents...")

    # Build timeline from all docs
    try:
        on_progress("Building case timeline...")
        timeline = doc_manager.build_timeline()
        on_progress(f"Timeline: {len(timeline.events)} events extracted.")
    except Exception as e:
        console.print(f"  [yellow]Timeline build warning: {e}[/yellow]")

    # Process interview transcripts
    transcripts = [d for d in index.documents if d.doc_type == "interview_transcript"]
    for t in transcripts:
        try:
            on_progress(f"Processing transcript: {t.filename}...")
            doc_manager.process_interview_transcript(t.doc_id)
        except Exception:
            pass

    # Analyze Excel files
    excel_docs = [d for d in index.documents if d.doc_type == "excel_data"]
    for e in excel_docs:
        try:
            on_progress(f"Analyzing Excel: {e.filename}...")
            doc_manager.analyze_excel(e.doc_id, inv_type)
        except Exception:
            pass


def _render_investigation_report(
    intake: CaseIntake,
    partner_output: dict,
    inv_type: str,
    audience: str,
) -> str:
    """Render investigation report as Markdown."""
    now = datetime.now(timezone.utc).strftime("%d %B %Y")
    output = partner_output.get("output", partner_output)

    lines = [
        f"# Investigation Report",
        f"**Client:** {intake.client_name}",
        f"**Investigation Type:** {TYPE_LABELS.get(inv_type, inv_type)}",
        f"**Audience:** {audience.replace('_', ' ').title()}",
        f"**Date:** {now}",
        f"**Prepared by:** GoodWork Forensic Consulting",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        output.get("summary", ""),
        "",
        "---",
        "",
        "## Scope & Methodology",
        "",
        output.get("methodology", ""),
        "",
        "---",
        "",
        "## Findings",
        "",
    ]

    for i, finding in enumerate(output.get("findings", []), 1):
        lines += [
            f"### Finding {i}: {finding.get('title', '')}",
            f"**Risk Level:** {finding.get('risk_level', 'medium').title()}",
            "",
            finding.get("description", ""),
            "",
            f"**Evidence:** {finding.get('evidence', '')}",
            "",
        ]

    lines += [
        "---",
        "",
        "## Regulatory Implications",
        "",
        output.get("regulatory_implications", ""),
        "",
        "---",
        "",
        "## Recommendations",
        "",
    ]
    for rec in output.get("recommendations", []):
        lines.append(f"- {rec}")

    if output.get("open_questions"):
        lines += ["", "---", "", "## Open Questions / Further Procedures", ""]
        for q in output.get("open_questions", []):
            lines.append(f"- {q}")

    lines += [
        "",
        "---",
        "",
        "## Partner Sign-off",
        "",
        output.get("review_notes", ""),
        "",
        f"*Approved by: {output.get('approving_agent', 'Partner')}*",
        f"*Date: {now}*",
    ]

    return "\n".join(lines)
