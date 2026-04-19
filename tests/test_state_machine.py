"""Tests for core/state_machine.py.

Covers: all valid transitions, all invalid transitions, is_terminal() for every
status, MAX_REVISION_ROUNDS values, and VALID_TRANSITIONS consistency.
"""
import pytest

from core.state_machine import (
    CaseStatus,
    VALID_TRANSITIONS,
    TERMINAL_STATUSES,
    MAX_REVISION_ROUNDS,
    InvalidTransitionError,
    transition,
    is_terminal,
)


# ── Valid transitions ──────────────────────────────────────────────────────────

class TestValidTransitions:
    """Every allowed transition must succeed and return the target status."""

    @pytest.mark.parametrize("from_status, to_status", [
        (CaseStatus.INTAKE_CREATED,          CaseStatus.JUNIOR_DRAFT_COMPLETE),
        (CaseStatus.INTAKE_CREATED,          CaseStatus.SCOPE_CONFIRMED),
        (CaseStatus.JUNIOR_DRAFT_COMPLETE,   CaseStatus.PM_REVIEW_COMPLETE),
        (CaseStatus.JUNIOR_DRAFT_COMPLETE,   CaseStatus.PM_REVISION_REQUESTED),
        (CaseStatus.PM_REVISION_REQUESTED,   CaseStatus.JUNIOR_DRAFT_COMPLETE),
        (CaseStatus.PM_REVIEW_COMPLETE,      CaseStatus.PARTNER_REVIEW_COMPLETE),
        (CaseStatus.PM_REVIEW_COMPLETE,      CaseStatus.PARTNER_REVISION_REQ),
        (CaseStatus.PARTNER_REVISION_REQ,    CaseStatus.PM_REVIEW_COMPLETE),
        (CaseStatus.PARTNER_REVISION_REQ,    CaseStatus.JUNIOR_DRAFT_COMPLETE),
        (CaseStatus.PARTNER_REVIEW_COMPLETE, CaseStatus.OWNER_READY),
        (CaseStatus.OWNER_READY,             CaseStatus.OWNER_APPROVED),
        (CaseStatus.OWNER_READY,             CaseStatus.OWNER_REJECTED),
        (CaseStatus.OWNER_REJECTED,          CaseStatus.JUNIOR_DRAFT_COMPLETE),
        (CaseStatus.SCOPE_CONFIRMED,         CaseStatus.DELIVERABLE_WRITTEN),
    ])
    def test_valid_transition_succeeds(self, from_status, to_status):
        result = transition(from_status, to_status)
        assert result == to_status

    def test_transition_returns_next_status_object(self):
        result = transition(CaseStatus.INTAKE_CREATED, CaseStatus.JUNIOR_DRAFT_COMPLETE)
        assert result is CaseStatus.JUNIOR_DRAFT_COMPLETE


# ── Invalid transitions ────────────────────────────────────────────────────────

