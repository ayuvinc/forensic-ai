from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, model_validator
from schemas.research import Citation


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
