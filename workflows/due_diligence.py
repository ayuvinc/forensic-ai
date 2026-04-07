"""Due Diligence workflow — Individual and Entity branches (SL-GATE-01).

Mode B: Sonnet single-pass with guided intake.
ARCH-GAP-01 (licensed DB disclaimer) injected automatically.
ARCH-GAP-02 (HUMINT scope flag) injected when Phase 2 selected.

BA sign-off: BA-006 (Individual), BA-007 (Entity).
"""

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
from schemas.dd import DDIntakeIndividual, DDIntakeEntity, DDReport
from tools.file_tools import append_audit_event, write_artifact, write_final_report


# ── ARCH-GAP-01: Licensed database disclaimer (injected into every DD report) ──

_LICENSED_DB_DISCLAIMER = (
    "**Screening Scope Limitation:** This screening was conducted using publicly available "
    "official sanctions and regulatory lists (OFAC SDN, UN Security Council, EU Consolidated "
    "Financial Sanctions List, UK OFSI, UAE Cabinet Resolution Sanctions List). It does not "
    "include commercial database screening (WorldCheck, WorldCompliance, LexisNexis Diligence, "
    "or equivalent services). For acquisition-grade or regulatory-grade due diligence, "
    "supplementary commercial database screening is recommended."
)

# ── ARCH-GAP-02: HUMINT scope flag (injected when Phase 2 selected) ──

_HUMINT_SCOPE_FLAG = (
    "**HUMINT Scope — Manual Execution Required:** This engagement scope includes components "
    "that require discreet human source enquiries (HUMINT). HUMINT cannot be performed by "
    "this tool. The section(s) below define the HUMINT scope and objectives. Execution requires "
    "qualified human investigators. This tool has defined the scope; delivery is a manual step."
)


def run_due_diligence_workflow(
    intake: CaseIntake,
    registry: ToolRegistry,
    hook_engine: HookEngine,
    console: Optional[Console] = None,
    on_progress: Optional[Callable[[str], None]] = None,
) -> FinalDeliverable:
    """Run a Due Diligence engagement — Individual or Entity branch."""
    if console is None:
        console = Console()
    if on_progress is None:
        on_progress = lambda msg: console.print(f"  [cyan]{msg}[/cyan]")

    console.print("\n  [bold]Due Diligence — Subject Type[/bold]")
    subject_type = Prompt.ask("  Subject type", choices=["individual", "entity"], default="individual")

    if subject_type == "individual":
        dd_intake = _collect_individual_intake(console)
    else:
        dd_intake = _collect_entity_intake(console)

    humint_required = (
        getattr(dd_intake, "screening_level", "") == "enhanced_phase2"
    )

    # Sanctions check — always run
    on_progress("Running sanctions screening...")
    sanctions_results, sanctions_citations = _run_sanctions_check(dd_intake)

    # Regulatory context (jurisdiction-aware)
    on_progress("Fetching regulatory context...")
    reg_citations = _fetch_reg_context(dd_intake, intake)

    # Generate report
    on_progress("Drafting Due Diligence report...")
    content = _generate_dd_report(
        intake=intake,
        dd_intake=dd_intake,
        subject_type=subject_type,
        sanctions_results=sanctions_results,
        reg_citations=reg_citations,
        humint_required=humint_required,
    )

    all_citations = sanctions_citations + reg_citations
    report_path = write_final_report(intake.case_id, content, "en")
    on_progress(f"Report saved → {report_path}")

    write_artifact(intake.case_id, "due_diligence", "deliverable", {
        "case_id": intake.case_id,
        "workflow": "due_diligence",
        "subject_type": subject_type,
        "screening_level": getattr(dd_intake, "screening_level", "standard_phase1"),
        "humint_required": humint_required,
        "citation_count": len(all_citations),
        "language": intake.language,
        "report_path": str(report_path),
        "delivery_date": datetime.now(timezone.utc).isoformat(),
    })
    append_audit_event(intake.case_id, {
        "event": "deliverable_generated",
        "agent": "due_diligence",
        "workflow": "due_diligence",
        "subject_type": subject_type,
        "status": "ok",
    })

    return FinalDeliverable(
        case_id=intake.case_id,
        workflow="due_diligence",
        approved_by="partner",
        language=intake.language,
        content_en=content,
        citations=all_citations,
        revision_history=[0],
        delivery_date=datetime.now(timezone.utc),
    )


