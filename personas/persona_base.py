"""Persona base — wraps BaseAgent for client persona reviews."""

from __future__ import annotations

import json
import re
from typing import Optional

from core.agent_base import BaseAgent
from core.hook_engine import HookEngine
from core.tool_registry import ToolRegistry
from schemas.artifacts import PersonaReviewOutput
from schemas.plugins import PluginManifest


class PersonaBase:
    """Base class for all client personas (CFO, Lawyer, Regulator, Insurance Adjuster)."""

    PERSONA_SYSTEM_TEMPLATE = ""  # override in subclass

    def __init__(
        self,
        manifest: PluginManifest,
        registry: ToolRegistry,
        hook_engine: HookEngine,
        tool_definitions: list[dict] | None = None,
        workflow: str = "persona_review",
    ):
        agent_manifest = manifest.to_agent_manifest()
        self._agent = BaseAgent(
            manifest=agent_manifest,
            registry=registry,
            hook_engine=hook_engine,
            tool_definitions=tool_definitions or [],
            workflow=workflow,
        )
        self._manifest = manifest
        self._workflow = workflow

    def review(self, deliverable: str | dict, context: dict) -> PersonaReviewOutput:
        """Review a deliverable from this persona's perspective."""
        if isinstance(deliverable, dict):
            deliverable_text = json.dumps(deliverable, indent=2, default=str)[:6000]
        else:
            deliverable_text = str(deliverable)[:6000]

        system_prompt = self._build_system_prompt(context)
        task_message = self._build_task_message(deliverable_text, context)

        result = self._agent.run(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": task_message}],
            context=context,
        )

        return self._parse_output(result["text"])

    def _build_system_prompt(self, context: dict) -> str:
        return self.PERSONA_SYSTEM_TEMPLATE

    def _build_task_message(self, deliverable_text: str, context: dict) -> str:
        return (
            "Review the following deliverable from your perspective. "
            "Provide structured feedback in the required JSON format.\n\n"
            f"DELIVERABLE:\n{deliverable_text}"
        )

    def _parse_output(self, text: str) -> PersonaReviewOutput:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                return PersonaReviewOutput(
                    persona=data.get("persona", self._manifest.plugin_id),
                    perspective=data.get("perspective", ""),
                    objections=data.get("objections", []),
                    questions=data.get("questions", []),
                    weak_sections=data.get("weak_sections", []),
                    regulatory_gaps=data.get("regulatory_gaps", []),
                    overall_verdict=data.get("overall_verdict", "conditional_pass"),
                    recommendation=data.get("recommendation", ""),
                )
            except Exception:
                pass

        return PersonaReviewOutput(
            persona=self._manifest.plugin_id,
            perspective="Parse error",
            objections=["Could not parse structured output"],
            questions=[],
            weak_sections=[],
            regulatory_gaps=[],
            overall_verdict="conditional_pass",
            recommendation=text[:300],
        )

    @staticmethod
    def _persona_output_format(persona_name: str) -> str:
        return f"""
OUTPUT FORMAT (required JSON):
{{
  "persona": "{persona_name}",
  "perspective": "Brief statement of your role and concerns...",
  "objections": ["Specific objection 1", "..."],
  "questions": ["Question this raises for me", "..."],
  "weak_sections": ["Section that needs strengthening", "..."],
  "regulatory_gaps": ["Missing regulatory reference or gap", "..."],
  "overall_verdict": "pass|conditional_pass|fail",
  "recommendation": "Overall recommendation and key action items..."
}}
"""