class TestInvalidTransitions:
    """Transitions absent from VALID_TRANSITIONS must raise InvalidTransitionError."""

    @pytest.mark.parametrize("from_status, to_status", [
        # Backwards
        (CaseStatus.JUNIOR_DRAFT_COMPLETE,   CaseStatus.INTAKE_CREATED),
        (CaseStatus.PM_REVIEW_COMPLETE,      CaseStatus.INTAKE_CREATED),
        (CaseStatus.OWNER_APPROVED,          CaseStatus.INTAKE_CREATED),
        (CaseStatus.DELIVERABLE_WRITTEN,     CaseStatus.INTAKE_CREATED),
        (CaseStatus.PIPELINE_ERROR,          CaseStatus.INTAKE_CREATED),
        # Skip-level
        (CaseStatus.INTAKE_CREATED,          CaseStatus.PM_REVIEW_COMPLETE),
        (CaseStatus.INTAKE_CREATED,          CaseStatus.OWNER_APPROVED),
        (CaseStatus.JUNIOR_DRAFT_COMPLETE,   CaseStatus.OWNER_APPROVED),
        (CaseStatus.PM_REVISION_REQUESTED,   CaseStatus.OWNER_APPROVED),
        # Self-loop (not explicitly allowed)
        (CaseStatus.INTAKE_CREATED,          CaseStatus.INTAKE_CREATED),
        (CaseStatus.OWNER_APPROVED,          CaseStatus.OWNER_APPROVED),
    ])
    def test_invalid_transition_raises(self, from_status, to_status):
        with pytest.raises(InvalidTransitionError):
            transition(from_status, to_status)

    def test_error_message_includes_allowed_states(self):
        """Error message must name valid next states so callers can debug."""
        with pytest.raises(InvalidTransitionError, match="Allowed"):
            transition(CaseStatus.INTAKE_CREATED, CaseStatus.OWNER_APPROVED)

    def test_terminal_states_have_no_outgoing_transitions(self):
        """Terminal states must not appear as keys with non-empty targets in VALID_TRANSITIONS."""
        for status in TERMINAL_STATUSES:
            targets = VALID_TRANSITIONS.get(status, [])
            assert targets == [], (
                f"{status} is in TERMINAL_STATUSES but has outgoing transitions: {targets}"
            )


# ── is_terminal ────────────────────────────────────────────────────────────────

class TestIsTerminal:
    """is_terminal() must be True for TERMINAL_STATUSES and False for all others."""

    @pytest.mark.parametrize("status", [
        CaseStatus.OWNER_APPROVED,
        CaseStatus.PIPELINE_ERROR,
        CaseStatus.DELIVERABLE_WRITTEN,
    ])
    def test_terminal_returns_true(self, status):
        assert is_terminal(status) is True

    @pytest.mark.parametrize("status", [
        CaseStatus.INTAKE_CREATED,
        CaseStatus.JUNIOR_DRAFT_COMPLETE,
        CaseStatus.PM_REVIEW_COMPLETE,
        CaseStatus.PM_REVISION_REQUESTED,
        CaseStatus.PARTNER_REVIEW_COMPLETE,
        CaseStatus.PARTNER_REVISION_REQ,
        CaseStatus.OWNER_READY,
        CaseStatus.OWNER_REJECTED,
        CaseStatus.SCOPE_CONFIRMED,
    ])
    def test_non_terminal_returns_false(self, status):
        assert is_terminal(status) is False

    def test_is_terminal_matches_terminal_statuses_set(self):
        """is_terminal() and TERMINAL_STATUSES must be in sync for every status."""
        for status in CaseStatus:
            assert is_terminal(status) == (status in TERMINAL_STATUSES), (
                f"Mismatch: is_terminal({status}) != ({status} in TERMINAL_STATUSES)"
            )


# ── MAX_REVISION_ROUNDS ────────────────────────────────────────────────────────

class TestMaxRevisionRounds:
    def test_junior_rounds(self):
        assert MAX_REVISION_ROUNDS["junior"] == 3

    def test_pm_rounds(self):
        assert MAX_REVISION_ROUNDS["pm"] == 2


# ── VALID_TRANSITIONS consistency ─────────────────────────────────────────────

class TestTransitionMapConsistency:
    """VALID_TRANSITIONS keys and targets must all be valid CaseStatus members."""

    def test_all_source_statuses_are_valid(self):
        all_statuses = set(CaseStatus)
        for status in VALID_TRANSITIONS:
            assert status in all_statuses, f"{status!r} is not a valid CaseStatus"

    def test_all_target_statuses_are_valid(self):
        all_statuses = set(CaseStatus)
        for src, targets in VALID_TRANSITIONS.items():
            for t in targets:
                assert t in all_statuses, (
                    f"Target {t!r} in VALID_TRANSITIONS[{src}] is not a valid CaseStatus"
                )