# ── Intake collectors ──────────────────────────────────────────────────────────

def _collect_individual_intake(console: Console) -> DDIntakeIndividual:
    console.print("\n  [bold]Individual Due Diligence — Intake[/bold]")
    full_name = Prompt.ask("  Full legal name (as on passport)")
    dob = Prompt.ask("  Date of birth (or approximate year)", default="not provided")
    place_of_birth = Prompt.ask("  Place of birth", default="not provided")
    nationalities_raw = Prompt.ask("  Nationalities (comma-separated)")
    nationalities = [n.strip() for n in nationalities_raw.split(",") if n.strip()]
    passport = Prompt.ask("  Passport number (optional — improves matching accuracy)", default="")
    affiliations_raw = Prompt.ask("  Known corporate affiliations (companies/roles, or Enter to skip)", default="")
    affiliations = [a.strip() for a in affiliations_raw.split(",") if a.strip()] if affiliations_raw else []
    purpose = Prompt.ask(
        "  Purpose of DD",
        choices=["onboarding", "investment", "partnership", "employment", "acquisition", "other"],
        default="onboarding",
    )
    level = Prompt.ask(
        "  Screening level",
        choices=["standard_phase1", "enhanced_phase2"],
        default="standard_phase1",
    )
    lists_raw = Prompt.ask("  Screening lists (all / OFAC / EU / UN / UK_OFSI / UAE_local)", default="all")
    screening_lists = ["all"] if lists_raw.strip().lower() == "all" else [l.strip() for l in lists_raw.split(",")]
    screen_associates = Prompt.ask("  Screen known associates and family members?", choices=["yes", "no"], default="no") == "yes"
    jurisdictions_raw = Prompt.ask("  Operating jurisdictions (comma-separated)")
    jurisdictions = [j.strip() for j in jurisdictions_raw.split(",") if j.strip()]
    concerns = Prompt.ask("  Specific concerns or red flags that triggered this DD (or Enter to skip)", default="")
    subject_aware = Prompt.ask("  Is the subject aware this DD is being conducted?", choices=["yes", "no"], default="no") == "yes"
    deliverable = Prompt.ask(
        "  Deliverable format",
        choices=["screening_memo", "full_report", "regulatory_submission", "board_pack"],
        default="full_report",
    )
    timeline = Prompt.ask("  Timeline requirement (or Enter to skip)", default="")

    return DDIntakeIndividual(
        full_legal_name=full_name,
        date_of_birth=dob,
        place_of_birth=place_of_birth,
        nationalities=nationalities,
        passport_number=passport or None,
        corporate_affiliations=affiliations,
        dd_purpose=purpose,
        screening_level=level,
        screening_lists=screening_lists,
        screen_associates=screen_associates,
        operating_jurisdictions=jurisdictions,
        specific_concerns=concerns,
        subject_aware=subject_aware,
        deliverable_format=deliverable,
        timeline=timeline,
    )


