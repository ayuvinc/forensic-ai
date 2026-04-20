from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, model_validator
from schemas.research import Citation


# ── AI Review Mode schema (P9-08b) ────────────────────────────────────────────

class ReviewAnnotation(BaseModel):
    """One annotation produced by ReviewAgent for a single finding.

    finding_id matches the finding title or risk_id from the draft.
    support_level reflects how well the cited evidence supports the claim.
    Finding with citations=[] is auto-classified as 'unsupported' without a model call.
    """
    finding_id: str
    support_level: Literal["supported", "partially_supported", "unsupported"]
    evidence_cited: list[str] = []
    logic_gaps: list[str] = []
    rewritten_text: Optional[str] = None


class JuniorDraft(BaseModel):
    case_id: str
    version: int
    summary: str
    findings: list[dict]           # {title, description, evidence, risk_level}
    methodology: str
    regulatory_implications: str
    recommendations: list[str]
    open_questions: list[str]
    citations: list[Citation]
    revision_round: int = 0


class ReviewFinding(BaseModel):
    section: str
    issue: str
    severity: Literal["critical", "major", "minor"]
    suggested_action: str


class RevisionRequest(BaseModel):
    from_agent: str
    to_agent: str
    revision_round: int
    findings: list[ReviewFinding]
    must_fix: list[str]
    should_fix: list[str]
    missing_citations: list[str]


class ApprovalDecision(BaseModel):
    approving_agent: str
    approved: bool
    conditions: list[str]
    regulatory_sign_off: str
    escalation_required: bool = False
    escalation_reason: Optional[str] = None


class FinalDeliverable(BaseModel):
    case_id: str
    workflow: str
    approved_by: str
    language: str
    content_en: str
    content_ar: Optional[str] = None
    citations: list[Citation]
    revision_history: list[int]
    delivery_date: datetime


class PersonaReviewOutput(BaseModel):
    persona: str
    perspective: str
    objections: list[str]
    questions: list[str]
    weak_sections: list[str]
    regulatory_gaps: list[str]
    overall_verdict: Literal["pass", "conditional_pass", "fail"]
    recommendation: str


# ── FRM Risk Register models ───────────────────────────────────────────────────

class RiskItem(BaseModel):
    risk_id: str
    category: str
    title: str
    description: str
    red_flags: list[str] = []
    likelihood: int                    # 1–5
    likelihood_rationale: str = ""
    impact: int                        # 1–5
    impact_rationale: str = ""
    risk_rating: int = 0               # computed: likelihood × impact
    risk_owner: str = ""               # editable by consultant
    existing_controls: list[str] = []
    control_gaps: list[str] = []
    recommendations: list[str] = []   # COSO/ACFE/ISO 37001 or novel
    regulatory_references: list[Citation] = []
    framework_references: list[str] = []

    @model_validator(mode="after")
    def compute_risk_rating(self) -> "RiskItem":
        if self.risk_rating == 0:
            self.risk_rating = self.likelihood * self.impact
        return self


class FRMModuleOutput(BaseModel):
    case_id: str
    module_number: int
    module_name: str
    version: int
    content: str
    risk_items: list[RiskItem] = []
    citations: list[Citation] = []
    revision_round: int = 0


class FRMDeliverable(BaseModel):
    case_id: str
    modules_completed: list[int] = []
    risk_register: list[RiskItem] = []
    executive_summary: str = ""
    content_en: str = ""
    content_ar: Optional[str] = None
    citations: list[Citation] = []
    delivery_date: datetime


# ── FRM Guided Exercise models (Phase 13 — ARCH-S-01) ─────────────────────────

class RiskContextItem(BaseModel):
    """Stores the consultant's per-sub-area answers during the FRM guided exercise.

    Created in FRM-R-03 for each sub-area Maher confirms as applicable.
    Passed to the model in FRM-R-04 to generate one RiskItem at a time.
    If is_baseline=True, all fields were pre-filled from industry knowledge
    (zero-info mode) and require consultant review before the item enters the register.
    """
    sub_area: str           # e.g. "Customer Due Diligence"
    module_number: int      # FRM module this sub-area belongs to (1–8)
    incident: str = ""      # known incidents or red flags; empty = none provided
    existing_controls: str = ""  # controls currently in place; empty = none known
    probability: int        # 1–5; set by consultant or pre-filled in zero-info mode
    impact: int             # 1–5; set by consultant or pre-filled in zero-info mode
    consultant_notes: str = ""   # freeform additional context from Maher
    is_baseline: bool = False    # True when pre-filled from knowledge base, not consultant input


# ── Historical Knowledge Library models (Phase 10C — ARCH-S-07) ───────────────

class SanitisedIndexEntry(BaseModel):
    """Sanitised record of a historical report or register stored in firm_profile/.

    No PII fields by design — enforced at model level, not by convention.
    This schema is the authoritative definition of what is permitted in any
    historical index.json file. Fields not listed here must never appear there.

    Created by KnowledgeLibrary.ingest() after sanitise() passes validation.
    If sanitise() detects residual PII, it raises SanitisationError before this
    model is ever constructed — no partial writes.
    """
    service_type: Literal[
        "frm_register",
        "due_diligence",
        "sanctions_screening",
        "transaction_testing",
        "proposal",
        "scope_letter",
    ]
    industry: str           # e.g. "construction", "financial_services"
    jurisdiction: str       # e.g. "UAE", "India" — no sub-jurisdiction detail
    company_size_band: Literal["<50", "50-200", "200-1000", ">1000"]
    engagement_date_year: int        # year only — not month/day (reduces re-identification risk)
    scope_components: list[str]      # e.g. ["Module 2 AML", "Module 4 Bribery/ABC"]
    risk_count: int                  # number of risks or findings in the source document
    key_patterns: list[str]          # anonymised patterns, e.g. "vendor concentration risk"
    source_file_hash: str            # SHA-256 of original file — deduplication only, not PII
    provenance: Literal["BASELINE", "FROM_SIMILAR_ENGAGEMENT"]
