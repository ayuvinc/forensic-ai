"""Junior Analyst agent — research and initial draft production."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from core.agent_base import BaseAgent
from core.hook_engine import HookEngine
from core.plugin_loader import plugin_loader
from core.tool_registry import ToolRegistry
from schemas.artifacts import JuniorDraft
from schemas.case import CaseIntake
from schemas.documents import DocumentIndex
from schemas.plugins import AgentHandoff

from . import prompts
from . import tools as agent_tools


class JuniorAnalyst:
    """Junior Analyst — researches and produces initial draft for PM review."""

    def __init__(
        self,
        registry: ToolRegistry,
        hook_engine: HookEngine,
        document_manager=None,
        workflow: str = "investigation_report",
    ):
        manifest = plugin_loader.load("junior_analyst")
        agent_manifest = manifest.to_agent_manifest()

        # Register tools if not already registered
        if "search_web" not in registry.list_tools():
            agent_tools.register_tools(registry, document_manager)

        self._agent = BaseAgent(
            manifest=agent_manifest,
            registry=registry,
            hook_engine=hook_engine,
            tool_definitions=agent_tools.get_tool_definitions(document_manager),
            workflow=workflow,
        )
        self._manifest = manifest
        self._workflow = workflow
        self._doc_manager = document_manager

    def __call__(self, intake: dict, context: dict) -> AgentHandoff:
        """Run Junior Analyst. Returns AgentHandoff TypedDict."""
        intake_obj = CaseIntake(**intake) if not isinstance(intake, CaseIntake) else intake

        # Load document index if available
        doc_index: DocumentIndex | None = None
        if self._doc_manager:
            try:
                doc_index = self._doc_manager.get_index()
            except Exception:
                pass

        revision_feedback = context.get("pm_feedback") or context.get("revision_feedback")
        firm_name = context.get("firm_name", "GoodWork Forensic Consulting")
        system_prompt = prompts.build_system_prompt(
            self._workflow, intake_obj, doc_index, revision_feedback, firm_name=firm_name
        )
        task_message = prompts.build_task_message(intake_obj)

        result = self._agent.run(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": task_message}],
            context=context,
            require_citations=True,
        )

        # Parse JSON from response
        output = self._parse_output(result["text"], intake_obj, context)

        # Run post-hooks
        hook_context = {
            **context,
            "agent": self._manifest.role,
            "artifact_type": self._manifest.artifact_type,
            "schema_cls": JuniorDraft,
            "workflow": self._workflow,
            "role": self._manifest.role,
        }
        self._agent.hook_engine.run_post({"output": output}, hook_context)

        return AgentHandoff(
            output=output,
            revision_requested=False,
            revision_reason=None,
            agent=self._manifest.role,
            workflow=self._workflow,
            turn_count=len(result["tool_calls"]),
            tool_calls_made=[tc["tool"] for tc in result["tool_calls"]],
        )

    def _parse_output(self, text: str, intake: CaseIntake, context: dict) -> dict:
        """Extract JSON output from response text.

        Tries in order:
        1. ```json ... ``` code block (model commonly wraps output this way)
        2. Greedy {.*} regex
        Fallback: minimal skeleton with summary text preserved.
        """
        import re

        def _try_parse(candidate: str) -> dict | None:
            try:
                data = json.loads(candidate)
                if isinstance(data, dict):
                    data["case_id"] = intake.case_id
                    data.setdefault("version", context.get("revision_round", 0) + 1)
                    data.setdefault("revision_round", context.get("revision_round", 0))
                    return data
            except json.JSONDecodeError:
                pass
            return None

        # 1. Code block: ```json ... ``` or ``` ... ```
        code_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if code_block:
            result = _try_parse(code_block.group(1))
            if result:
                return result

        # 2. Greedy {.*} — last resort
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            result = _try_parse(match.group())
            if result:
                return result

        # Fallback: preserve summary text so the run is not a total loss
        return {
            "case_id": intake.case_id,
            "version": 1,
            "summary": text[:500],
            "findings": [],
            "methodology": "See summary",
            "regulatory_implications": "",
            "recommendations": [],
            "open_questions": [],
            "citations": [],
            "revision_round": context.get("revision_round", 0),
        }