def _collect_entity_intake(console: Console) -> DDIntakeEntity:
    console.print("\n  [bold]Entity Due Diligence — Intake[/bold]")
    legal_name = Prompt.ask("  Registered legal name")
    reg_number = Prompt.ask("  Company registration number (optional)", default="")
    jurisdiction_inc = Prompt.ask("  Jurisdiction of incorporation")
    jurisdictions_raw = Prompt.ask("  Principal operating jurisdictions (comma-separated)")
    jurisdictions = [j.strip() for j in jurisdictions_raw.split(",") if j.strip()]
    business = Prompt.ask("  Business activity / industry")
    principals_raw = Prompt.ask("  Key principals — directors, shareholders, UBOs (names + roles, comma-separated)")
    principals = [p.strip() for p in principals_raw.split(",") if p.strip()]
    purpose = Prompt.ask(
        "  Purpose of DD",
        choices=["acquisition", "investment", "vendor_onboarding", "joint_venture", "partnership", "other"],
        default="investment",
    )
    level = Prompt.ask(
        "  Screening level",
        choices=["standard_phase1", "enhanced_phase2"],
        default="standard_phase1",
    )
    lists_raw = Prompt.ask("  Screening lists (all / OFAC / EU / UN / UK_OFSI / UAE_local)", default="all")
    screening_lists = ["all"] if lists_raw.strip().lower() == "all" else [l.strip() for l in lists_raw.split(",")]
    ubo_scope = Prompt.ask(
        "  Beneficial owner screening scope",
        choices=["above_25pct_threshold", "named_individuals_only"],
        default="above_25pct_threshold",
    )
    is_group = Prompt.ask("  Is this a group entity (multiple subsidiaries)?", choices=["yes", "no"], default="no") == "yes"
    concerns = Prompt.ask("  Specific concerns or red flags (or Enter to skip)", default="")
    target_aware = Prompt.ask("  Is the target aware this DD is being conducted?", choices=["yes", "no"], default="no") == "yes"
    deliverable = Prompt.ask(
        "  Deliverable format",
        choices=["screening_memo", "full_report", "regulatory_submission", "board_pack"],
        default="full_report",
    )
    timeline = Prompt.ask("  Timeline requirement (or Enter to skip)", default="")

    return DDIntakeEntity(
        registered_legal_name=legal_name,
        company_registration_number=reg_number or None,
        jurisdiction_of_incorporation=jurisdiction_inc,
        principal_operating_jurisdictions=jurisdictions,
        business_activity=business,
        key_principals=principals,
        dd_purpose=purpose,
        screening_level=level,
        screening_lists=screening_lists,
        screen_beneficial_owners=ubo_scope,
        is_group_entity=is_group,
        specific_concerns=concerns,
        target_aware=target_aware,
        deliverable_format=deliverable,
        timeline=timeline,
    )


# ── Research helpers ───────────────────────────────────────────────────────────

def _run_sanctions_check(dd_intake) -> tuple[str, list]:
    """Run sanctions check on primary subject name. Returns (narrative, citations)."""
    try:
        from tools.research.sanctions_check import SanctionsCheck
        checker = SanctionsCheck()
        name = getattr(dd_intake, "full_legal_name", None) or getattr(dd_intake, "registered_legal_name", "")
        result = checker.check(name)
        if result.authoritative_citations:
            narrative = f"POTENTIAL MATCH IDENTIFIED — {len(result.authoritative_citations)} authoritative citation(s) found. Requires manual review and false positive analysis before concluding."
        else:
            narrative = result.disclaimer or "No authoritative sanctions match identified from OFAC, UN, or EU sources."
        return narrative, result.authoritative_citations
    except Exception:
        return "Sanctions check could not be completed — verify manually against OFAC, UN, EU, UK OFSI, and UAE lists.", []


def _fetch_reg_context(dd_intake, intake: CaseIntake) -> list:
    """Fetch regulatory context for DD in the relevant jurisdictions."""
    try:
        from tools.research.regulatory_lookup import RegulatoryLookup
        reg = RegulatoryLookup()
        jurisdictions = (
            getattr(dd_intake, "operating_jurisdictions", None)
            or getattr(dd_intake, "principal_operating_jurisdictions", None)
            or intake.operating_jurisdictions
        )
        result = reg.search(
            query="due diligence KYC AML enhanced customer due diligence requirements",
            jurisdictions=jurisdictions,
        )
        return result.authoritative_citations
    except Exception:
        return []


# ── Report generation ──────────────────────────────────────────────────────────

