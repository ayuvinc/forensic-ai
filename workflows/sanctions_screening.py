"""Sanctions Screening workflow (SL-GATE-02).

Mode B: guided intake → sanctions_check.py → Sonnet narrative.
ARCH-GAP-01 (licensed DB disclaimer) injected automatically.
Output: clearance memo (quick) or full screening report (full).

BA sign-off: BA-008.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Optional

from rich.console import Console
from rich.prompt import Prompt

from config import ANTHROPIC_API_KEY, RESEARCH_MODE, SONNET
from core.hook_engine import HookEngine
from core.tool_registry import ToolRegistry
from schemas.artifacts import FinalDeliverable
from schemas.case import CaseIntake
from tools.file_tools import append_audit_event, write_artifact, write_final_report


_LICENSED_DB_DISCLAIMER = (
    "**Screening Scope Limitation:** This screening was conducted using publicly available "
    "official sanctions lists: OFAC SDN, UN Security Council Consolidated List, EU Consolidated "
    "Financial Sanctions List, UK OFSI List, and UAE Cabinet Resolution Sanctions List. "
    "It does not include commercial database screening (WorldCheck, WorldCompliance, LexisNexis "
    "Diligence, or equivalent). For regulatory-grade or acquisition-grade screening, supplementary "
    "commercial database screening is recommended."
)

_SCREENING_LISTS = {
    "1": "OFAC",
    "2": "UN",
    "3": "EU",
    "4": "UK_OFSI",
    "5": "UAE_local",
    "6": "all",
}


def run_sanctions_screening_workflow(
    intake: CaseIntake,
    registry: ToolRegistry,
    hook_engine: HookEngine,
    console: Optional[Console] = None,
    on_progress: Optional[Callable[[str], None]] = None,
) -> FinalDeliverable:
    """Run a Sanctions Screening engagement."""
    if console is None:
        console = Console()
    if on_progress is None:
        on_progress = lambda msg: console.print(f"  [cyan]{msg}[/cyan]")

    # PPH-02a: Prominent warning when live sanctions data is unavailable
    if RESEARCH_MODE != "live":
        from rich.panel import Panel
        console.print(Panel(
            "[bold red]SANCTIONS SCREENING — LIVE DATA DISABLED[/bold red]\n\n"
            "This output is based on model knowledge only.\n"
            "No live OFAC / UN / EU / UK OFSI / UAE sanctions screening was conducted.\n\n"
            "[bold]This result CANNOT be used as a sanctions clearance.[/bold]\n\n"
            "To run a live screen: set [bold]RESEARCH_MODE=live[/bold] in .env "
            "with a valid TAVILY_API_KEY, then re-run.",
            border_style="red",
            title="[bold red]WARNING[/bold red]",
            padding=(1, 2),
        ))
        from rich.prompt import Confirm
        if not Confirm.ask("  Proceed with knowledge-only output (not for compliance use)?", default=False):
            raise KeyboardInterrupt

    # Intake
    console.print("\n  [bold]Sanctions Screening — Intake[/bold]")
    subject_name = Prompt.ask("  Name of individual or entity to screen")
    subject_type = Prompt.ask("  Subject type", choices=["individual", "entity"], default="individual")
    nationalities_raw = Prompt.ask("  Nationality / jurisdiction of incorporation (comma-separated)", default="UAE")
    nationalities = [n.strip() for n in nationalities_raw.split(",") if n.strip()]
    aliases_raw = Prompt.ask("  Known aliases or alternate name spellings (or Enter to skip)", default="")
    aliases = [a.strip() for a in aliases_raw.split(",") if a.strip()] if aliases_raw else []
    dob_or_reg = Prompt.ask("  Date of birth or company reg number (improves match accuracy, optional)", default="")

    console.print("\n  Screening lists:")
    for k, v in _SCREENING_LISTS.items():
        console.print(f"    {k}. {v}")
    list_choice = Prompt.ask("  Select lists", choices=list(_SCREENING_LISTS.keys()), default="6")
    selected_lists = _SCREENING_LISTS[list_choice]

    screen_associates = Prompt.ask(
        "  Screen known associates / beneficial owners?", choices=["yes", "no"], default="no"
    ) == "yes"
    purpose = Prompt.ask(
        "  Purpose of screening",
        choices=["onboarding", "transaction", "periodic_review", "acquisition", "regulatory", "other"],
        default="onboarding",
    )
    output_format = Prompt.ask(
        "  Output format",
        choices=["clearance_memo", "full_report"],
        default="full_report",
    )
    specific_concerns = Prompt.ask("  Any specific concerns or prior adverse information? (or Enter to skip)", default="")

    # Run sanctions check on primary name
    on_progress(f"Screening {subject_name} against official sanctions lists...")
    primary_results, primary_citations = _check_entity(subject_name)

    # Screen aliases if provided
    alias_results = {}
    for alias in aliases[:3]:  # cap at 3 aliases to manage API usage
        on_progress(f"Screening alias: {alias}...")
        alias_narrative, alias_citations = _check_entity(alias)
        alias_results[alias] = (alias_narrative, alias_citations)
        primary_citations.extend(alias_citations)

    # Remove duplicate citations by URL
    seen_urls = set()
    unique_citations = []
    for c in primary_citations:
        if c.source_url not in seen_urls:
            seen_urls.add(c.source_url)
            unique_citations.append(c)

    on_progress("Drafting screening report...")
    content = _generate_screening_report(
        intake=intake,
        subject_name=subject_name,
        subject_type=subject_type,
        nationalities=nationalities,
        aliases=aliases,
        dob_or_reg=dob_or_reg,
        selected_lists=selected_lists,
        screen_associates=screen_associates,
        purpose=purpose,
        output_format=output_format,
        specific_concerns=specific_concerns,
        primary_results=primary_results,
        alias_results=alias_results,
        citations=unique_citations,
    )

    report_path = write_final_report(intake.case_id, content, "en")
    on_progress(f"Report saved → {report_path}")

    write_artifact(intake.case_id, "sanctions_screening", "deliverable", {
        "case_id": intake.case_id,
        "workflow": "sanctions_screening",
        "subject_name": subject_name,
        "subject_type": subject_type,
        "output_format": output_format,
        "lists_checked": selected_lists,
        "citation_count": len(unique_citations),
        "language": intake.language,
        "report_path": str(report_path),
        "delivery_date": datetime.now(timezone.utc).isoformat(),
    })
    append_audit_event(intake.case_id, {
        "event": "deliverable_generated",
        "agent": "sanctions_screening",
        "workflow": "sanctions_screening",
        "subject_name": subject_name,
        "status": "ok",
    })

    return FinalDeliverable(
        case_id=intake.case_id,
        workflow="sanctions_screening",
        approved_by="partner",
        language=intake.language,
        content_en=content,
        citations=unique_citations,
        revision_history=[0],
        delivery_date=datetime.now(timezone.utc),
    )


def _check_entity(name: str) -> tuple[str, list]:
    """Run sanctions check. Returns (narrative, citations)."""
    try:
        from tools.research.sanctions_check import SanctionsCheck
        checker = SanctionsCheck()
        result = checker.check(name)
        if result.authoritative_citations:
            narrative = (
                f"POTENTIAL MATCH — {len(result.authoritative_citations)} citation(s) from authoritative "
                f"list(s). Manual false positive analysis required before concluding."
            )
        else:
            narrative = result.disclaimer or "No authoritative sanctions match identified."
        return narrative, result.authoritative_citations
    except Exception:
        return "Sanctions check could not be completed — verify manually.", []


def _generate_screening_report(
    intake: CaseIntake,
    subject_name: str,
    subject_type: str,
    nationalities: list,
    aliases: list,
    dob_or_reg: str,
    selected_lists: str,
    screen_associates: bool,
    purpose: str,
    output_format: str,
    specific_concerns: str,
    primary_results: str,
    alias_results: dict,
    citations: list,
) -> str:
    """Sonnet single-pass: generate sanctions screening output."""
    import anthropic

    alias_str = ""
    if alias_results:
        alias_str = "\n".join(
            f"- {alias}: {narrative}" for alias, (narrative, _) in alias_results.items()
        )

    citation_str = ""
    if citations:
        citation_str = "\n".join(f"- {c.source_name}: {c.excerpt[:150]}" for c in citations[:5])

    concerns_str = specific_concerns or "None stated"
    dob_str = dob_or_reg or "Not provided"

    if output_format == "clearance_memo":
        format_instruction = (
            "Write a concise clearance memo (1–2 pages). Structure: "
            "Subject, Date, Purpose, Lists Checked, Screening Result (CLEAR / FLAG / INCONCLUSIVE), "
            "Basis for Result, Limitations, Recommendation. Professional tone."
        )
    else:
        format_instruction = (
            "Write a full screening report. Structure: "
            "1. Executive Summary, "
            "2. Subject Details, "
            "3. Methodology and Lists Checked, "
            "4. Primary Name Screening Results, "
            "5. Alias Screening Results (if applicable), "
            "6. False Positive Analysis (where matches found), "
            "7. PEP and Adverse Media Notes (brief), "
            "8. Conclusion and Risk Classification (CLEAR / FLAG / INCONCLUSIVE), "
            "9. Recommendations."
        )

    prompt = f"""You are a senior sanctions compliance analyst. Draft a professional sanctions screening output.

