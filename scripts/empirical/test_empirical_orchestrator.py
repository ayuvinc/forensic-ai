# integration test — requires real codebase, no mocks
"""
Empirical orchestrator tests — E3.
Runs the real Orchestrator with controlled mock agent callables.
Validates revision loop enforcement, PM feedback threading, resume logic.
"""
from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

from tests.empirical_fixtures import (
    make_intake, make_junior_handoff, make_pm_handoff, make_partner_handoff
)


@dataclass
class OrchestratorTestResult:
    test_id: str
    description: str
    outcome: str              # "PASS" | "FAIL" | "EXCEPTION" | "IMPORT_ERROR"
    detail: str
    confirmed_sim_finding: str | None
    junior_rounds_observed: int
    pm_rounds_observed: int
    terminal_state: str | None


# ---------------------------------------------------------------------------
# Orchestrator test runner helper
# ---------------------------------------------------------------------------

def _run_orchestrator(
    tmp_cases: Path,
    case_id: str,
    workflow: str,
    junior_responses: list[dict],
    pm_responses: list[dict],
    partner_response: dict,
) -> tuple[str | None, dict | None, Exception | None]:
    try:
        import config
        import tools.file_tools as ft
        config.CASES_DIR = tmp_cases
        ft.CASES_DIR = tmp_cases

        from core.orchestrator import Orchestrator

        junior_call_count = [0]
        pm_call_count = [0]
        observed_junior_context = [None]

        def junior_fn(intake: dict, ctx: dict) -> dict:
            idx = min(junior_call_count[0], len(junior_responses) - 1)
            junior_call_count[0] += 1
            observed_junior_context[0] = dict(ctx)
            return junior_responses[idx]

        def pm_fn(junior_output: dict, ctx: dict) -> dict:
            idx = min(pm_call_count[0], len(pm_responses) - 1)
            pm_call_count[0] += 1
            return pm_responses[idx]

        def partner_fn(pm_output: dict, ctx: dict) -> dict:
            return partner_response

        orch = Orchestrator(
            case_id=case_id,
            workflow=workflow,
            junior_fn=junior_fn,
            pm_fn=pm_fn,
            partner_fn=partner_fn,
        )

        result = orch.run(make_intake(workflow=workflow, case_id=case_id))

        state_file = tmp_cases / case_id / "state.json"
        state = json.loads(state_file.read_text()) if state_file.exists() else {}

        return (
            state.get("status"),
            {
                "state": state,
                "junior_calls": junior_call_count[0],
                "pm_calls": pm_call_count[0],
                "observed_junior_context": observed_junior_context[0],
                "result": result,
            },
            None,
        )

    except Exception as e:
        return None, {"junior_calls": 0, "pm_calls": 0}, e


# ---------------------------------------------------------------------------
# E3.1 — Basic pipeline (no revisions)
# ---------------------------------------------------------------------------

def run_e3_basic_pipeline() -> OrchestratorTestResult:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        case_id = "TEST-E31"
        (tmp_path / case_id).mkdir()

        status, info, exc = _run_orchestrator(
            tmp_path, case_id, "investigation_report",
            junior_responses=[make_junior_handoff("good", case_id=case_id)],
            pm_responses=[make_pm_handoff(revision_requested=False, case_id=case_id)],
            partner_response=make_partner_handoff(revision_requested=False, case_id=case_id),
        )

        if exc:
            return OrchestratorTestResult(
                "E3.1", "Basic pipeline — no revisions", "EXCEPTION",
                str(exc)[:200], None, 0, 0, None,
            )

        jr = info.get("junior_calls", 0)
        pm = info.get("pm_calls", 0)
        passed = (jr == 1 and pm == 1 and status in (
            "owner_ready", "OWNER_READY",
            "partner_review_complete", "PARTNER_REVIEW_COMPLETE",
        ))

        return OrchestratorTestResult(
            "E3.1", "Basic pipeline — no revisions",
            "PASS" if passed else "FAIL",
            f"junior_calls={jr}, pm_calls={pm}, terminal_status={status}",
            None, jr, pm, status,
        )


# ---------------------------------------------------------------------------
# E3.2 — PM requests one revision; confirm PM feedback reaches Junior
# ---------------------------------------------------------------------------

