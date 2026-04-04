"""Project Manager agent — reviews Junior draft, approves or requests revision."""

from __future__ import annotations

import json

from core.agent_base import BaseAgent
from core.hook_engine import HookEngine
from core.plugin_loader import plugin_loader
from core.tool_registry import ToolRegistry
from schemas.case import CaseIntake
from schemas.plugins import AgentHandoff

from . import prompts
from . import tools as agent_tools


class ProjectManager:
    """Project Manager — reviews draft, decides approve or revise."""

    def __init__(
        self,
        registry: ToolRegistry,
        hook_engine: HookEngine,
        document_manager=None,
        workflow: str = "investigation_report",
    ):
        manifest = plugin_loader.load("project_manager")
        agent_manifest = manifest.to_agent_manifest()

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

    def __call__(self, junior_output: dict, context: dict) -> AgentHandoff:
        """Review Junior output. Returns AgentHandoff with revision_requested flag."""
        # Build intake from context if available
        intake_dict = context.get("intake", {})
        intake = CaseIntake(**intake_dict) if intake_dict else _minimal_intake(context)

        system_prompt = prompts.build_system_prompt(self._workflow, intake)
        task_message  = prompts.build_task_message(junior_output)

        result = self._agent.run(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": task_message}],
            context=context,
        )

        output = self._parse_output(result["text"])

        # Persist via post-hooks
        hook_context = {
            **context,
            "agent": self._manifest.role,
            "artifact_type": self._manifest.artifact_type,
            "workflow": self._workflow,
            "role": self._manifest.role,
        }
        self._agent.hook_engine.run_post({"output": output}, hook_context)

        revision_requested = output.get("revision_requested", False)
        feedback = output.get("feedback_to_junior", "")

        return AgentHandoff(
            output=output,
            revision_requested=revision_requested,
            revision_reason=feedback if revision_requested else None,
            agent=self._manifest.role,
            workflow=self._workflow,
            turn_count=len(result["tool_calls"]),
            tool_calls_made=[tc["tool"] for tc in result["tool_calls"]],
        )

    def _parse_output(self, text: str) -> dict:
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {
            "revision_requested": False,
            "review_summary": text[:500],
            "findings": [],
            "must_fix": [],
            "should_fix": [],
            "missing_citations": [],
            "feedback_to_junior": "",
        }


def _minimal_intake(context: dict) -> CaseIntake:
    """Create minimal CaseIntake from context dict for PM prompts."""
    from datetime import datetime, timezone
    return CaseIntake(
        case_id=context.get("case_id", "unknown"),
        client_name=context.get("client_name", "Client"),
        industry=context.get("industry", "Unknown"),
        workflow=context.get("workflow", "unknown"),
        description=context.get("description", ""),
        created_at=datetime.now(timezone.utc),
    )
