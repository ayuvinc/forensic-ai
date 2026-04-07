# schemas/engagement_scope.py — Engagement Scoping workflow schemas (ARCH-S-04)
#
# BA sign-off: BA-010 (problem-first engagement scoping workflow).
# Used by: workflows/engagement_scoping.py (SCOPE-WF-01).
#
# Design: the scoping workflow uses a 5-step conversational flow.
# ScopeIntake captures what Maher knows about the client situation.
# ScopeRecommendation is the model's proposed engagement design.
# ConfirmedScope is the locked output after Maher approves — this is
# what gets written to state.json and routed to the appropriate workflow.

from typing import Literal, Optional
from pydantic import BaseModel


class ScopeIntake(BaseModel):
    """Captures the client situation and Maher's initial context.

    Populated during Step 2 of the engagement scoping conversation.
    The model asks open questions — these fields are extracted from
    the conversation, not presented as a form.
    """
    client_situation: str       # plain-language description of what the client is facing
    trigger: str                # what prompted GoodWork to be engaged
    desired_outcome: str        # what the client wants at the end
    constraints: str = ""       # time, budget, access limitations, confidentiality concerns
    known_red_flags: str = ""   # anything Maher already suspects or has been told
    client_industry: str = ""   # e.g. "real estate", "financial services"
    client_jurisdiction: str = ""   # primary operating jurisdiction


class ScopeRecommendation(BaseModel):
    """Model-proposed engagement scope, presented in Step 3 for Maher's review.

    The model draws on knowledge/engagement_taxonomy/framework.md (KF-NEW) to
    identify the best-fit engagement type(s) and propose scope components.
    Maher reviews this recommendation and either confirms it or triggers Step 4
    (follow-up questions to refine).
    """
    engagement_types: list[str]     # e.g. ["due_diligence", "investigation_report"]
    primary_engagement: str         # the single most relevant engagement type
    scope_components: list[str]     # what work will be done
    deliverables: list[str]         # what Maher will produce
    sequencing: list[str]           # recommended order if multiple engagements
    caveats: list[str] = []         # limitations, HUMINT flags, data access requirements
    chaining_suggestion: Optional[str] = None   # follow-on workflow if a red flag emerges
    rationale: str = ""             # one paragraph explaining why this scope fits the situation


class ConfirmedScope(BaseModel):
    """Locked scope document produced after Maher confirms the recommendation.

    Written to state.json before any drafting or document ingestion begins.
    For standard engagements: routed to the matching workflow in run.py/app.py.
    For novel/hybrid engagements: this document is itself the deliverable.
    """
    case_id: str
    intake: ScopeIntake
    recommendation: ScopeRecommendation

    # Routing — set after Maher confirms
    target_workflow: Optional[str] = None   # e.g. "due_diligence", "investigation_report"
    # None if engagement is novel/hybrid and scope document is the deliverable

    confirmed: bool = False     # True once Maher explicitly approves
    scope_content: str = ""     # formatted scope document text (markdown)

    # Standard disclaimer injection points
    humint_required: bool = False   # True → ARCH-GAP-02 text injected in scope document
    licensed_db_gap: bool = False   # True → ARCH-GAP-01 text injected for DD/Sanctions scopes