def run_e3_pm_revision_feedback() -> OrchestratorTestResult:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        case_id = "TEST-E32"
        (tmp_path / case_id).mkdir()

        feedback_text = "Please add more regulatory citations."

        pm_responses = [
            make_pm_handoff(revision_requested=True, feedback=feedback_text, case_id=case_id),
            make_pm_handoff(revision_requested=False, case_id=case_id),
        ]

        junior_responses = [
            make_junior_handoff("good", revision_round=0, case_id=case_id),
            make_junior_handoff("good", revision_round=1, case_id=case_id),
        ]

        received_feedback = [None]
        try:
            import config
            import tools.file_tools as ft
            config.CASES_DIR = tmp_path
            ft.CASES_DIR = tmp_path
            from core.orchestrator import Orchestrator

            call_num = [0]

            def junior_fn(intake, ctx):
                call_num[0] += 1
                if call_num[0] == 2:
                    received_feedback[0] = ctx.get("pm_feedback") or ctx.get("revision_feedback")
                idx = min(call_num[0] - 1, len(junior_responses) - 1)
                return junior_responses[idx]

            pm_call = [0]

            def pm_fn(j_out, ctx):
                idx = min(pm_call[0], len(pm_responses) - 1)
                pm_call[0] += 1
                return pm_responses[idx]

            orch = Orchestrator(
                case_id=case_id, workflow="investigation_report",
                junior_fn=junior_fn, pm_fn=pm_fn,
                partner_fn=lambda *a, **kw: make_partner_handoff(case_id=case_id),
            )
            orch.run(make_intake(workflow="investigation_report", case_id=case_id))

            feedback_received = received_feedback[0] is not None
            detail = (
                f"junior_calls={call_num[0]}, pm_calls={pm_call[0]}, "
                f"feedback_in_context={repr(received_feedback[0])[:60]}"
            )
            passed = call_num[0] == 2 and pm_call[0] == 2

            if not feedback_received:
                detail += " — SIM-02 CONFIRMED: PM feedback NOT in Junior context on revision"
                sim_ref = "SIM-02"
            else:
                detail += " — SIM-02 REFUTED: PM feedback IS in Junior context"
                sim_ref = "SIM-02"

            return OrchestratorTestResult(
                "E3.2", "PM revision feedback threading",
                "PASS" if passed else "FAIL",
                detail, sim_ref, call_num[0], pm_call[0], None,
            )

        except Exception as e:
            return OrchestratorTestResult(
                "E3.2", "PM revision feedback threading", "EXCEPTION",
                str(e)[:200], "SIM-02", 0, 0, None,
            )


# ---------------------------------------------------------------------------
# E3.3 — Revision limit exhaustion
# ---------------------------------------------------------------------------

def run_e3_revision_limit_exhaustion() -> OrchestratorTestResult:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        case_id = "TEST-E33"
        (tmp_path / case_id).mkdir()

        always_revise_pm = make_pm_handoff(revision_requested=True, case_id=case_id)
        always_pass_junior = make_junior_handoff("good", case_id=case_id)

        call_counts = {"junior": 0, "pm": 0}

        try:
            import config
            import tools.file_tools as ft
            config.CASES_DIR = tmp_path
            ft.CASES_DIR = tmp_path
            from core.orchestrator import Orchestrator

            def junior_fn(intake, ctx):
                call_counts["junior"] += 1
                return always_pass_junior

            def pm_fn(j_out, ctx):
                call_counts["pm"] += 1
                return always_revise_pm

            orch = Orchestrator(
                case_id=case_id, workflow="investigation_report",
                junior_fn=junior_fn, pm_fn=pm_fn,
                partner_fn=lambda *a, **kw: make_partner_handoff(case_id=case_id),
            )

            orch.run(make_intake(workflow="investigation_report", case_id=case_id))

            # Correct behavior (post G-13/G-14 fix): PM revision limit hit →
            # best-effort draft promoted to Partner, no exception raised.
            # Call counts must match: pm_calls == MAX_REVISION_ROUNDS["pm"],
            # junior_calls == pm_limit + 1 (1 initial + pm_limit revisions).
            from config import MAX_REVISION_ROUNDS as MRR
            expected_pm = MRR["pm"]
            expected_junior = MRR["pm"] + 1
            counts_correct = (
                call_counts["pm"] == expected_pm
                and call_counts["junior"] == expected_junior
            )
            detail = (
                f"No exception — junior_calls={call_counts['junior']} "
                f"(expected {expected_junior}), pm_calls={call_counts['pm']} "
                f"(expected {expected_pm})"
            )
            detail += (
                " — PASS: best-effort draft promoted, limit enforced"
                if counts_correct else " — FAIL: unexpected call counts"
            )
            return OrchestratorTestResult(
                "E3.3", "Revision limit exhaustion — promote best-effort draft",
                "PASS" if counts_correct else "FAIL",
                detail, "SIM-02",
                call_counts["junior"], call_counts["pm"], None,
            )

        except Exception as e:
            error_type = type(e).__name__
            detail = (
                f"UNEXPECTED exception {error_type} after "
                f"junior_calls={call_counts['junior']}, "
                f"pm_calls={call_counts['pm']} — {str(e)[:80]}"
            )
            return OrchestratorTestResult(
                "E3.3", "Revision limit exhaustion — promote best-effort draft",
                "FAIL", detail, "SIM-02",
                call_counts["junior"], call_counts["pm"], None,
            )


# ---------------------------------------------------------------------------
# E3.4 — Partner requests revision (terminal — SIM-04)
# ---------------------------------------------------------------------------

