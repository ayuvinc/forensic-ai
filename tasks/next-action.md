# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
session-close

## NEXT_TASK
**Session 038: Sprint-IA-01 COMPLETE — close session**

Sprint-IA-01 is fully merged to main (commit 9d0aa49).
All 17 smoke test steps pass. QA_APPROVED.

Run `/session-close` to close Session 038 and write the session summary.

## COMMAND
```
/session-close
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
Sprint-IA-02 (hybrid intake): 0% ░░░░░░░░░░ NEXT SPRINT
```

**OVERALL: ~97% complete by task count**

## CARRY_FORWARD_CONTEXT
Sprint-IA-01 delivered and merged:
- app.py: st.navigation() 5-section sidebar
- 01_Scope.py: renamed from 01b_Scope.py (URL slug fix)
- 16_Workspace.py: Workflow Outputs expander, A-F picker filter, client_name from index
- 01_Engagements.py: IDD - Background checks in service type + Run Workflow selectbox
- tools/file_tools.py: build_case_index() preserves is_af_project flag
- scripts/seed_test_engagement.py: seed creates A-F engagement
- All "Persona Review" labels → "Individual Due Diligence - Background checks" (14 locations)
- docs/hld.md + docs/lld/product-ia-design.md: updated to reflect rename + file rename

Open observations (carry to Sprint-IA-02 or backlog):
- OBS-02: "Investigation Report" sidebar label → AK preference is "Investigation"
- OBS-03: No back/home navigation on Workspace error state

## BLOCKERS_AND_ENV_LIMITATIONS
- Sprint-IA-02 (hybrid intake) — can begin next session
- FE-TRIAGE-01 (full triage pass) — resume if crashes remain post-IA-01 merge
