# schemas/policy_sop_cobuild.py — Sprint-IA-04 (BA-IA-09)
#
# State models for the Policy/SOP guided co-build session.
# These live only in Streamlit session_state and in E_Drafts/cobuild_progress.json
# for resume. They are never written to the historical knowledge index.

from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel


class CoBuildSection(BaseModel):
    """One section in the co-build loop."""
    section_title: str
    body: str = ""
    # pending = not yet drafted/reviewed; approved/edited/regenerated = Maher acted on it
    status: Literal["pending", "approved", "edited", "regenerated"] = "pending"
    # Free-text note attached by the page (e.g. "pre-filled from uploaded document")
    action_note: str = ""


class CoBuildState(BaseModel):
    """Full co-build session state persisted to E_Drafts/cobuild_progress.json."""
    sections: list[CoBuildSection]
    current_idx: int = 0
    doc_type: str          # "policy" | "sop"
    doc_subtype: str       # e.g. "whistleblower_policy"
    gap_analysis: str = "new"   # "new" | "gap"
    custom_scope: Optional[dict] = None   # answers from custom scoping conversation
    structure_confirmed: bool = False
    aic_context: str = ""  # answers injected from AIC questions stage
    # Serialised CaseIntake fields for resume after page refresh.
    # Stored as a plain dict so we avoid a circular import between schemas.
    intake_snapshot: dict = {}
