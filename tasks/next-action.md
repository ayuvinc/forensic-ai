# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
architect

## NEXT_TASK
**Session 052 — Sprint-INDEX-01 (Tier 2 Foundation)**

Tier 1 fully closed Session 051: DOCX-01, PARTNER-FIX-01, FOLDER-01, UX-PROGRESS-01 all merged to main (2026-04-24). 139 tests pass.

**Sprint-INDEX-01 — Pipeline State Index:**

Design confirmed Session 050. Additive only — no UI, no pipeline redesign.
Schema and task list in `tasks/todo.md` Sprint-INDEX-01 block.

**Architect start-of-session tasks:**
1. QA writes AC for INDEX-01/02/03/04 before Junior Dev starts
2. Architect confirms scope (5 tasks: INDEX-01..05) — all dependencies clear
3. Branch: `feature/sprint-index-01-pipeline-state-index`

**File scope:**
- NEW: `tools/pipeline_index.py` — `PipelineIndex` class
- MODIFY: `core/hooks.py` — `persist_artifact` hook wires `PipelineIndex.update_stage()`
- MODIFY: `workflows/frm_risk_register.py` — skip completed stages + fire milestone
- MODIFY: `workflows/investigation_report.py` — same pattern
- SMOKE: INDEX-05 (requires API credits — FRM knowledge_only run)

**After INDEX-01:** Sprint-CHECKPOINT-01 (Tier 3) unblocked. Sprint-PROCESS-01 and Sprint-KB-02 also Tier 2 but need BA sign-off / content session first.

## COMMAND
```
/session-open
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
Sprint-UX-PROGRESS-01:           100% ██████████ MERGED 2026-04-24
Sprint-INDEX-01:                 0%  ░░░░░░░░░░ ACTIVE — Tier 2 Foundation
Sprint-PROCESS-01:               0%  ░░░░░░░░░░ QUEUED — Tier 2 (BA needed)
Sprint-KB-02:                    0%  ░░░░░░░░░░ QUEUED — Tier 2 (content needed)
Sprint-CHECKPOINT-01:            0%  ░░░░░░░░░░ QUEUED — Tier 3 (after INDEX-01)
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
- **API credits: limited** — INDEX-01/02/03/04 are code-only (safe to build). INDEX-05 smoke test needs API credit (FRM knowledge_only run).
- Recommendations coercion P1: RiskItem validator uses 'recommendation' key but model returns 'title' key — raw dicts still render in .md report. Fix in Sprint-KB-02 or standalone hotfix.

## CARRY_FORWARD_CONTEXT
- Session 051 closed all Tier 1 sprints (PARTNER-FIX-01, FOLDER-01, UX-PROGRESS-01) in a single session
- Sprint-INDEX-01 is the dependency foundation for CHECKPOINT-01 and SESSION-ENTRY-01
- PROCESS-01 and KB-02 are Tier 2 but each need a non-code prerequisite session before Junior Dev can build
- INDEX-05 (smoke verify resume-on-failure) requires API credits — deferred like KB-01 smoke
