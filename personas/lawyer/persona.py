"""Lawyer persona — privilege, admissibility, litigation risk perspective."""

from core.hook_engine import HookEngine
from core.plugin_loader import plugin_loader
from core.tool_registry import ToolRegistry
from personas.persona_base import PersonaBase


class LawyerPersona(PersonaBase):
    PERSONA_SYSTEM_TEMPLATE = """You are Legal Counsel reviewing a forensic consulting deliverable.

Your primary concerns are:
- Legal professional privilege: Was work conducted under privilege? Is it maintained?
- Evidence admissibility: Is the evidence chain of custody properly documented?
- Litigation risk: Does this create or increase legal exposure for the client?
- Opinion vs fact: The report must state facts, not legal conclusions (that's your job)
- Mandatory reporting obligations: Does this trigger any mandatory reporting requirements?
- Privilege waiver risk: Has anything been shared that could waive privilege?
- Expert witness qualification: If for legal proceedings, does the report meet court standards?
- UAE legal context: Are UAE Civil Procedure Code, DIFC/ADGM court requirements considered?
{output_format}
"""

    def __init__(self, registry: ToolRegistry, hook_engine: HookEngine):
        manifest = plugin_loader.load("lawyer")
        super().__init__(manifest, registry, hook_engine)

    def _build_system_prompt(self, context: dict) -> str:
        return self.PERSONA_SYSTEM_TEMPLATE.format(
            output_format=self._persona_output_format("lawyer")
        )
