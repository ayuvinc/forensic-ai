"""Partner agent — final quality gate before client delivery."""

from __future__ import annotations

import json
import logging

import config

from core.agent_base import BaseAgent
from core.hook_engine import HookEngine
from core.plugin_loader import plugin_loader
from core.tool_registry import ToolRegistry
from schemas.case import CaseIntake
from schemas.plugins import AgentHandoff

from . import prompts
from . import tools as agent_tools

logger = logging.getLogger(__name__)

# Workflows that require evidence-chain validation before approval
_EVIDENCE_CHAIN_WORKFLOWS = frozenset(["investigation_report", "expert_witness_report"])


class Partner:
    """Partner — final approval decision. Validates evidence permissibility."""

    def __init__(
        self,
        registry: ToolRegistry,
        hook_engine: HookEngine,
        document_manager=None,
        workflow: str = "investigation_report",
    ):
        manifest = plugin_loader.load("partner")
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

    def __call__(self, pm_output: dict, context: dict) -> AgentHandoff:
        """Review PM-approved draft. Returns AgentHandoff with approval decision."""
        intake_dict = context.get("intake", {})
        intake = CaseIntake(**intake_dict) if intake_dict else _minimal_intake(context)

        junior_output = context.get("junior_output")

        language_standard = context.get("language_standard", "acfe")
        system_prompt = prompts.build_system_prompt(
            self._workflow, intake,
            research_mode=config.RESEARCH_MODE,
            language_standard=language_standard,
        )
        task_message  = prompts.build_task_message(pm_output, junior_output, research_mode=config.RESEARCH_MODE)

        result = self._agent.run(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": task_message}],
            context=context,
            require_citations=(self._workflow != "client_proposal"),
        )

        output = self._parse_output(result["text"])

        # C-03a: Evidence-chain validation before allowing approval
        if self._workflow in _EVIDENCE_CHAIN_WORKFLOWS:
            output = self._enforce_evidence_chains(output, context)

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

        return AgentHandoff(
            output=output,
            revision_requested=revision_requested,
            revision_reason=output.get("revision_reason") if revision_requested else None,
            agent=self._manifest.role,
            workflow=self._workflow,
            turn_count=len(result["tool_calls"]),
            tool_calls_made=[tc["tool"] for tc in result["tool_calls"]],
        )

    def _enforce_evidence_chains(self, output: dict, context: dict) -> dict:
        """Validate finding chains against evidence items. Override approval if any chain fails.

        No-op when evidence_items or finding_chains are absent (non-document cases).
        """
        evidence_items = context.get("evidence_items", [])
        finding_chains_raw = output.get("finding_chains", [])

        if not evidence_items or not finding_chains_raw:
            return output

        from tools.evidence.evidence_classifier import EvidenceClassifier
        from schemas.evidence import FindingChain, EvidenceItem

        classifier = EvidenceClassifier()

        # Deserialise if raw dicts
        chains = []
        for fc in finding_chains_raw:
            if isinstance(fc, FindingChain):
                chains.append(fc)
            elif isinstance(fc, dict):
                try:
                    chains.append(FindingChain(**fc))
                except Exception:
                    continue

        items = []
        for ei in evidence_items:
            if isinstance(ei, EvidenceItem):
                items.append(ei)
            elif isinstance(ei, dict):
                try:
                    items.append(EvidenceItem(**ei))
                except Exception:
                    continue

        if not chains or not items:
            return output

        failed_ids = []
        for chain in chains:
            if not classifier.validate_finding_chain(chain, items):
                failed_ids.append(chain.finding_id)

        if failed_ids and output.get("approved", False):
            logger.warning(
                "Evidence chain validation failed for findings: %s — overriding approval",
                failed_ids,
            )
            output["approved"] = False
            output["revision_requested"] = True
            output["revision_reason"] = (
                f"Evidence chain validation failed: finding(s) {failed_ids} reference "
                "LEAD_ONLY or INADMISSIBLE evidence. Revise findings to use only PERMISSIBLE evidence."
            )

        return output

    def _parse_output(self, text: str) -> dict:
        import re

        def _try_json(s: str):
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                return None

        # 1. Code block fence: extract content between ``` markers first
        code_block = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if code_block:
            inner = re.search(r'\{[\s\S]*\}', code_block.group(1))
            if inner:
                result = _try_json(inner.group())
                if result is not None:
                    return result

        # 2. Greedy outermost { } across full response
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            result = _try_json(match.group())
            if result is not None:
                return result
        return {
            "approving_agent": "partner",
            "approved": False,
            "conditions": ["Parse error — manual review required"],
            "regulatory_sign_off": "",
            "escalation_required": False,
            "escalation_reason": None,
            "review_notes": text[:500],
            "revision_requested": False,
            "revision_reason": None,
        }


def _minimal_intake(context: dict) -> CaseIntake:
    from datetime import datetime, timezone
    return CaseIntake(
        case_id=context.get("case_id", "unknown"),
        client_name=context.get("client_name", "Client"),
        industry=context.get("industry", "Unknown"),
        workflow=context.get("workflow", "unknown"),
        description=context.get("description", ""),
        created_at=datetime.now(timezone.utc),
    )
