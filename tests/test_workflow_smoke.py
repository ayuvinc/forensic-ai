"""Workflow smoke tests (TEST-07).

Verifies workflow entry-points with fully mocked LLM calls — no API key required.
Each test patches anthropic.Anthropic (or the relevant agent callables) so no network
I/O occurs. Confirms the happy path returns the expected type.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from schemas.case import CaseIntake


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def intake(sample_case_id) -> CaseIntake:
    return CaseIntake(
        case_id=sample_case_id,
        client_name="Smoke Test Corp",
        industry="financial_services",
        primary_jurisdiction="UAE",
        operating_jurisdictions=["UAE"],
        workflow="test_workflow",
        description="Smoke test engagement",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def mock_registry():
    reg = MagicMock()
    reg.list_tools.return_value = []
    return reg


@pytest.fixture
def mock_hook_engine():
    engine = MagicMock()
    engine.run_pre_hooks.side_effect = lambda payload, ctx: payload
    engine.run_post_hooks.side_effect = lambda payload, ctx: payload
    return engine


def _stub_anthropic(text: str):
    """Return a mock anthropic module whose Anthropic() returns a client with text."""
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    msg.stop_reason = "end_turn"
    client = MagicMock()
    client.messages.create.return_value = msg
    mock_module = MagicMock()
    mock_module.Anthropic.return_value = client
    return mock_module


# ── Engagement Scoping smoke ───────────────────────────────────────────────────

class TestEngagementScopingSmoke:
    def test_headless_returns_confirmed_scope(self, patched_cases_dir, intake):
        """run_engagement_scoping_workflow returns ConfirmedScope in headless mode."""
        from schemas.engagement_scope import ConfirmedScope

        scope_json = json.dumps({
            "engagement_types": ["investigation_report"],
            "primary_engagement": "investigation_report",
            "scope_components": ["financial transaction analysis"],
            "deliverables": ["Investigation Report"],
            "sequencing": ["Phase 1: Fieldwork"],
            "caveats": [],
            "chaining_suggestion": None,
            "rationale": "Asset misappropriation investigation required.",
        })
        # Also need _generate_scope_document to call LLM — patch with same stub
        scope_doc_text = "# Scope Document\n\nSmoke test scope."

        call_count = [0]
        def _side_effect(*args, **kwargs):
            call_count[0] += 1
            msg = MagicMock()
            # First call: _propose_scope returns scope JSON
            # Subsequent calls (_generate_scope_document): return plain text
            msg.content = [MagicMock(text=scope_json if call_count[0] == 1 else scope_doc_text)]
            msg.stop_reason = "end_turn"
            return msg

        client_mock = MagicMock()
        client_mock.messages.create.side_effect = _side_effect

        with patch("anthropic.Anthropic", return_value=client_mock):
            from workflows.engagement_scoping import run_engagement_scoping_workflow
            result = run_engagement_scoping_workflow(
                intake,
                on_progress=lambda _: None,
                headless_params={
                    "situation": "Suspected cash theft",
                    "trigger": "Internal audit finding",
                    "desired_outcome": "Investigation report",
                    "constraints": "",
                    "red_flags": "",
                },
            )

        assert isinstance(result, ConfirmedScope)
        assert result.confirmed is True


# ── Due Diligence smoke ────────────────────────────────────────────────────────

class TestDueDiligenceSmoke:
    def test_individual_headless_returns_deliverable(
        self, patched_cases_dir, intake, mock_registry, mock_hook_engine
    ):
        """run_due_diligence_workflow (individual, headless) returns FinalDeliverable."""
        from schemas.artifacts import FinalDeliverable

        dd_report_text = "# Due Diligence Report\n\nNo adverse findings identified."

        client_mock = MagicMock()
        msg = MagicMock()
        msg.content = [MagicMock(text=dd_report_text)]
        msg.stop_reason = "end_turn"
        client_mock.messages.create.return_value = msg

        with patch("anthropic.Anthropic", return_value=client_mock):
            from workflows.due_diligence import run_due_diligence_workflow
            result = run_due_diligence_workflow(
                intake,
                mock_registry,
                mock_hook_engine,
                on_progress=lambda _: None,
                headless_params={
                    "subject_type": "individual",
                    "subject_name": "Jane Doe",
                    "screening_level": "standard_phase1",
                    "dob": "1980-01-01",
                    "place_of_birth": "Dubai",
                    "nationalities": ["UAE"],
                    "dd_purpose": "onboarding",
                },
            )

        assert isinstance(result, FinalDeliverable)
        assert result.workflow == "due_diligence"


# ── FRM pipeline smoke ─────────────────────────────────────────────────────────

class TestFRMPipelineSmoke:
    def test_single_module_returns_risk_items(
        self, patched_cases_dir, intake, mock_registry, mock_hook_engine
    ):
        """run_frm_pipeline with mocked agents returns (risk_items, citations, modules, summary)."""
        from schemas.plugins import AgentHandoff

        stub_junior_output = {
            "case_id": intake.case_id,
            "version": 1,
            "summary": "Module 2 assessment complete.",
            "findings": [
                {
                    "title": "Petty cash risk",
                    "description": "Petty cash controls are weak.",
                    "evidence": "No reconciliation logs found.",
                    "risk_level": "high",
                },
            ],
            "methodology": "Document review",
            "regulatory_implications": "COSO 2013",
            "recommendations": ["Implement petty cash reconciliation"],
            "open_questions": [],
            "citations": [],
            "revision_round": 0,
        }

        stub_handoff: AgentHandoff = {
            "output": stub_junior_output,
            "revision_requested": False,
            "revision_reason": None,
            "agent": "junior",
            "workflow": "frm_risk_register",
            "turn_count": 1,
            "tool_calls_made": [],
        }

        pm_handoff: AgentHandoff = {**stub_handoff, "agent": "pm"}
        partner_handoff: AgentHandoff = {**stub_handoff, "agent": "partner"}

        exec_summary_text = "Executive summary: 1 risk identified."

        client_mock = MagicMock()
        msg = MagicMock()
        msg.content = [MagicMock(text=exec_summary_text)]
        msg.stop_reason = "end_turn"
        client_mock.messages.create.return_value = msg

        with (
            patch("agents.junior_analyst.agent.JuniorAnalyst") as MockJunior,
            patch("agents.project_manager.agent.ProjectManager") as MockPM,
            patch("agents.partner.agent.Partner") as MockPartner,
            patch("anthropic.Anthropic", return_value=client_mock),
        ):
            MockJunior.return_value.side_effect = lambda *a, **kw: stub_handoff
            MockPM.return_value.side_effect = lambda *a, **kw: pm_handoff
            MockPartner.return_value.side_effect = lambda *a, **kw: partner_handoff

            from workflows.frm_risk_register import run_frm_pipeline
            risk_items, citations, completed_modules, exec_summary = run_frm_pipeline(
                intake,
                selected_modules=[2],
                registry=mock_registry,
                hook_engine=mock_hook_engine,
                on_progress=lambda _: None,
            )

        assert len(risk_items) >= 1
        assert 2 in completed_modules
        assert isinstance(exec_summary, str)
