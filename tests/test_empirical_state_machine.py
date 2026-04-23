# integration test — requires real codebase, no mocks
"""
Empirical state machine tests — E4.
Runs real transition() and is_terminal() against all edge cases.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SMTestResult:
    test_id: str
    description: str
    outcome: str        # "PASS" | "FAIL" | "IMPORT_ERROR"
    detail: str
    confirmed_sim_finding: str | None


def run_all_state_machine_tests() -> list[SMTestResult]:
    results = []

    try:
        from core.state_machine import (
            CaseStatus, VALID_TRANSITIONS, TERMINAL_STATUSES, transition, is_terminal
        )
    except ImportError as e:
        return [SMTestResult("E4-import", "import", "IMPORT_ERROR", str(e), "SIM-17")]

    # E4.1 — All valid transitions succeed
    for src, targets in VALID_TRANSITIONS.items():
        for tgt in targets:
            try:
                result = transition(src, tgt)
                passed = result == tgt
                results.append(SMTestResult(
                    f"E4.1-{src.value}->{tgt.value}",
                    f"Valid transition {src.value}→{tgt.value}",
                    "PASS" if passed else "FAIL",
                    f"returned {result}",
                    None,
                ))
            except Exception as e:
                results.append(SMTestResult(
                    f"E4.1-{src.value}->{tgt.value}",
                    f"Valid transition {src.value}→{tgt.value}",
                    "FAIL",
                    f"Unexpected exception: {e}",
                    None,
                ))

    # E4.2 — Invalid transitions raise InvalidTransitionError
    invalid_cases = [
        (CaseStatus.INTAKE_CREATED, CaseStatus.PARTNER_REVIEW_COMPLETE),
        (CaseStatus.JUNIOR_DRAFT_COMPLETE, CaseStatus.OWNER_APPROVED),
        (CaseStatus.PM_REVIEW_COMPLETE, CaseStatus.INTAKE_CREATED),
        (CaseStatus.PARTNER_REVIEW_COMPLETE, CaseStatus.JUNIOR_DRAFT_COMPLETE),
        (CaseStatus.INTAKE_CREATED, CaseStatus.INTAKE_CREATED),
        (CaseStatus.OWNER_APPROVED, CaseStatus.OWNER_APPROVED),
        (CaseStatus.OWNER_APPROVED, CaseStatus.INTAKE_CREATED),
    ]

    for src, tgt in invalid_cases:
        try:
            transition(src, tgt)
            results.append(SMTestResult(
                f"E4.2-{src.value}->{tgt.value}",
                f"Invalid transition {src.value}→{tgt.value}",
                "FAIL",
                "No exception raised — invalid transition accepted",
                None,
            ))
        except Exception as e:
            error_type = type(e).__name__
            expected = "InvalidTransitionError" in error_type or "ValueError" in error_type
            results.append(SMTestResult(
                f"E4.2-{src.value}->{tgt.value}",
                f"Invalid transition {src.value}→{tgt.value}",
                "PASS" if expected else "FAIL",
                f"Raised {error_type}: {str(e)[:80]}",
                None,
            ))

    # E4.3 — PIPELINE_ERROR reachability (SIM-17)
    pipeline_error_reachable_via_transition = False
    for src, targets in VALID_TRANSITIONS.items():
        if CaseStatus.PIPELINE_ERROR in targets:
            pipeline_error_reachable_via_transition = True
            break

    pipeline_error_is_terminal = CaseStatus.PIPELINE_ERROR in TERMINAL_STATUSES

    results.append(SMTestResult(
        "E4.3-pipeline_error_reachability",
        "PIPELINE_ERROR reachable via transition()",
        "INFO",
        (
            f"reachable_via_transition={pipeline_error_reachable_via_transition}, "
            f"in_TERMINAL_STATUSES={pipeline_error_is_terminal}. "
            + ("SIM-17 CONFIRMED: orchestrator sets PIPELINE_ERROR directly, bypassing transition(). "
               "This is intentional but means is_terminal() must be checked separately."
               if not pipeline_error_reachable_via_transition else
               "SIM-17 REFUTED: PIPELINE_ERROR is reachable via standard transitions.")
        ),
        "SIM-17",
    ))

    # E4.4 — OWNER_REJECTED recovery path
    try:
        s1 = transition(CaseStatus.OWNER_READY, CaseStatus.OWNER_REJECTED)
        s2 = transition(CaseStatus.OWNER_REJECTED, CaseStatus.JUNIOR_DRAFT_COMPLETE)
        results.append(SMTestResult(
            "E4.4-rejected_recovery",
            "OWNER_REJECTED → JUNIOR_DRAFT_COMPLETE recovery",
            "PASS",
            f"Full path OK: OWNER_READY→{s1.value}→{s2.value}",
            None,
        ))
    except Exception as e:
        results.append(SMTestResult(
            "E4.4-rejected_recovery",
            "OWNER_REJECTED → JUNIOR_DRAFT_COMPLETE recovery",
            "FAIL",
            f"Recovery path blocked: {e}",
            None,
        ))

    # E4.5 — is_terminal() for all states
    terminal_check_failures = []
    for status in CaseStatus:
        expected_terminal = status in TERMINAL_STATUSES
        actual_terminal = is_terminal(status)
        if expected_terminal != actual_terminal:
            terminal_check_failures.append(
                f"{status.value}: expected is_terminal={expected_terminal}, got {actual_terminal}"
            )

    results.append(SMTestResult(
        "E4.5-is_terminal_consistency",
        "is_terminal() consistent with TERMINAL_STATUSES",
        "PASS" if not terminal_check_failures else "FAIL",
        ("; ".join(terminal_check_failures) if terminal_check_failures
         else f"All {len(list(CaseStatus))} states consistent"),
        None,
    ))

    return results
