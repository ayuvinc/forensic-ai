# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
architect

## NEXT_TASK
**Session 041: Sprint-IA-03 — Wire HybridIntakeEngine to remaining workflow pages**

AK approval required before build starts. Architect to decompose tasks, then junior-dev executes.

Sprint-IA-03 scope (confirmed in next-action.md carry-forward, Session 039):
- Wire HybridIntakeEngine to: 06_FRM.py, 09_Due_Diligence.py, 10_Sanctions.py,
  11_Transaction_Testing.py, 04_Policy_SOP.py, 05_Training.py
- Each workflow needs its own _FIELD_CONFIG (WorkflowFieldConfig list)
- Engine infrastructure already built (streamlit_app/shared/hybrid_intake.py)
- This is wiring-only — mechanical, low risk
- No new BA decisions required: BA-IA-07 covers all workflows

## COMMAND
```
/architect sprint_id=sprint-ia-03
```

## COMPLETION STATUS

```
Phase 1-8 + Sprints A-G:   100% ██████████ DONE — all merged
Phase H + Phase I (P9):    100% ██████████ DONE — merged c8ee66f
Sprint-RD:                 100% ██████████ DONE
P9 (Engagement Framework): 100% ██████████ DONE
Sprint-WF/FR/AIC/EMB/FE:  100% ██████████ DONE
Sprint-WORK/CONV/KL/ACT:  100% ██████████ DONE
Sprint-TPL (TPL-01..05):   100% ██████████ DONE — merged Session 035
Sprint-FE-TRIAGE-03/04/05: 100% ██████████ DONE — merged Session 038
Sprint-REM-01..04:         100% ██████████ DONE — merged Session 038
Sprint-IA-01:              100% ██████████ DONE — merged Session 038 (9d0aa49)
Sprint-IA-02 (hybrid intake): 100% ██████████ DONE — merged Session 039
Sprint-IA-03 (remaining workflows hybrid intake): 0% ░░░░░░░░░░ NEXT SPRINT
```

**OVERALL: ~98% complete by task count**

## CARRY_FORWARD_CONTEXT
Session 040 was a demo/walkthrough session — no sprint work executed.
App demo guidance given; session lifecycle completed cleanly.

Sprint-IA-03 context (unchanged from Session 039 handoff):
- HybridIntakeEngine built: streamlit_app/shared/hybrid_intake.py
- Investigation workflow wired (02_Investigation.py) — reference implementation
- Multi-workstream engagements: initial_workstreams in ProjectState, multiselect in 01_Engagements.py
- AUP (type 8) + Custom/Other (type 9) investigation types live
- 131 tests pass; manual smoke STEP-A..F pending Maher live run

Open carry-forward observations:
- OBS-02: "Investigation Report" sidebar label → AK preference is "Investigation" (deferred)
- OBS-03: No back/home navigation on Workspace error state (deferred)
- Manual smoke: STEP-A..F of tasks/smoke-tests/sprint-ia-02.md pending Maher live run

## BLOCKERS_AND_ENV_LIMITATIONS
- None blocking
- Watch: R-NEW-10 (HybridIntake API timeout), R-NEW-11 (mid-intake session state), R-NEW-12 (investigation_type side-effects)
