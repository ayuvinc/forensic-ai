# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
manual-verify → architect → session-close

## NEXT_TASK
**Session 037: Sprint-IA-01 — IA-VERIFY gate (manual), then merge to main**

Sprint-IA-01 build is complete and committed (`2d68014` on `feature/sprint-fe-triage`).
131 tests pass. The only remaining gate is IA-VERIFY — a manual browser pass.

**Required before QA_APPROVED:**

1. `IA-VERIFY` — AK runs: `streamlit run app.py`
   - Sidebar shows exactly 5 sections: MAIN, PROPOSALS, MONITOR, SETTINGS, WORKFLOWS
   - "b Scope" is gone — shows "Scope" under PROPOSALS
   - 00_Setup NOT visible in sidebar (redirect-only)
   - All workflow pages reachable via sidebar
   - Engagements page: "Run Workflow" selectbox includes Persona Review
   - Workspace: run `python3 scripts/seed_test_engagement.py` first, then open "abc-corp-test-engagement" — should show "Workflow Outputs" expander with 3 sections + download links
   - Proposals page: Arc 1 info banner visible at top
   - No new crashes introduced on any page

2. AK reports PASS/FAIL back. If PASS: architect closes sprint, merges to main, writes session-close.

**If IA-VERIFY has failures:**
- Note the exact page + error
- Open /junior-dev to fix, then re-run IA-VERIFY

## COMMAND
After AK runs IA-VERIFY:
```
/architect Sprint-IA-01 IA-VERIFY PASS — close sprint, merge feature/sprint-fe-triage to main, write session-close
```

Or if failures found:
```
/junior-dev IA-VERIFY failure: [exact error] — fix and retest
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
Sprint-FE-TRIAGE-03/04/05: 100% ██████████ DONE — on feature/sprint-fe-triage
Sprint-REM-01..04:         100% ██████████ DONE — committed 2d68014
Sprint-IA-01 docs:         100% ██████████ DONE — hld, README, brief, scope, LLD, packaging all current
Sprint-IA-01 code:         100% ██████████ BUILT — awaiting IA-VERIFY (manual gate)
Sprint-IA-01 QA:             0% ░░░░░░░░░░ BLOCKED — IA-VERIFY not yet run
Sprint-IA-02 (hybrid intake): 0% ░░░░░░░░░░ AFTER Sprint-IA-01 merges
```

**OVERALL: ~95% complete by task count**

## CARRY_FORWARD_CONTEXT
Sprint-IA-01 delivered:
- app.py: st.navigation() 5-section sidebar, bootstrap(st, caller_file=__file__)
- 01_Engagements.py: Persona Review added to workflow selectbox (no service_type restriction confirmed)
- 16_Workspace.py: Workflow Outputs expander iterates ProjectState.cases
- 07_Proposal.py: Arc 1 info banner
- scripts/seed_test_engagement.py: test engagement with 3 completed workflow cases

Sprint-REM-01..04 also committed in same PR:
- PII hardening (FUT-01..03), orchestrator fix (FUT-04), schema validators (FUT-05), Partner decision gate (FUT-06), evidence chain fix (FUT-07), audit_log mkdir (FUT-24)
- feature-gates.md (Gates 1–4) — pre-build requirements for unbuilt features

## BLOCKERS_AND_ENV_LIMITATIONS
- IA-VERIFY requires manual browser test — cannot be automated
- sentence-transformers not installed — EMB tests use code-inspection path
- FE-TRIAGE-01 (full triage pass) paused — resume after Sprint-IA-01 merges if crashes remain
- Sprint-IA-02 gated on IA-VERIFY PASS
