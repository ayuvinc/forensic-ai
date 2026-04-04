"""Policy / SOP generator workflow — jurisdiction-aware regulatory citations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Optional

from rich.console import Console
from rich.prompt import Prompt

from config import ANTHROPIC_API_KEY, SONNET
from core.hook_engine import HookEngine
from core.tool_registry import ToolRegistry
from schemas.artifacts import FinalDeliverable
from schemas.case import CaseIntake
from tools.file_tools import append_audit_event, write_artifact, write_final_report


POLICY_TYPES = {
    "1": "aml_cft_policy",
    "2": "fraud_prevention_policy",
    "3": "whistleblower_policy",
    "4": "procurement_policy",
    "5": "conflict_of_interest_policy",
    "6": "data_privacy_policy",
    "7": "custom",
}

SOP_TYPES = {
    "1": "transaction_monitoring_sop",
    "2": "kyc_due_diligence_sop",
    "3": "fraud_investigation_sop",
    "4": "sanctions_screening_sop",
    "5": "suspicious_activity_reporting_sop",
    "6": "custom",
}


def run_policy_sop_workflow(
    intake: CaseIntake,
    registry: ToolRegistry,
    hook_engine: HookEngine,
    console: Optional[Console] = None,
    on_progress: Optional[Callable[[str], None]] = None,
) -> FinalDeliverable:
    """Generate policy or SOP document with regulatory citations."""
    if console is None:
        console = Console()
    if on_progress is None:
        on_progress = lambda msg: console.print(f"  [cyan]{msg}[/cyan]")

    doc_type = Prompt.ask("  Document type", choices=["policy", "sop"], default="policy")

    if doc_type == "policy":
        console.print("\n  Policy type:")
        for k, v in POLICY_TYPES.items():
            console.print(f"    {k}. {v.replace('_', ' ').title()}")
        choice = Prompt.ask("  Select", choices=list(POLICY_TYPES.keys()), default="1")
        doc_subtype = POLICY_TYPES[choice]
        if doc_subtype == "custom":
            doc_subtype = Prompt.ask("  Custom policy name")
    else:
        console.print("\n  SOP type:")
        for k, v in SOP_TYPES.items():
            console.print(f"    {k}. {v.replace('_', ' ').title()}")
        choice = Prompt.ask("  Select", choices=list(SOP_TYPES.keys()), default="1")
        doc_subtype = SOP_TYPES[choice]
        if doc_subtype == "custom":
            doc_subtype = Prompt.ask("  Custom SOP name")

    gap_analysis = Prompt.ask(
        "  Mode: new document or gap analysis of existing?",
        choices=["new", "gap"],
        default="new",
    )

    # Fetch regulatory citations first
    on_progress("Fetching regulatory requirements...")
    reg_citations = _fetch_regulatory_citations(doc_subtype, intake)

    on_progress(f"Drafting {doc_type}...")
    content = _generate_policy_sop(
        intake, doc_type, doc_subtype, gap_analysis, reg_citations
    )

    report_path = write_final_report(intake.case_id, content, "en")
    on_progress(f"Document saved → {report_path}")

    write_artifact(intake.case_id, "policy_sop", "deliverable", {
        "case_id": intake.case_id,
        "workflow": "policy_sop",
        "doc_subtype": doc_subtype,
        "language": intake.language,
        "report_path": str(report_path),
        "citation_count": len(reg_citations),
        "delivery_date": datetime.now(timezone.utc).isoformat(),
    })
    append_audit_event(intake.case_id, {
        "event": "deliverable_generated",
        "agent": "policy_sop",
        "workflow": "policy_sop",
        "status": "ok",
    })

    return FinalDeliverable(
        case_id=intake.case_id,
        workflow="policy_sop",
        approved_by="partner",
        language=intake.language,
        content_en=content,
        citations=reg_citations,
        revision_history=[0],
        delivery_date=datetime.now(timezone.utc),
    )


def _fetch_regulatory_citations(doc_subtype: str, intake: CaseIntake) -> list:
    """Fetch authoritative regulatory citations for this document type."""
    try:
        from tools.research.regulatory_lookup import RegulatoryLookup
        reg = RegulatoryLookup()
        result = reg.search(
            query=f"{doc_subtype.replace('_', ' ')} requirements regulations",
            jurisdictions=intake.operating_jurisdictions,
        )
        return result.authoritative_citations
    except Exception:
        return []


def _generate_policy_sop(
    intake: CaseIntake,
    doc_type: str,
    doc_subtype: str,
    mode: str,
    reg_citations: list,
) -> str:
    """Sonnet single-turn: generate complete policy/SOP document."""
    import anthropic

    citations_str = ""
    if reg_citations:
        citations_str = "\n".join(
            f"- {c.source_name}: {c.excerpt[:200]}"
            for c in reg_citations[:5]
        )

    prompt = f"""Draft a professional {doc_type} document for a {intake.industry} company.

DOCUMENT: {doc_subtype.replace('_', ' ').title()} {"(Gap Analysis)" if mode == "gap" else ""}
CLIENT: {intake.client_name}
JURISDICTION: {intake.primary_jurisdiction}
OPERATING JURISDICTIONS: {', '.join(intake.operating_jurisdictions)}

APPLICABLE REGULATORY REFERENCES:
{citations_str or "No specific references fetched — apply general best practice."}

{"Draft a new document" if mode == "new" else "Perform a gap analysis against current requirements"}.

Include:
1. Purpose and scope
2. Policy statement / SOP objective
3. Definitions
4. Roles and responsibilities
5. Detailed requirements / procedures (numbered steps for SOP)
6. Regulatory compliance references
7. Monitoring and review
8. Escalation procedures
9. Version history table

Write professionally in English. Reference specific regulation articles where applicable.
Format in Markdown with clear headings.
"""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=SONNET,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    header = f"# {doc_subtype.replace('_', ' ').title()}\n**Client:** {intake.client_name}\n**Date:** {datetime.now(timezone.utc).strftime('%d %B %Y')}\n\n---\n\n"
    return header + resp.content[0].text.strip()
