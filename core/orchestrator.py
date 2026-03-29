"""Orchestrator — pipeline sequencer with revision loops and resumability.

Runs the Junior → PM → Partner pipeline for a given workflow.
On startup, checks state.json for a non-terminal status and offers to resume.

Revision limits (from config):
  MAX_REVISION_ROUNDS = {"junior": 3, "pm": 2}
"""

from datetime import datetime, timezone
from typing import Callable

from config import MAX_REVISION_ROUNDS
from core.state_machine import (
    CaseStatus,
    InvalidTransitionError,
    is_terminal,
    transition,
)
from tools.file_tools import (
    append_audit_event,
    read_state,
    write_state,
)


# ── Types ─────────────────────────────────────────────────────────────────────

AgentRunner = Callable[[dict, dict], dict]   # (intake, context) -> output


class RevisionLimitError(Exception):
    pass

class PipelineError(Exception):
    pass


# ── Orchestrator ──────────────────────────────────────────────────────────────

class Orchestrator:
    """Sequences the Junior → PM → Partner pipeline.

    Agents are injected as callables so the orchestrator stays decoupled
    from specific agent implementations.

    Usage:
        orch = Orchestrator(case_id, workflow, junior_fn, pm_fn, partner_fn)
        result = orch.run(intake_dict)
    """

    def __init__(
        self,
        case_id: str,
        workflow: str,
        junior_fn:  AgentRunner,
        pm_fn:      AgentRunner,
        partner_fn: AgentRunner,
        on_status_change: Callable[[CaseStatus], None] | None = None,
    ):
        self.case_id   = case_id
        self.workflow  = workflow
        self.junior_fn  = junior_fn
        self.pm_fn      = pm_fn
        self.partner_fn = partner_fn
        self.on_status_change = on_status_change or (lambda s: None)

        self._revision_counts = {"junior": 0, "pm": 0}

    # ── Public entry point ────────────────────────────────────────────────────

    def run(self, intake: dict) -> dict:
        """Run (or resume) the pipeline. Returns the partner's final output."""
        status = self._load_or_init_status(intake)
        context = {"case_id": self.case_id, "workflow": self.workflow}

        # ── resume logic ─────────────────────────────────────────────────────
        if status == CaseStatus.INTAKE_CREATED:
            junior_output = self._run_junior(intake, context)
        elif status == CaseStatus.PM_REVISION_REQUESTED:
            junior_output = self._run_junior(intake, context)
        elif status == CaseStatus.JUNIOR_DRAFT_COMPLETE:
            junior_output = self._load_last_output("junior_output")
        else:
            junior_output = self._load_last_output("junior_output")

        if status in (
            CaseStatus.INTAKE_CREATED,
            CaseStatus.JUNIOR_DRAFT_COMPLETE,
            CaseStatus.PM_REVISION_REQUESTED,
        ):
            pm_output = self._run_pm(junior_output, context)
        elif status == CaseStatus.PARTNER_REVISION_REQ:
            pm_output = self._run_pm(junior_output, context)
        elif status == CaseStatus.PM_REVIEW_COMPLETE:
            pm_output = self._load_last_output("pm_review")
        else:
            pm_output = self._load_last_output("pm_review")

        if status not in (
            CaseStatus.PARTNER_REVIEW_COMPLETE,
            CaseStatus.OWNER_READY,
            CaseStatus.OWNER_APPROVED,
        ):
            partner_output = self._run_partner(pm_output, context)
        else:
            partner_output = self._load_last_output("partner_approval")

        return partner_output

    # ── Stage runners ─────────────────────────────────────────────────────────

    def _run_junior(self, intake: dict, context: dict) -> dict:
        max_rounds = MAX_REVISION_ROUNDS["junior"]
        while self._revision_counts["junior"] < max_rounds:
            try:
                output = self.junior_fn(intake, {**context, "agent": "junior"})
                self._set_status(CaseStatus.JUNIOR_DRAFT_COMPLETE)
                return output
            except Exception as e:
                self._set_status(CaseStatus.PIPELINE_ERROR)
                raise PipelineError(f"Junior agent failed: {e}") from e
        raise RevisionLimitError(f"Junior exceeded max revision rounds ({max_rounds})")

    def _run_pm(self, junior_output: dict, context: dict) -> dict:
        max_rounds = MAX_REVISION_ROUNDS["pm"]
        while self._revision_counts["pm"] < max_rounds:
            output = self.pm_fn(junior_output, {**context, "agent": "pm"})

            revision_requested = output.get("revision_requested", False)
            if revision_requested:
                self._revision_counts["pm"] += 1
                self._revision_counts["junior"] += 1
                self._set_status(CaseStatus.PM_REVISION_REQUESTED)
                # re-run junior with PM feedback
                revised = self.junior_fn(
                    {**junior_output, "pm_feedback": output.get("feedback")},
                    {**context, "agent": "junior", "revision_round": self._revision_counts["junior"]},
                )
                self._set_status(CaseStatus.JUNIOR_DRAFT_COMPLETE)
                junior_output = revised
                continue

            self._set_status(CaseStatus.PM_REVIEW_COMPLETE)
            return output

        raise RevisionLimitError(f"PM exceeded max revision rounds ({max_rounds})")

    def _run_partner(self, pm_output: dict, context: dict) -> dict:
        output = self.partner_fn(pm_output, {**context, "agent": "partner"})

        revision_requested = output.get("revision_requested", False)
        if revision_requested:
            self._set_status(CaseStatus.PARTNER_REVISION_REQ)
            raise PipelineError(
                "Partner requested revision — re-run pipeline from PM stage. "
                f"Reason: {output.get('feedback', 'unspecified')}"
            )

        self._set_status(CaseStatus.PARTNER_REVIEW_COMPLETE)
        self._set_status(CaseStatus.OWNER_READY)
        return output

    # ── State helpers ─────────────────────────────────────────────────────────

    def _load_or_init_status(self, intake: dict) -> CaseStatus:
        state = read_state(self.case_id)
        if state and not is_terminal(CaseStatus(state["status"])):
            current = CaseStatus(state["status"])
            self._revision_counts = state.get("revision_rounds", {"junior": 0, "pm": 0})
            return current
        # fresh start
        self._set_status(CaseStatus.INTAKE_CREATED, intake)
        return CaseStatus.INTAKE_CREATED

    def _set_status(self, status: CaseStatus, extra: dict | None = None) -> None:
        now = datetime.now(timezone.utc).isoformat()
        state = {
            "case_id":        self.case_id,
            "workflow":       self.workflow,
            "status":         status.value,
            "revision_rounds": self._revision_counts,
            "last_updated":   now,
        }
        if extra:
            state.update(extra)
        write_state(self.case_id, state)
        append_audit_event(self.case_id, {
            "event":    "status_change",
            "status":   status.value,
            "workflow": self.workflow,
        })
        self.on_status_change(status)

    # Artifact type → persisting role mapping (must match write_envelope calls)
    _ARTIFACT_ROLES: dict[str, str] = {
        "junior_output":    "junior",
        "pm_review":        "pm",
        "partner_approval": "partner",
    }

    def _load_last_output(self, artifact_type: str) -> dict:
        """Load persisted artifact payload for resume.

        Uses load_envelope() so ArtifactEnvelope wrappers are transparently unwrapped.
        Falls back to raw glob if the artifact was written without an envelope.
        """
        from tools.file_tools import load_envelope, case_dir
        import json, glob as _glob

        role = self._ARTIFACT_ROLES.get(artifact_type)
        if role:
            result = load_envelope(self.case_id, role, artifact_type)
            if result is not None:
                return result

        # Fallback: glob pattern (covers FRM module artifacts and legacy bare payloads)
        pattern = str(case_dir(self.case_id) / f"*_{artifact_type}.v*.json")
        files = sorted(_glob.glob(pattern))
        if not files:
            return {}
        data = json.loads(open(files[-1], encoding="utf-8").read())
        return data.get("payload", data)  # unwrap envelope if present
