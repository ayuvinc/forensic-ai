# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 051 (continued) — Build Sprint-UX-PROGRESS-01**

Sprint-FOLDER-01 merged to main (QA_APPROVED 2026-04-24). 139 tests pass.

**Build now — Sprint-UX-PROGRESS-01 (1 file: streamlit_app/shared/pipeline.py):**

Option A chosen. Remove the `st.progress()` overlay from `run_in_status()`. The `st.status()` block already provides spinner (running) + green checkmark (complete). No step counting in UI.

**Exact changes to `streamlit_app/shared/pipeline.py`:**
1. Remove `total_steps: int = 3` parameter from `run_in_status()` signature
2. Remove docstring lines referencing `total_steps` (lines ~16-18 in module docstring)
3. Remove `progress_bar = st.progress(0)` (line ~161)
4. Remove `_advance_progress()` function (lines ~164-167)
5. Remove `_advance_progress()` call inside `on_progress` (line ~179) — replace with inline `step_count[0] += 1`
6. Remove `progress_bar.progress(1.0)` on pipeline success (line ~183)
7. Keep `step_count = [0]` — still used for activity log `detail.steps`

**What to keep unchanged:**
- `st.status(label, expanded=True) as status` — provides the visual indicator
- `status.update(label=..., state="complete")` on success
- Forensic tip panel (UX-WAIT-01 regression prevention)
- All activity logging, crash reporter, event log replay

**Branch:** `feature/sprint-ux-progress-01-fix-progress-bar`

**After UX-PROGRESS-01:** Sprint-INDEX-01 (foundation sprint, Tier 2).

## COMMAND
```
/junior-dev build Sprint-UX-PROGRESS-01 (PROG-01/02/03)
```

## COMPLETION STATUS

```
Phase 1-8 + Sprints A-G:        100% ██████████ DONE
Phase H + Phase I (P9):          100% ██████████ DONE
Sprint-RD/WF/FR/AIC/EMB/FE:     100% ██████████ DONE
Sprint-WORK/CONV/KL/ACT/TPL:    100% ██████████ DONE
Sprint-IA-01/02/03/04:           100% ██████████ DONE
Sprint-KB-01:                    100% ██████████ MERGED — smoke check deferred
Sprint-QUAL-01:                  100% ██████████ DONE
ARCH-SIM-01/02:                  100% ██████████ DONE
Sprint-UX-ERR-01:                100% ██████████ DONE
Sprint-UX-WAIT-01:               100% ██████████ DONE
Sprint-DOCX-01:                  100% ██████████ MERGED 2026-04-24
Sprint-PARTNER-FIX-01:           100% ██████████ MERGED 2026-04-24
Sprint-FOLDER-01:                100% ██████████ MERGED 2026-04-24
Sprint-UX-PROGRESS-01:           0%  ░░░░░░░░░░ ACTIVE — Tier 1
Sprint-INDEX-01:                 0%  ░░░░░░░░░░ QUEUED — Tier 2 Foundation
Sprint-PROCESS-01:               0%  ░░░░░░░░░░ QUEUED — Tier 2 Foundation (BA needed)
Sprint-KB-02:                    0%  ░░░░░░░░░░ QUEUED — Tier 2 Foundation (content needed)
Sprint-CHECKPOINT-01:            0%  ░░░░░░░░░░ QUEUED — Tier 3
Sprint-CLOSE-01:                 0%  ░░░░░░░░░░ QUEUED — Tier 3 (BA needed)
Sprint-EVIDENCE-01:              0%  ░░░░░░░░░░ QUEUED — Tier 3 (BA needed)
Sprint-SMOKE-01:                 0%  ░░░░░░░░░░ QUEUED — Tier 5
Sprint-UX-WIRE-01:               0%  ░░░░░░░░░░ QUEUED — Tier 4
Sprint-UX-STREAM-01:             0%  ░░░░░░░░░░ QUEUED — Tier 4
Sprint-CLI-ERR-01:               0%  ░░░░░░░░░░ QUEUED — Tier 5 (design needed)
```

## BLOCKERS_AND_ENV_LIMITATIONS
- R-NEW-13 OPEN: evidence-chain enforcement prompt-only — production cases blocked
- BA-REQ-SANCTIONS-EVIDENCE-01: Sanctions output not evidenced — do not use for real compliance files
- BA-REQ-CLOSE-01: No Mark Complete/Close button yet
- Sprint-KB-01 smoke check: DEFERRED (no API credit)
- **API credits: limited** — PROGRESS-01 has no API dependency (pure UI fix; safe to build)
- Recommendations coercion P1: RiskItem validator uses 'recommendation' key but model returns 'title' key — raw dicts still render in .md report. Fix in Sprint-KB-02 or standalone hotfix.

## CARRY_FORWARD_CONTEXT
- Three Tier 1 sprints completed this session: PARTNER-FIX-01, FOLDER-01, UX-PROGRESS-01 (active)
- Tier 1 complete clears the path for Tier 2: INDEX-01 (foundation), PROCESS-01 (BA needed), KB-02 (content needed)
- Sprint-INDEX-01 is the foundation for CHECKPOINT-01, SESSION-ENTRY-01, PROCESS-01 persistence
- UX-PROGRESS-01 is 1 file only — fastest sprint possible
