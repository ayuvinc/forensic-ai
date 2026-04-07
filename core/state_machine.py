from enum import Enum


class CaseStatus(str, Enum):
    INTAKE_CREATED          = "intake_created"
    JUNIOR_DRAFT_COMPLETE   = "junior_draft_complete"
    PM_REVIEW_COMPLETE      = "pm_review_complete"
    PM_REVISION_REQUESTED   = "pm_revision_requested"
    PARTNER_REVIEW_COMPLETE = "partner_review_complete"
    PARTNER_REVISION_REQ    = "partner_revision_requested"
    OWNER_READY             = "owner_ready"
    OWNER_APPROVED          = "owner_approved"
    OWNER_REJECTED          = "owner_rejected"
    PIPELINE_ERROR          = "pipeline_error"
    DELIVERABLE_WRITTEN     = "deliverable_written"   # Mode B (Assisted) terminal status
    SCOPE_CONFIRMED         = "scope_confirmed"        # Transaction Testing: testing plan locked before document ingestion


VALID_TRANSITIONS: dict[CaseStatus, list[CaseStatus]] = {
    # Standard pipeline
    CaseStatus.INTAKE_CREATED:          [CaseStatus.JUNIOR_DRAFT_COMPLETE, CaseStatus.SCOPE_CONFIRMED],
    CaseStatus.JUNIOR_DRAFT_COMPLETE:   [CaseStatus.PM_REVIEW_COMPLETE, CaseStatus.PM_REVISION_REQUESTED],
    CaseStatus.PM_REVISION_REQUESTED:   [CaseStatus.JUNIOR_DRAFT_COMPLETE],
    CaseStatus.PM_REVIEW_COMPLETE:      [CaseStatus.PARTNER_REVIEW_COMPLETE, CaseStatus.PARTNER_REVISION_REQ],
    CaseStatus.PARTNER_REVISION_REQ:    [CaseStatus.PM_REVIEW_COMPLETE, CaseStatus.JUNIOR_DRAFT_COMPLETE],
    CaseStatus.PARTNER_REVIEW_COMPLETE: [CaseStatus.OWNER_READY],
    CaseStatus.OWNER_READY:             [CaseStatus.OWNER_APPROVED, CaseStatus.OWNER_REJECTED],
    CaseStatus.OWNER_REJECTED:          [CaseStatus.JUNIOR_DRAFT_COMPLETE],
    # Transaction Testing path: testing plan confirmed → deliverable written
    CaseStatus.SCOPE_CONFIRMED:         [CaseStatus.DELIVERABLE_WRITTEN],
}

TERMINAL_STATUSES = {CaseStatus.OWNER_APPROVED, CaseStatus.PIPELINE_ERROR, CaseStatus.DELIVERABLE_WRITTEN}

MAX_REVISION_ROUNDS = {"junior": 3, "pm": 2}


class InvalidTransitionError(Exception):
    pass


def transition(current: CaseStatus, next_status: CaseStatus) -> CaseStatus:
    """Validate and apply a state transition. Raises InvalidTransitionError if invalid."""
    allowed = VALID_TRANSITIONS.get(current, [])
    if next_status not in allowed:
        raise InvalidTransitionError(
            f"Cannot transition from '{current}' to '{next_status}'. "
            f"Allowed: {[s.value for s in allowed]}"
        )
    return next_status


def is_terminal(status: CaseStatus) -> bool:
    return status in TERMINAL_STATUSES
