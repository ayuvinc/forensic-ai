# schemas/transaction_testing.py — Transaction Testing intake and output schemas (ARCH-S-03)
#
# BA sign-off: BA-009 (two-stage intake + testing plan review before document ingestion).
# Key architectural constraint: testing plan must be locked in state.json at SCOPE_CONFIRMED
# before document ingestion begins. The TTIntakeContext and TestingPlan schemas enforce this
# sequencing by being distinct — intake produces TTIntakeContext; Maher reviews the proposed
# TestingPlan; only after confirmation does the state transition to SCOPE_CONFIRMED.

from typing import Literal, Optional
from pydantic import BaseModel


# ── Stage 1 + 2 Intake ────────────────────────────────────────────────────────

class TTIntakeContext(BaseModel):
    """Stage 1 + 2 intake for a Transaction Testing engagement.

    Stage 1 (all branches): engagement_context — determines which branch to follow.
    Stage 2 (branch-specific questions): fraud_typology and supporting fields.

    Fraud typology drives the entire testing methodology:
        procurement_fraud     → three-way matching (PO/Invoice/Payment), vendor analysis, split PO
        payroll_fraud         → ghost employee, rate manipulation, overtime analysis
        expense_fraud         → duplicate submissions, round-dollar, weekend/holiday spend
        cash_fraud            → petty cash reconciliation, sequencing gaps
        financial_stmt_fraud  → journal entry testing, cut-off, revenue recognition
        aml                   → structuring patterns, counterparty analysis, layering
    """
    # Stage 1 — branch gate
    engagement_context: Literal[
        "fraud_discovery",       # does fraud exist?
        "fraud_quantification",  # fraud confirmed — measure the loss
        "audit_compliance",      # testing controls against a framework
        "due_diligence",         # financial integrity pre-acquisition / pre-investment
        "regulatory",            # regulator-mandated testing
    ]

    # Stage 2 — fraud branches (A/B)
    fraud_typology: Optional[Literal[
        "procurement_fraud",
        "payroll_fraud",
        "expense_fraud",
        "cash_fraud",
        "financial_stmt_fraud",
        "aml",
    ]] = None
    suspects_identified: list[str] = []    # names/roles if suspects known at intake

    # Stage 2 — audit/compliance branch (C)
    controls_framework: str = ""           # e.g. "ISO 27001", "COSO", "UAE CB guidelines"
    specific_controls: list[str] = []

    # Stage 2 — due diligence branch (D)
    target_financial_systems: str = ""     # ERP / accounting system in use

    # Stage 2 — regulatory branch (E)
    regulator: str = ""
    prescribed_methodology: str = ""
    reporting_deadline: str = ""

    # Common core (all branches)
    data_inventory: str = ""               # what data Maher has or expects to receive
    population_size: str = ""             # rough count of transactions in scope
    date_range: str = ""                  # e.g. "Jan 2023 – Dec 2024"
    evidence_standard: Literal[
        "internal_review",
        "regulatory_submission",
        "court_ready",
        "board_pack",
    ] = "internal_review"
    full_population_or_sample: Literal["full_population", "sampling"] = "full_population"
    timeline: str = ""


# ── Testing Plan (model-proposed, Maher reviews before document ingestion) ────

class TestObjective(BaseModel):
    """A single test objective within the testing plan.

    The model proposes these in FRM-R-03 / SL-GATE-03; Maher reviews and confirms
    (or deselects) before any document ingestion begins.
    """
    test_id: str                   # e.g. "T-01"
    name: str                      # e.g. "Three-way matching — PO/Invoice/Payment"
    fraud_area: str                # e.g. "Procurement fraud — fictitious vendor"
    method: str                    # procedure description
    population: str                # what records will be tested
    sample_rationale: str = ""     # why sampling if not full population
    expected_output: str           # what a finding looks like in this test
    acfe_reference: str = ""       # ACFE or IIA standard reference, if applicable


class TestingPlan(BaseModel):
    """Model-proposed testing plan presented to Maher for review before document ingestion.

    State transition: INTAKE_CREATED → SCOPE_CONFIRMED happens when Maher confirms this plan.
    The confirmed plan is written to state.json before any document upload is accepted.
    """
    case_id: str
    engagement_context: str        # summary of Stage 1 answer
    fraud_typology: Optional[str] = None
    tests: list[TestObjective]
    population: str                # overall population description
    date_range: str
    method_summary: str            # one-paragraph description of the overall approach
    caveats: list[str] = []        # limitations, data dependencies, advisory notes
    confirmed: bool = False        # set True when Maher approves; gates SCOPE_CONFIRMED


# ── Transaction Testing Result ─────────────────────────────────────────────────

class TTFinding(BaseModel):
    """A single finding from a completed transaction test."""
    test_id: str                   # references TestObjective.test_id
    test_name: str
    finding: str                   # what was found
    exception_count: int = 0       # number of exceptions identified
    amount_at_risk: str = ""       # monetary value if quantifiable
    risk_level: Literal["high", "medium", "low", "informational"]
    recommendation: str


class TTResult(BaseModel):
    """Output schema for a completed Transaction Testing engagement."""
    case_id: str
    testing_plan: TestingPlan
    findings: list[TTFinding] = []
    overall_conclusion: str = ""
    total_exceptions: int = 0
    total_amount_at_risk: str = ""
    methodology_notes: str = ""    # limitations, sampling rationale, data quality notes
    content_en: str = ""           # full formatted report text
