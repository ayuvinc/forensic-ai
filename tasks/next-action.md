# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 041: Sprint-IA-03 — AK approval received → junior-dev executes IA-03-C1 through IA-03-W6**

Architect decomposition complete (Session 041). Tasks written to tasks/todo.md.

All 4 design decisions confirmed by AK (Session 041):
- [D1 CONFIRMED] FRM: 8 individual radio (Yes/No) fields per module, each has_remarks=True. Dependency check runs in page after engine_result.
- [D2 CONFIRMED] Training: duration selectbox (presets), include_quiz/case_study radio Yes/No.
- [D3 CONFIRMED] Sanctions: subject_name INSIDE engine; client_name OUTSIDE (engagement banner).
- [D4 CONFIRMED] Policy/SOP IA-03-W5: fixed 11 types only; no Custom in this sprint. Custom co-build → Sprint-IA-04.

Junior-dev runs IA-03-C1 first (field configs + option lists), then W1–W6 in parallel, then QA.

Sprint-IA-04 (co-build) queued — needs dedicated architect session. BA-IA-09 written.

## COMMAND
```
/junior-dev task_id=IA-03-C1
```

(After IA-03-C1 complete: run W1–W6 in parallel, then QA)

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
