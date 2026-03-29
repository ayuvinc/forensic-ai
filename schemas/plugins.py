"""Plugin manifest and artifact envelope schemas.

Resolves Codex Findings #1 and #2:
  - PluginManifest.role used for model routing (not plugin_id)
  - ArtifactEnvelope (persisted) vs AgentHandoff (in-memory) are distinct shapes
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional, TypedDict
from pydantic import BaseModel


# ── In-memory: passed between agents within a pipeline run ───────────────────

class AgentHandoff(TypedDict):
    output: dict              # agent's Pydantic model as dict
    revision_requested: bool
    revision_reason: Optional[str]
    agent: str                # "junior" | "pm" | "partner"
    workflow: str
    turn_count: int
    tool_calls_made: list[str]


# ── Persisted: written to disk, used on resume ───────────────────────────────

class ArtifactEnvelope(BaseModel):
    """Canonical persisted artifact. Orchestrator loads this on resume."""
    case_id: str
    agent: str
    role: str                 # "junior" | "pm" | "partner" — matches get_model() routing key
    artifact_type: str        # e.g. "junior_output", "pm_review", "partner_approval"
    version: int
    workflow: str
    status: str               # CaseStatus value at time of write
    payload: dict             # agent's Pydantic model as dict
    created_at: datetime
    tool_calls_made: list[str] = []
    revision_round: int = 0


# ── Plugin manifest ───────────────────────────────────────────────────────────

class PluginManifest(BaseModel):
    plugin_id: str                    # matches folder name: "junior_analyst"
    role: str                         # routing key for get_model(): "junior" | "pm" | "partner" | "persona"
    plugin_type: Literal["agent", "persona"]
    version: str = "1.0.0"
    enabled: bool = True
    supported_workflows: list[str] = []
    input_schema: str = ""
    output_schema: str = ""
    required_tools: list[str] = []    # must use canonical tool registry IDs
    model_preference: Literal["haiku", "sonnet", "opus"] = "haiku"
    max_turns: int = 10
    timeout_seconds: int = 120
    revision_capable: bool = False
    artifact_type: str = "output"     # canonical artifact_type for this agent's output
    persona_perspective: Optional[str] = None

    def to_agent_manifest(self) -> Any:
        """Convert to AgentManifest. Uses self.role for model routing (not plugin_id)."""
        from core.agent_base import AgentManifest
        return AgentManifest(
            plugin_id=self.role,      # CRITICAL: pass role, not plugin_id
            model_preference=self.model_preference,
            max_turns=self.max_turns,
            timeout_seconds=self.timeout_seconds,
            required_tools=self.required_tools,
            revision_capable=self.revision_capable,
            supported_workflows=self.supported_workflows,
        )
