"""Transaction Testing workflow (SL-GATE-03).

Two-stage intake: engagement context → testing plan → Maher review → SCOPE_CONFIRMED → testing.
State transitions: INTAKE_CREATED → SCOPE_CONFIRMED → DELIVERABLE_WRITTEN.

BA sign-off: BA-009.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable, Optional

from rich.console import Console
from rich.prompt import Prompt, Confirm

from config import ANTHROPIC_API_KEY, SONNET
from core.hook_engine import HookEngine
from core.tool_registry import ToolRegistry
from schemas.artifacts import FinalDeliverable
from schemas.case import CaseIntake
from schemas.transaction_testing import (
    TTIntakeContext,
    TestingPlan,
    TestObjective,
    TTResult,
)
from tools.file_tools import (
    append_audit_event,
    write_artifact,
    write_final_report,
    write_state,
    read_state,
)

_FRAUD_TYPOLOGY_LABELS = {
    "procurement_fraud": "Procurement Fraud",
    "payroll_fraud": "Payroll Fraud",
    "expense_fraud": "Expense/Reimbursement Fraud",
    "cash_fraud": "Cash and Petty Cash Fraud",
    "financial_stmt_fraud": "Financial Statement Fraud",
    "aml": "AML / Suspicious Transaction Patterns",
}


def run_transaction_testing_workflow(
    intake: CaseIntake,
    registry: ToolRegistry,
    hook_engine: HookEngine,
    console: Optional[Console] = None,
    on_progress: Optional[Callable[[str], None]] = None,
) -> FinalDeliverable:
    """Run a Transaction Testing engagement — 2-stage intake + testing plan review."""
    if console is None:
        console = Console()
    if on_progress is None:
        on_progress = lambda msg: console.print(f"  [cyan]{msg}[/cyan]")

    # ── Stage 1 + 2: Collect intake ───────────────────────────────────────────
    tt_intake = _collect_intake(console)

    # ── Propose testing plan ──────────────────────────────────────────────────
    on_progress("Proposing testing plan based on engagement context...")
    testing_plan = _propose_testing_plan(intake, tt_intake)

    # ── Show plan to Maher for review ─────────────────────────────────────────
    console.print("\n  [bold yellow]Proposed Testing Plan[/bold yellow]")
    console.print(f"  Engagement: {testing_plan.engagement_context}")
    if testing_plan.fraud_typology:
        console.print(f"  Fraud typology: {_FRAUD_TYPOLOGY_LABELS.get(testing_plan.fraud_typology, testing_plan.fraud_typology)}")
    console.print(f"  Population: {testing_plan.population}")
    console.print(f"  Date range: {testing_plan.date_range}")
    console.print(f"  Method: {testing_plan.method_summary}")
    console.print(f"\n  [bold]Proposed tests ({len(testing_plan.tests)}):[/bold]")
    for obj in testing_plan.tests:
        console.print(f"    [{obj.test_id}] {obj.name}")
        console.print(f"         {obj.method}")
    if testing_plan.caveats:
        console.print("\n  [yellow]Caveats:[/yellow]")
        for c in testing_plan.caveats:
            console.print(f"    • {c}")

    console.print()
    confirmed = Confirm.ask("  Confirm this testing plan and proceed?")
    if not confirmed:
        # Allow Maher to provide feedback and regenerate once
        feedback = Prompt.ask("  Describe adjustments needed")
        on_progress("Revising testing plan...")
        testing_plan = _revise_testing_plan(intake, tt_intake, testing_plan, feedback)
        console.print("\n  [bold yellow]Revised Testing Plan[/bold yellow]")
        for obj in testing_plan.tests:
            console.print(f"    [{obj.test_id}] {obj.name}")
        confirmed = Confirm.ask("  Confirm revised plan and proceed?")
        if not confirmed:
            console.print("  [yellow]Testing plan not confirmed. Workflow cancelled.[/yellow]")
            raise ValueError("Transaction testing plan not confirmed by consultant.")

    testing_plan.confirmed = True

    # ── Write SCOPE_CONFIRMED state ───────────────────────────────────────────
    _write_scope_confirmed(intake.case_id, testing_plan)
    append_audit_event(intake.case_id, {
        "event": "scope_confirmed",
        "agent": "transaction_testing",
        "workflow": "transaction_testing",
        "test_count": len(testing_plan.tests),
        "status": "ok",
    })
    on_progress("Testing plan confirmed. State: SCOPE_CONFIRMED.")

    # ── Document ingestion prompt ─────────────────────────────────────────────
    console.print("\n  [bold]Document Ingestion[/bold]")
    console.print("  Upload transaction data files to the case folder, then press Enter.")
    console.print(f"  Case folder: cases/{intake.case_id}/")
    console.print("  Accepted: Excel (.xlsx), CSV, exported GL/ERP data")
    input("  Press Enter when documents are ready (or Enter to proceed without documents)...")

    # ── Generate testing report ───────────────────────────────────────────────
    on_progress("Drafting Transaction Testing report...")
    content = _generate_testing_report(intake, tt_intake, testing_plan)

    report_path = write_final_report(intake.case_id, content, "en")
    on_progress(f"Report saved → {report_path}")

    write_artifact(intake.case_id, "transaction_testing", "deliverable", {
        "case_id": intake.case_id,
        "workflow": "transaction_testing",
        "engagement_context": tt_intake.engagement_context,
        "fraud_typology": tt_intake.fraud_typology,
        "test_count": len(testing_plan.tests),
        "evidence_standard": tt_intake.evidence_standard,
        "language": intake.language,
        "report_path": str(report_path),
        "delivery_date": datetime.now(timezone.utc).isoformat(),
    })
    append_audit_event(intake.case_id, {
        "event": "deliverable_generated",
        "agent": "transaction_testing",
        "workflow": "transaction_testing",
        "status": "ok",
    })

    return FinalDeliverable(
        case_id=intake.case_id,
        workflow="transaction_testing",
        approved_by="partner",
        language=intake.language,
        content_en=content,
        citations=[],
        revision_history=[0],
        delivery_date=datetime.now(timezone.utc),
    )


# ── Intake ─────────────────────────────────────────────────────────────────────

def _collect_intake(console: Console) -> TTIntakeContext:
    console.print("\n  [bold]Transaction Testing — Stage 1: Engagement Context[/bold]")
    context = Prompt.ask(
        "  Engagement context",
        choices=["fraud_discovery", "fraud_quantification", "audit_compliance", "due_diligence", "regulatory"],
        default="fraud_discovery",
    )

    fraud_typology = None
    suspects: list[str] = []
    controls_framework = ""
    specific_controls: list[str] = []
    target_financial_systems = ""
    regulator = ""
    prescribed_methodology = ""
    reporting_deadline = ""

    console.print("\n  [bold]Transaction Testing — Stage 2: Scope Detail[/bold]")

    if context in ("fraud_discovery", "fraud_quantification"):
        console.print("  Fraud typology:")
        for k, label in _FRAUD_TYPOLOGY_LABELS.items():
            console.print(f"    {k}: {label}")
        fraud_typology = Prompt.ask(
            "  Select typology",
            choices=list(_FRAUD_TYPOLOGY_LABELS.keys()),
            default="procurement_fraud",
        )
        suspects_raw = Prompt.ask("  Known suspects or persons of interest (names/roles, or Enter to skip)", default="")
        suspects = [s.strip() for s in suspects_raw.split(",") if s.strip()] if suspects_raw else []

    elif context == "audit_compliance":
        controls_framework = Prompt.ask("  Controls framework being tested (e.g. COSO, ISO 27001, UAE CB guidelines)")
        controls_raw = Prompt.ask("  Specific controls to test (comma-separated, or Enter for all)")
        specific_controls = [c.strip() for c in controls_raw.split(",") if c.strip()] if controls_raw else []

    elif context == "due_diligence":
        target_financial_systems = Prompt.ask("  Target's ERP or accounting system (or 'unknown')", default="unknown")

    elif context == "regulatory":
        regulator = Prompt.ask("  Regulator requiring this testing (e.g. CBUAE, DFSA, SCA)")
        prescribed_methodology = Prompt.ask("  Prescribed methodology or framework (if any)", default="")
        reporting_deadline = Prompt.ask("  Reporting deadline", default="")

    # Common fields
    data_inventory = Prompt.ask("  Data available / expected (e.g. 'GL export Jan-Dec 2024, AP ledger', or 'TBD')", default="TBD")
    population_size = Prompt.ask("  Approximate number of transactions in scope (or 'unknown')", default="unknown")
    date_range = Prompt.ask("  Transaction date range (e.g. 'Jan 2023 – Dec 2024')")
    evidence_standard = Prompt.ask(
        "  Evidence standard",
        choices=["internal_review", "regulatory_submission", "court_ready", "board_pack"],
        default="internal_review",
    )
    sampling = Prompt.ask(
        "  Full population or sampling?",
        choices=["full_population", "sampling"],
        default="full_population",
    )
    timeline = Prompt.ask("  Timeline requirement (or Enter to skip)", default="")

    return TTIntakeContext(
        engagement_context=context,
        fraud_typology=fraud_typology,
        suspects_identified=suspects,
        controls_framework=controls_framework,
        specific_controls=specific_controls,
        target_financial_systems=target_financial_systems,
        regulator=regulator,
        prescribed_methodology=prescribed_methodology,
        reporting_deadline=reporting_deadline,
        data_inventory=data_inventory,
        population_size=population_size,
        date_range=date_range,
        evidence_standard=evidence_standard,
        full_population_or_sample=sampling,
        timeline=timeline,
    )


# ── Testing plan ───────────────────────────────────────────────────────────────

def _propose_testing_plan(intake: CaseIntake, tt_intake: TTIntakeContext) -> TestingPlan:
    """Sonnet proposes a testing plan based on the intake context."""
    import anthropic

    typology_label = _FRAUD_TYPOLOGY_LABELS.get(tt_intake.fraud_typology or "", "Not specified")
    suspects_str = ", ".join(tt_intake.suspects_identified) if tt_intake.suspects_identified else "None identified"

    prompt = f"""You are a senior forensic accountant. Propose a transaction testing plan.