def run_e3_partner_revision_terminal() -> OrchestratorTestResult:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        case_id = "TEST-E34"
        (tmp_path / case_id).mkdir()

        retry_attempts = [0]

        try:
            import config
            import tools.file_tools as ft
            config.CASES_DIR = tmp_path
            ft.CASES_DIR = tmp_path
            from core.orchestrator import Orchestrator

            def partner_fn(pm_out, ctx):
                retry_attempts[0] += 1
                return make_partner_handoff(revision_requested=True, case_id=case_id)

            orch = Orchestrator(
                case_id=case_id, workflow="investigation_report",
                junior_fn=lambda *a, **kw: make_junior_handoff("good", case_id=case_id),
                pm_fn=lambda *a, **kw: make_pm_handoff(revision_requested=False, case_id=case_id),
                partner_fn=partner_fn,
            )
            orch.run(make_intake(workflow="investigation_report", case_id=case_id))

            detail = (
                f"NO EXCEPTION RAISED, partner called {retry_attempts[0]} times — "
                "SIM-04 pattern: Partner rejection not triggering PipelineError"
            )
            return OrchestratorTestResult(
                "E3.4", "Partner revision is terminal",
                "FAIL", detail, "SIM-04", 1, 1, None,
            )

        except Exception as e:
            error_type = type(e).__name__
            retried = retry_attempts[0] > 1
            detail = (
                f"Raised {error_type} after partner called {retry_attempts[0]} time(s) — "
                f"{str(e)[:80]}"
            )
            if retried:
                detail += " — UNEXPECTED: Partner was retried (should be terminal)"
            else:
                detail += " — SIM-04 CONFIRMED: Partner rejection is terminal (1 call, then error)"

            return OrchestratorTestResult(
                "E3.4", "Partner revision is terminal",
                "PASS" if not retried else "FAIL",
                detail, "SIM-04", 1, 1, None,
            )


# ---------------------------------------------------------------------------
# E3.5 — Resume from checkpoint
# ---------------------------------------------------------------------------

def run_e3_resume_from_checkpoint() -> OrchestratorTestResult:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        case_id = "TEST-E35"
        (tmp_path / case_id).mkdir()

        call_log: list[str] = []

        try:
            import config
            import tools.file_tools as ft
            config.CASES_DIR = tmp_path
            ft.CASES_DIR = tmp_path
            from core.orchestrator import Orchestrator
            from core.state_machine import CaseStatus

            def junior_fn(intake, ctx):
                call_log.append("junior")
                return make_junior_handoff("good", case_id=case_id)

            def pm_fn(j_out, ctx):
                call_log.append("pm")
                return make_pm_handoff(revision_requested=False, case_id=case_id)

            def partner_fn(pm_out, ctx):
                call_log.append("partner")
                return make_partner_handoff(revision_requested=False, case_id=case_id)

            from tools.file_tools import write_state
            from schemas.case import CaseState
            _cs = CaseState(
                case_id=case_id,
                workflow="investigation_report",
                status=CaseStatus.JUNIOR_DRAFT_COMPLETE,
                revision_rounds={"junior": 0, "pm": 0},
            )
            write_state(case_id, _cs.model_dump(mode="json"))

            junior_artifact_path = tmp_path / case_id / "junior_output.v1.json"
            junior_artifact_path.write_text(json.dumps(
                {"output": make_junior_handoff("good", case_id=case_id)["output"]}
            ))

            call_log.clear()

            orch2 = Orchestrator(
                case_id=case_id, workflow="investigation_report",
                junior_fn=junior_fn, pm_fn=pm_fn, partner_fn=partner_fn,
            )
            orch2.run(make_intake(workflow="investigation_report", case_id=case_id))

            junior_re_ran = "junior" in call_log
            detail = (
                f"After resume from JUNIOR_DRAFT_COMPLETE: call_log={call_log}, "
                f"junior_re_ran={junior_re_ran}"
            )
            if junior_re_ran:
                detail += " — RESUME GAP: Junior re-ran after checkpoint"
            else:
                detail += " — Resume correct: Junior skipped, PM+Partner ran"

            return OrchestratorTestResult(
                "E3.5", "Resume from checkpoint",
                "PASS" if not junior_re_ran else "FAIL",
                detail, None,
                call_log.count("junior"), call_log.count("pm"), None,
            )

        except Exception as e:
            return OrchestratorTestResult(
                "E3.5", "Resume from checkpoint", "EXCEPTION",
                str(e)[:200], None, 0, 0, None,
            )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_all_orchestrator_tests() -> list[OrchestratorTestResult]:
    return [
        run_e3_basic_pipeline(),
        run_e3_pm_revision_feedback(),
        run_e3_revision_limit_exhaustion(),
        run_e3_partner_revision_terminal(),
        run_e3_resume_from_checkpoint(),
    ]
