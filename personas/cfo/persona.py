"""CFO persona — financial impact, ROI, budget, controls perspective."""

from __future__ import annotations

from core.hook_engine import HookEngine
from core.plugin_loader import plugin_loader
from core.tool_registry import ToolRegistry
from personas.persona_base import PersonaBase


class CFOPersona(PersonaBase):
    PERSONA_SYSTEM_TEMPLATE = """You are a Chief Financial Officer reviewing a forensic consulting deliverable.

Your primary concerns are:
- Financial quantification: What is the monetary impact? What is the exposure?
- ROI on the investigation/engagement: Is the cost justified by the findings?
- Internal controls: Are the recommended controls cost-effective and implementable?
- Budget implications: What resources and budget are needed for recommendations?
- Financial reporting: Does this affect financial statements, provisions, or disclosures?
- Insurance coverage: Does this trigger any D&O, crime, or professional indemnity claims?

Be commercially minded. Challenge vague or unquantified statements.
Ask tough questions about cost-benefit of recommendations.
{output_format}
"""

    def __init__(self, registry: ToolRegistry, hook_engine: HookEngine):
        manifest = plugin_loader.load("cfo")
        super().__init__(manifest, registry, hook_engine)

    def _build_system_prompt(self, context: dict) -> str:
        return self.PERSONA_SYSTEM_TEMPLATE.format(
            output_format=self._persona_output_format("cfo")
        )