def _generate_dd_report(
    intake: CaseIntake,
    dd_intake,
    subject_type: str,
    sanctions_results: str,
    reg_citations: list,
    humint_required: bool,
) -> str:
    """Sonnet single-pass: generate complete Due Diligence report."""
    import anthropic

    subject_name = (
        getattr(dd_intake, "full_legal_name", None)
        or getattr(dd_intake, "registered_legal_name", "")
    )
    screening_level = getattr(dd_intake, "screening_level", "standard_phase1")
    deliverable_format = getattr(dd_intake, "deliverable_format", "full_report")
    concerns = getattr(dd_intake, "specific_concerns", "") or "None stated"
    jurisdictions = (
        getattr(dd_intake, "operating_jurisdictions", None)
        or getattr(dd_intake, "principal_operating_jurisdictions", [])
    )

    reg_str = ""
    if reg_citations:
        reg_str = "\n".join(f"- {c.source_name}: {c.excerpt[:200]}" for c in reg_citations[:4])

    humint_section = ""
    if humint_required:
        humint_section = f"\n\n> {_HUMINT_SCOPE_FLAG}\n\n## HUMINT Scope (Manual Execution Required)\n\nThe following intelligence components fall within the scope of this engagement but require manual investigator action:\n- Discreet source enquiries regarding subject's reputation and associations\n- Verification of information that cannot be confirmed through open-source research\n- Any lifestyle or business conduct enquiries requiring physical presence or local networks\n\nThis section defines the scope. Findings to be integrated by the assigned investigator before final report issuance.\n"

    prompt = f"""You are a senior forensic due diligence analyst. Draft a professional Due Diligence report.

SUBJECT: {subject_name}
SUBJECT TYPE: {subject_type}
SCREENING LEVEL: {screening_level}
DELIVERABLE FORMAT: {deliverable_format}
OPERATING JURISDICTIONS: {', '.join(jurisdictions)}
PURPOSE: {getattr(dd_intake, 'dd_purpose', 'not specified')}
SPECIFIC CONCERNS: {concerns}
ENGAGEMENT CLIENT: {intake.client_name}
ENGAGEMENT DATE: {datetime.now(timezone.utc).strftime('%d %B %Y')}

SANCTIONS SCREENING RESULTS:
{sanctions_results}

REGULATORY REFERENCES FOUND:
{reg_str or "No specific references retrieved — apply FATF/ACFE general standards."}

Write the report using this structure:
1. Executive Summary (3–5 sentences: subject, purpose, key finding, risk classification, recommendation)
2. Subject Profile (identity, background, business activities, corporate affiliations as applicable)
3. Methodology and Sources (what was checked, which lists, what registries, date of search — be specific)
4. Sanctions and Regulatory Status (results of sanctions screening above; PEP status if applicable)
5. {"PEP Results and Associates" if subject_type == "individual" else "Beneficial Ownership and Corporate Structure"} (findings or 'no adverse findings identified')
6. Adverse Media (news, legal proceedings, regulatory actions — findings or 'no adverse findings identified')
7. Conclusion (narrative summary; risk classification: LOW / MEDIUM / HIGH with justification; recommendation)

Write professionally in English. Do not fabricate specific findings — if a section has no findings, state "No adverse findings identified from available open sources." Flag anything that requires manual verification.
Format in Markdown with clear numbered headings.
"""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=SONNET,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    body = resp.content[0].text.strip()

    # Assemble final report with mandatory disclaimer and optional HUMINT flag
    header = (
        f"# Due Diligence Report\n"
        f"**Subject:** {subject_name}\n"
        f"**Type:** {subject_type.title()}\n"
        f"**Prepared for:** {intake.client_name}\n"
        f"**Date:** {datetime.now(timezone.utc).strftime('%d %B %Y')}\n"
        f"**Screening Level:** {'Standard (Phase 1)' if screening_level == 'standard_phase1' else 'Enhanced (Phase 2)'}\n\n"
        f"---\n\n"
        f"> {_LICENSED_DB_DISCLAIMER}\n\n"
        f"---\n\n"
    )

    return header + body + humint_section
