from datetime import datetime
from typing import Any
from pydantic import BaseModel
from core.state_machine import CaseStatus


class AgentHandoff(BaseModel):
    case_id: str
    from_agent: str
    to_agent: str
    status_before: CaseStatus
    status_after: CaseStatus
    payload: dict[str, Any]
    timestamp: datetime
    notes: str = ""
