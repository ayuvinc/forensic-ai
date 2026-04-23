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

        revision_feedback          = context.get("pm_feedback") or context.get("revision_feedback")
        firm_name                  = context.get("firm_name", "GoodWork Forensic Consulting")
        language_standard          = context.get("language_standard", "acfe")
        recommendation_instruction = context.get("recommendation_instruction")  # FR-06
        stakeholder_context        = context.get("stakeholder_context") or None  # FR-02
        firm_knowledge_context     = context.get("firm_knowledge_context", "")   # KB-03
        system_prompt = prompts.build_system_prompt(
            self._workflow, intake_obj, doc_index, revision_feedback,
            firm_name=firm_name, language_standard=language_standard,
            recommendation_instruction=recommendation_instruction,
            stakeholder_context=stakeholder_context,
            firm_knowledge_context=firm_knowledge_context,
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

        _VALID_CONFIDENCE = {"high", "medium", "low"}

        def _normalize_citations(data: dict) -> dict:
            for c in data.get("citations", []):
                if isinstance(c, dict):
                    conf = str(c.get("confidence", "medium")).lower()
                    if conf not in _VALID_CONFIDENCE:
                        c["confidence"] = "high" if "high" in conf else "low" if "low" in conf else "medium"
            return data

        def _try_parse(candidate: str) -> dict | None:
            try:
                data = json.loads(candidate)
                if isinstance(data, dict):
                    data["case_id"] = intake.case_id
                    data.setdefault("version", context.get("revision_round", 0) + 1)
                    data.setdefault("revision_round", context.get("revision_round", 0))
                    return _normalize_citations(data)
            except json.JSONDecodeError:
                pass
            return None

        # 1. Code block: extract everything between ``` fences, then find outermost { }
        code_block = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if code_block:
            block_content = code_block.group(1)
            # Find outermost { } within the code block (greedy inside fence)
            inner = re.search(r'\{[\s\S]*\}', block_content)
            if inner:
                result = _try_parse(inner.group())
                if result:
                    return result

        # 2. Greedy {.*} across entire response — last resort
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            result = _try_parse(match.group())
            if result:
                return result

        # Fallback: preserve summary text so the run is not a total loss
        return _normalize_citations({
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
        })
