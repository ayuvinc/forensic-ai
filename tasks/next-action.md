# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 039: Sprint-IA-02 — Hybrid Intake — Stream A first**

Sprint-IA-02 is designed and tasks written to `tasks/todo.md`. AK has approved scope.

Start with Stream A (BA-IA-04 — schema changes, safest first):
1. **IA-02-A1** — Add `project_name: str` + `initial_workstreams: list[str]` to `ProjectState` (`schemas/project.py`)
2. **IA-02-A2** — Update `ProjectIntake` + `ProjectManager.create_project()` to persist both fields
3. **IA-02-A3** — Update `01_Engagements.py`: multiselect workstream picker, ≥1 validation
4. **IA-02-A4** — Update `16_Workspace.py`: show initial_workstreams + "Run Now" cards

Then Stream B (IA-02-B1..B5 — knowledge file + intake branches for AUP/Custom).
Then Stream C (IA-02-C1..C5 — HybridIntakeEngine for Investigation).

## COMMAND
```
/junior-dev
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
Sprint-IA-02 (hybrid intake): 0% ░░░░░░░░░░ IN PROGRESS (Session 039)
Sprint-IA-03 (remaining workflows hybrid intake): 0% ░░░░░░░░░░ NEXT SPRINT
```

**OVERALL: ~97% complete by task count**

## CARRY_FORWARD_CONTEXT
Sprint-IA-01 doc debt resolved:
- `docs/lld/product-ia-design.md` navigation table + app.py code block updated to reflect as-built state
- FIX-01/02/03, CR-01 archived to releases/completed-tasks.md

Sprint-IA-02 scope (confirmed by Architect Session 039):
- Stream A: BA-IA-04 — `project_name` + `initial_workstreams` in `ProjectState`; multi-workstream UI in `01_Engagements.py`; "Not yet run" cards in `16_Workspace.py`
- Stream B: BA-IA-05/06 — AUP (type 8) + Custom (type 9) investigation intake branches; Partner AUP hard rule
- Stream C: BA-IA-07 — `HybridIntakeEngine` infrastructure + Investigation wiring only
- Sprint-IA-03: HybridIntakeEngine wiring for FRM, DD, Sanctions, TT, Policy/SOP, Training

Open observations (carry from Sprint-IA-01):
- OBS-02: "Investigation Report" sidebar label → AK preference is "Investigation" (deferred)
- OBS-03: No back/home navigation on Workspace error state (deferred)

## BLOCKERS_AND_ENV_LIMITATIONS
- AK must approve Sprint-IA-02 task plan before Junior Dev starts building
- HybridIntakeEngine targeted conversation (IA-02-C2d) makes Claude API call during intake — ensure RESEARCH_MODE check gated before build begins
- investigation_type field addition to CaseIntake (IA-02-B2b) is a schema touch — run 131 tests after this task before proceeding
