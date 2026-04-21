from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from core.state_machine import CaseStatus


class CaseIntake(BaseModel):
    case_id: str
    client_name: str
    industry: str
    company_size: Optional[str] = None
    primary_jurisdiction: str = "UAE"              # single-venue: governs report language + law refs
    operating_jurisdictions: list[str] = ["UAE"]   # multi-jurisdiction regulatory + company lookup
    workflow: str
    description: str
    language: str = "en"
    created_at: datetime
    engagement_letter_path: Optional[str] = None   # set at intake
    sample_report_paths: list[str] = []            # investigation style calibration
    engagement_id: Optional[str] = None            # P9 project slug if launched from Engagements page
    recommendation_depth: Optional[str] = None     # FR-03: "structured" | "executive" | "detailed" (FRM only)


class CaseState(BaseModel):
    case_id: str
    workflow: str
    status: CaseStatus
    revision_rounds: dict[str, int] = {}   # {"junior": 0, "pm": 0}
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error: Optional[str] = None
