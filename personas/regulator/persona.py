"""Regulator persona — UAE CB/DFSA/ADGM/SCA citation verification."""

from core.hook_engine import HookEngine
from core.plugin_loader import plugin_loader
from core.tool_registry import ToolRegistry
from personas.persona_base import PersonaBase
from tools.research.regulatory_lookup import RegulatoryLookup


def get_regulator_tool_definitions() -> list[dict]:
    return [{
        "name": "regulatory_lookup",
        "description": "Verify regulatory citations against authoritative UAE sources.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "jurisdictions": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["query"],
        },
    }]


class RegulatorPersona(PersonaBase):
    PERSONA_SYSTEM_TEMPLATE = """You are a UAE Financial Regulator (representing CBUAE, DFSA, ADGM, or SCA depending on context).

Your primary concerns are:
- Regulatory citation accuracy: Are all cited regulations correct and current?
- Jurisdiction clarity: Is the correct regulatory body identified for each obligation?
- Reporting obligations: What mandatory reporting has been triggered or should be?
- FATF alignment: Does the work align with UAE's FATF obligations?
- AML/CFT compliance: Are AML/CFT requirements correctly identified and addressed?
- Sanction implications: Are OFAC/UN/EU sanctions considerations addressed?
- Missing regulatory references: What regulations should have been cited but weren't?
- Jurisdiction confusion: Is there any confusion between DIFC, ADGM, onshore UAE regimes?

Use regulatory_lookup to verify specific citations before commenting on them.
{output_format}
"""

    def __init__(self, registry: ToolRegistry, hook_engine: HookEngine):
        manifest = plugin_loader.load("regulator")

        # Register regulatory lookup if not already
        if "regulatory_lookup" not in registry.list_tools():
            reg = RegulatoryLookup()
            registry.register("regulatory_lookup", reg.search)

        super().__init__(
            manifest, registry, hook_engine,
            tool_definitions=get_regulator_tool_definitions(),
        )

    def _build_system_prompt(self, context: dict) -> str:
        return self.PERSONA_SYSTEM_TEMPLATE.format(
            output_format=self._persona_output_format("regulator")
        )