ENGAGEMENT CONTEXT: {tt_intake.engagement_context}
FRAUD TYPOLOGY: {typology_label}
SUSPECTS / PERSONS OF INTEREST: {suspects_str}
DATA AVAILABLE: {tt_intake.data_inventory}
POPULATION SIZE: {tt_intake.population_size}
DATE RANGE: {tt_intake.date_range}
EVIDENCE STANDARD: {tt_intake.evidence_standard}
SAMPLING APPROACH: {tt_intake.full_population_or_sample}
CLIENT: {intake.client_name}

Propose a testing plan. Return a JSON object with this exact structure:
{{
  "engagement_context": "one-sentence summary",
  "fraud_typology": "{tt_intake.fraud_typology or 'N/A'}",
  "population": "description of what will be tested",
  "date_range": "{tt_intake.date_range}",
  "method_summary": "one-paragraph description of overall approach",
  "caveats": ["caveat 1", "caveat 2"],
  "tests": [
    {{
      "test_id": "T-01",
      "name": "test name",
      "fraud_area": "specific fraud area this test targets",
      "method": "procedure description (2-3 sentences)",
      "population": "what records/data this test covers",
      "sample_rationale": "why sampling if applicable, else empty string",
      "expected_output": "what a finding looks like",
      "acfe_reference": "ACFE or IIA reference if applicable, else empty string"
    }}
  ]
}}

