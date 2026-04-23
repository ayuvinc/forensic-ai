# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
architect

## NEXT_TASK
**Session 042: Sprint-IA-04 — Policy/SOP Guided Co-Build Mode**

Sprint-IA-03 complete and merged (Session 041). HybridIntakeEngine now wired to all 7 workflows.

Next sprint requires a dedicated architect session before any build tasks are written:
- BA: BA-IA-09 confirmed (tasks/ba-logic.md)
- Product context: docs/product-packaging.md → "Product Positioning Insight — Co-Build Mode"
- Prerequisite: Sprint-IA-03-W5 QA_APPROVED (done)

Architect decomposes Sprint-IA-04 into tasks and gets AK approval before junior-dev builds.

## COMMAND
```
/architect sprint_id=sprint-ia-04
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
Sprint-IA-03 (remaining workflows): 100% ██████████ DONE — merged Session 041 (5246ad4)
Sprint-IA-04 (Policy/SOP co-build): 0% ░░░░░░░░░░ NEXT SPRINT
```

**OVERALL: ~99% complete by task count**

## CARRY_FORWARD_CONTEXT

Sprint-IA-03 summary (Session 041):
- HybridIntakeEngine wired to all 7 workflow pages (FRM, DD, Sanctions, TT, Policy/SOP, Training + Investigation)
- All generic_intake_form / frm_intake_form / dd_intake_form removed from 6 pages
- BA-IA-09 written: Policy/SOP co-build mode (section-by-section sync loop)
- 131 tests pass; smoke spec written

Open carry-forward observations (unchanged):
- OBS-02: "Investigation Report" sidebar label → AK preference is "Investigation" (deferred)
- OBS-03: No back/home navigation on Workspace error state (deferred)
- Manual smoke: tasks/smoke-tests/sprint-ia-03.md Steps A-G pending Maher live run

## BLOCKERS_AND_ENV_LIMITATIONS
- None blocking
- Sprint-IA-04 needs architect decomposition before build — BA-IA-09 is the input
