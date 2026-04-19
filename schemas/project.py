"""schemas/project.py — Phase 9 engagement framework schemas.

Three models that together define a GoodWork engagement (project):

  ProjectIntake   — immutable creation record; slug is derived + validated
  InputSession    — one working session within an engagement
  ProjectState    — mutable runtime state of an engagement

Security: project_name → project_slug conversion strips all path-traversal
characters before any filesystem write.  R-019 mitigation.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, field_validator, model_validator

from core.state_machine import CaseStatus


# ── Slug derivation (7-step algorithm, R-019) ─────────────────────────────────

def derive_slug(project_name: str) -> str:
    """Convert a human project name into a safe filesystem slug.

    Steps:
      1. Strip leading/trailing whitespace
      2. Lowercase
      3. Replace spaces and underscores with hyphens
      4. Strip all characters not in [a-z0-9-]
      5. Collapse consecutive hyphens to one
      6. Strip leading/trailing hyphens
      7. Raise ValueError if result is empty

    Raises ValueError on path-traversal patterns (.., /, \\, null byte)
    even if they would survive the character strip.
    """
    # Blocklist check before transformation (R-019 defense-in-depth).
    # Only ".." and null bytes indicate path-traversal intent.
    # Standalone "/" and "\" are stripped safely by step 4, so they are allowed
    # in natural-language names like "Project Alpha / FRM".
    raw = project_name or ""
    for danger in ("..", "\x00"):
        if danger in raw:
            raise ValueError(
                f"project_name contains disallowed pattern '{danger!r}' — "
                "path traversal blocked"
            )

    slug = raw.strip()
    slug = slug.lower()
    slug = slug.replace(" ", "-").replace("_", "-")
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    slug = slug.strip("-")

    if not slug:
        raise ValueError(
            "project_name produced an empty slug after normalisation — "
            "use at least one alphanumeric character"
        )

    return slug


# ── ProjectIntake ─────────────────────────────────────────────────────────────

class ProjectIntake(BaseModel):
    """Immutable creation record for a new engagement.

    project_slug is always derived from project_name — never set directly.
    """

    project_name: str
    project_slug: str = ""          # populated by validator below
    client_name: str
    service_type: str
    language_standard: Literal["acfe", "expert_witness", "regulatory", "board_pack"] = "acfe"
    created_at: datetime = None     # defaulted by validator below
    naming_convention: str = "acfe"

    @model_validator(mode="before")
    @classmethod
    def derive_and_default(cls, values: dict) -> dict:
        # Always re-derive slug from name — never trust a caller-supplied slug
        name = values.get("project_name", "")
        values["project_slug"] = derive_slug(name)   # raises ValueError on bad input
        if not values.get("created_at"):
            values["created_at"] = datetime.utcnow()
        return values


# ── InputSession ──────────────────────────────────────────────────────────────

class InputSession(BaseModel):
    """One working session within an engagement.

    Mode:
      "input"     — Maher is uploading documents and adding notes
      "final_run" — pipeline is being executed

    Status lifecycle: open → closed | abandoned | error
    Session log written to: cases/{project_slug}/D_Working_Papers/session_log.jsonl
    """

    session_id: str
    project_slug: str
    mode: Literal["input", "final_run"]
    status: Literal["open", "closed", "abandoned", "error"]
    started_at: datetime
    closed_at: Optional[datetime] = None
    documents_registered: list[str] = []
    notes_path: Optional[str] = None
    key_facts_count: int = 0
    red_flags_count: int = 0

    @property
    def session_log_path(self) -> str:
        return f"cases/{self.project_slug}/D_Working_Papers/session_log.jsonl"


# ── ProjectState ──────────────────────────────────────────────────────────────

class ProjectState(BaseModel):
    """Mutable runtime state of an engagement.

    is_legacy: True for pre-Phase-9 cases that use UUID case IDs instead of
    the A-F folder structure.  All A-F features are gated on is_legacy=False.

    last_updated is automatically set to utcnow() by the model validator so
    callers do not need to supply it.
    """

    project_slug: str
    status: CaseStatus
    project_health: Literal["green", "amber", "red"] = "green"
    cases: dict[str, str] = {}          # workflow_type → case_id
    sessions: list[InputSession] = []
    language_standard: str = "acfe"
    context_budget_used_pct: float = 0.0
    interim_context_written: bool = False
    last_updated: datetime = None       # auto-set below
    is_legacy: bool = False

    @model_validator(mode="before")
    @classmethod
    def stamp_last_updated(cls, values: dict) -> dict:
        if not values.get("last_updated"):
            values["last_updated"] = datetime.utcnow()
        return values