Propose 3–6 tests appropriate to the typology and data available. If data is TBD or unknown, note this in caveats and propose tests that would apply once data is received.
Return only valid JSON — no markdown, no explanation.
"""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=SONNET,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    return _parse_testing_plan(intake.case_id, tt_intake, resp.content[0].text.strip())


def _revise_testing_plan(
    intake: CaseIntake,
    tt_intake: TTIntakeContext,
    current_plan: TestingPlan,
    feedback: str,
) -> TestingPlan:
    """Sonnet revises the testing plan based on consultant feedback."""
    import anthropic

    current_tests = "\n".join(
        f"  [{t.test_id}] {t.name}: {t.method}" for t in current_plan.tests
    )
    prompt = f"""Revise this transaction testing plan based on the consultant's feedback.

CURRENT PLAN:
Population: {current_plan.population}
Method: {current_plan.method_summary}
Tests:
{current_tests}

CONSULTANT FEEDBACK: {feedback}

Return revised JSON in the same structure as before. Return only valid JSON.
"""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=SONNET,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_testing_plan(intake.case_id, tt_intake, resp.content[0].text.strip())


def _parse_testing_plan(case_id: str, tt_intake: TTIntakeContext, raw: str) -> TestingPlan:
    """Parse Sonnet JSON response into a TestingPlan. Fallback on parse error."""
    import json, re

    try:
        # Strip code block if present
        match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", raw)
        data = json.loads(match.group(1) if match else raw)
        tests = [TestObjective(**t) for t in data.get("tests", [])]
        return TestingPlan(
            case_id=case_id,
            engagement_context=data.get("engagement_context", tt_intake.engagement_context),
            fraud_typology=data.get("fraud_typology") or tt_intake.fraud_typology,
            tests=tests,
            population=data.get("population", tt_intake.population_size),
            date_range=data.get("date_range", tt_intake.date_range),
            method_summary=data.get("method_summary", ""),
            caveats=data.get("caveats", []),
        )
    except Exception:
        # Fallback: minimal plan
        return TestingPlan(
            case_id=case_id,
            engagement_context=tt_intake.engagement_context,
            fraud_typology=tt_intake.fraud_typology,
            tests=[TestObjective(
                test_id="T-01",
                name="General transaction review",
                fraud_area=tt_intake.fraud_typology or "general",
                method="Review transaction data for anomalies, duplicates, and patterns consistent with fraud.",
                population=tt_intake.population_size,
                expected_output="List of exceptions for manual review",
            )],
            population=tt_intake.population_size,
            date_range=tt_intake.date_range,
            method_summary="General transaction review — testing plan could not be parsed from model response.",
            caveats=["Testing plan was not fully parsed — review and adjust before proceeding."],
        )


def _write_scope_confirmed(case_id: str, testing_plan: TestingPlan) -> None:
    """Write SCOPE_CONFIRMED state to state.json."""
    existing = read_state(case_id) or {}
    existing.update({
        "status": "scope_confirmed",
        "workflow": "transaction_testing",
        "scope_confirmed_at": datetime.now(timezone.utc).isoformat(),
        "test_count": len(testing_plan.tests),
        "testing_plan_confirmed": True,
    })
    write_state(case_id, existing)


# ── Report generation ──────────────────────────────────────────────────────────

def _generate_testing_report(
    intake: CaseIntake,
    tt_intake: TTIntakeContext,
    testing_plan: TestingPlan,
) -> str:
    """Sonnet: draft the Transaction Testing report from the confirmed plan."""
    import anthropic

    tests_str = "\n".join(
        f"[{t.test_id}] {t.name}\n  Method: {t.method}\n  Population: {t.population}\n  Expected output: {t.expected_output}"
        for t in testing_plan.tests
    )
    caveats_str = "\n".join(f"- {c}" for c in testing_plan.caveats) if testing_plan.caveats else "None noted."
    typology_label = _FRAUD_TYPOLOGY_LABELS.get(tt_intake.fraud_typology or "", "Not specified")

    prompt = f"""You are a senior forensic accountant. Draft a Transaction Testing report.

