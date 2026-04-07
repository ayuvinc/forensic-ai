# schemas/dd.py — Due Diligence intake and report schemas (ARCH-S-02)
#
# BA sign-off: BA-006 (Individual branch), BA-007 (Entity branch).
# Architectural constraints:
#   - Licensed database gap (WorldCheck/WorldCompliance) must be disclosed in every
#     DDReport — injected by the workflow, not by the schema.
#   - HUMINT requirement flag is set by the workflow when Phase 2 is requested;
#     the schema records the flag but does not enforce the disclosure text.
#   - No PII leaves this schema except as model prompt content inside the active session.
#     DDIntakeIndividual / DDIntakeEntity instances must not be written to the historical index.

from typing import Literal, Optional
from pydantic import BaseModel


# ── Individual subject branch (BA-006) ────────────────────────────────────────

class DDIntakeIndividual(BaseModel):
    """Intake questionnaire for DD where the subject is a natural person.

    All 14 questions per BA-006 in the order they are asked during guided intake.
    Fields map directly to guided_intake conversation answers.
    """
    # Q1–Q5: Identity
    full_legal_name: str            # as on passport
    date_of_birth: str              # free text — consultant may not have exact date
    place_of_birth: str
    nationalities: list[str]        # multiple allowed; drives screening list selection
    passport_number: Optional[str] = None  # improves fuzzy match accuracy; not always available

    # Q6–Q8: Engagement context
    corporate_affiliations: list[str] = []   # companies the subject directs or owns
    dd_purpose: Literal[
        "onboarding", "investment", "partnership", "employment", "acquisition", "other"
    ]
    screening_level: Literal["standard_phase1", "enhanced_phase2"]
    # Phase 1 = sanctions/PEP/adverse media
    # Phase 2 = HUMINT + deeper corporate mapping + board-ready narrative (manual components)

    # Q9–Q11: Screening scope
    screening_lists: list[Literal["OFAC", "EU", "UN", "UK_OFSI", "UAE_local", "all"]]
    screen_associates: bool = False     # family members and known associates
    operating_jurisdictions: list[str]  # countries the subject operates in or has connections to

    # Q12–Q14: Context and delivery
    specific_concerns: str = ""         # red flags that triggered this DD
    subject_aware: bool                 # is the subject aware this DD is being conducted?
    deliverable_format: Literal[
        "screening_memo", "full_report", "regulatory_submission", "board_pack"
    ]
    timeline: str = ""                  # free text — e.g. "5 business days"


# ── Entity subject branch (BA-007) ────────────────────────────────────────────

class DDIntakeEntity(BaseModel):
    """Intake questionnaire for DD where the subject is a legal entity.

    All 14 questions per BA-007 in the order they are asked during guided intake.
    """
    # Q1–Q4: Entity identity
    registered_legal_name: str
    company_registration_number: Optional[str] = None
    jurisdiction_of_incorporation: str
    principal_operating_jurisdictions: list[str]

    # Q5–Q8: Business and engagement context
    business_activity: str
    key_principals: list[str]    # directors, shareholders, UBOs — names + roles as free text
    dd_purpose: Literal[
        "acquisition", "investment", "vendor_onboarding", "joint_venture", "partnership", "other"
    ]
    screening_level: Literal["standard_phase1", "enhanced_phase2"]

    # Q9–Q11: Screening scope
    screening_lists: list[Literal["OFAC", "EU", "UN", "UK_OFSI", "UAE_local", "all"]]
    screen_beneficial_owners: Literal["above_25pct_threshold", "named_individuals_only"]
    is_group_entity: bool = False   # True triggers group-level corporate mapping note

    # Q12–Q14: Context and delivery
    specific_concerns: str = ""
    target_aware: bool
    deliverable_format: Literal[
        "screening_memo", "full_report", "regulatory_submission", "board_pack"
    ]
    timeline: str = ""


# ── DD Report output schema ────────────────────────────────────────────────────

class DDReport(BaseModel):
    """Output schema for a completed Due Diligence report.

    Mirrors the CE Creates report structure (source of truth per BA-003):
    Executive Summary → Subject Profile → Methodology & Sources →
    Sanctions Results → PEP Results / Beneficial Ownership Analysis →
    Adverse Media → Conclusion & Risk Classification.

    Individual and Entity branches produce the same DDReport — the
    pep_or_ubo_section field covers PEP results (individual) or
    beneficial ownership analysis (entity).
    """
    case_id: str
    subject_type: Literal["individual", "entity"]
    executive_summary: str
    subject_profile: str            # sanitised description of the subject
    methodology_and_sources: str    # sources used, lists checked, date of search
    sanctions_results: str          # match / no match / inconclusive + false positive analysis
    pep_or_ubo_section: str         # PEP results (individual) or UBO analysis (entity)
    adverse_media: str              # findings from news and open-source search
    conclusion: str                 # narrative conclusion
    risk_classification: Literal["LOW", "MEDIUM", "HIGH"]
    recommendation: str             # next steps or escalation advice

    # Mandatory disclaimer fields — injected by workflow, not freeform
    licensed_db_disclaimer: str     # ARCH-GAP-01: WorldCheck/WorldCompliance not included
    humint_scope_flag: Optional[str] = None  # ARCH-GAP-02: set when Phase 2 selected