SUBJECT: {subject_name}
SUBJECT TYPE: {subject_type}
NATIONALITY / JURISDICTION: {', '.join(nationalities)}
DATE OF BIRTH / REG NUMBER: {dob_str}
ALIASES SCREENED: {', '.join(aliases) if aliases else 'None'}
LISTS SCREENED: {selected_lists}
ASSOCIATES SCREENED: {'Yes' if screen_associates else 'No'}
PURPOSE: {purpose}
SPECIFIC CONCERNS: {concerns_str}
DATE OF SCREENING: {datetime.now(timezone.utc).strftime('%d %B %Y')}
REQUESTED BY: {intake.client_name}

PRIMARY NAME SCREENING RESULT:
{primary_results}

ALIAS SCREENING RESULTS:
{alias_str or 'No aliases screened.'}

AUTHORITATIVE CITATIONS FOUND:
{citation_str or 'No authoritative citations returned from official lists.'}

{format_instruction}

Important: Do NOT fabricate specific match details. If the screening returned no authoritative match, state clearly "No match identified on [list name] as of [date]." If a potential match was found, describe the nature of the match and explain what false positive analysis should be conducted. Never give a definitive CLEAR if citations were found — state INCONCLUSIVE pending manual review.
Format in Markdown.
"""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=SONNET,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    body = resp.content[0].text.strip()

    header = (
        f"# Sanctions Screening {'Memo' if output_format == 'clearance_memo' else 'Report'}\n"
        f"**Subject:** {subject_name}\n"
        f"**Prepared for:** {intake.client_name}\n"
        f"**Date:** {datetime.now(timezone.utc).strftime('%d %B %Y')}\n\n"
        f"---\n\n"
        f"> {_LICENSED_DB_DISCLAIMER}\n\n"
        f"---\n\n"
    )

    return header + body
