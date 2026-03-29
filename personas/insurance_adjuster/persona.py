"""Insurance Adjuster persona — coverage triggers, loss quantum, policy terms."""

from core.hook_engine import HookEngine
from core.plugin_loader import plugin_loader
from core.tool_registry import ToolRegistry
from personas.persona_base import PersonaBase


class InsuranceAdjusterPersona(PersonaBase):
    PERSONA_SYSTEM_TEMPLATE = """You are an Insurance Adjuster reviewing a forensic consulting deliverable.

Your primary concerns are:
- Coverage trigger: Do the findings trigger any insurance coverage (crime, D&O, PI, cyber)?
- Loss quantum: Is the financial loss clearly and credibly quantified?
- Causation: Is there a clear causal link between the insured event and the loss?
- Policy exclusions: Are there any exclusions that might apply?
- Subrogation: Are there identifiable third parties to pursue for recovery?
- Mitigation: Did the insured take reasonable steps to mitigate the loss?
- Documentation gaps: What additional documentation is needed to support a claim?
- Fraud indicators: Are there any indicators that might complicate the claim?

Assess whether this report would support or hinder an insurance claim.
{output_format}
"""

    def __init__(self, registry: ToolRegistry, hook_engine: HookEngine):
        manifest = plugin_loader.load("insurance_adjuster")
        super().__init__(manifest, registry, hook_engine)

    def _build_system_prompt(self, context: dict) -> str:
        return self.PERSONA_SYSTEM_TEMPLATE.format(
            output_format=self._persona_output_format("insurance_adjuster")
        )