CLIENT: {intake.client_name}
ENGAGEMENT CONTEXT: {tt_intake.engagement_context}
FRAUD TYPOLOGY: {typology_label}
POPULATION: {testing_plan.population}
DATE RANGE: {testing_plan.date_range}
EVIDENCE STANDARD: {tt_intake.evidence_standard}
DATA AVAILABLE: {tt_intake.data_inventory}
DATE: {datetime.now(timezone.utc).strftime('%d %B %Y')}

CONFIRMED TESTING PLAN:
{tests_str}

CAVEATS:
{caveats_str}

Draft the Transaction Testing report with this structure:
1. Executive Summary (engagement purpose, scope, overall conclusion placeholder)
2. Engagement Background (context, who engaged GoodWork, trigger event)
3. Methodology (testing approach, sampling rationale, data sources, standards applied)
4. Testing Results (for each test: objective, procedure, findings, exceptions identified — use BASELINE FINDINGS since no documents have been reviewed yet; clearly label each section as "[FINDINGS PENDING — Document review required]")
5. Exceptions Summary (table or list — placeholder for actual exceptions)
6. Conclusions and Recommendations (draft conclusions framework; final conclusions pending document review)
7. Limitations and Caveats

IMPORTANT: Since no documents have been reviewed yet, clearly mark all findings sections as "[FINDINGS PENDING — Document review required]". The report structure, methodology, and framework should be complete and professional. The consultant will populate findings after document review.

Format in Markdown with clear numbered headings.
"""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=SONNET,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    body = resp.content[0].text.strip()

    header = (
        f"# Transaction Testing Report\n"
        f"**Client:** {intake.client_name}\n"
        f"**Engagement:** {tt_intake.engagement_context.replace('_', ' ').title()}\n"
        f"**Typology:** {typology_label}\n"
        f"**Date:** {datetime.now(timezone.utc).strftime('%d %B %Y')}\n"
        f"**Status:** DRAFT — Findings pending document review\n\n"
        f"---\n\n"
    )

    return header + body
