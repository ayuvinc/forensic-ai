# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
architect

## NEXT_TASK
**Session 051 — Sprint-DOCX-01 merge + Sprint-PARTNER-FIX-01 build + Sprint-PROCESS-01 BA sign-off**

Session 050 completed on branch `feature/sprint-docx-01-download-buttons`:

**Immediate on session open:**
1. AK confirms DOCX-03 (download buttons visible in FRM Done Zone) — call PASS or FAIL
2. Architect merges `feature/sprint-docx-01-download-buttons` → main
3. Build Sprint-PARTNER-FIX-01 (2-3 tasks, fixes broken Partner prompt, no design needed)
4. Write BA logic for Sprint-PROCESS-01 per-workflow questionnaires and confirm with AK
5. Plan Sprint-INDEX-01 build session

**Sprint priority order (see `docs/app-plan.md` for full plan):**
- Tier 1 (fix broken): PARTNER-FIX-01, FOLDER-01, UX-PROGRESS-01
- Tier 2 (foundation): INDEX-01, PROCESS-01, KB-02
- Tier 3 (quality): CHECKPOINT-01, CLOSE-01, EVIDENCE-01
- Tier 4 (UX polish): UPLOAD-01, NAV-01, SESSION-ENTRY-01, WIRE-01, STREAM-01
- Tier 5 (quality gates): SMOKE-01, CLI-ERR-01
- Tier 6 (advanced): IA-04, STAGE-01, Phase 7

**Session 050 work committed (all on feature branch, not yet merged):**
- FRM schema_retry double-failure: graceful module skip (was crashing pipeline)
- FRM module sequencing display: [Module 1/2], [Module 2/2] (was [Module 4/2])
- Forensic tip panel during pipeline runs (Sprint-UX-WAIT-01 DONE)
- docs/product-packaging.md: Human checkpoint layer positioning insight
- Sprint-INDEX-01, CHECKPOINT-01, SESSION-ENTRY-01 tasks written
- Sprint-PARTNER-FIX-01, KB-02, PROCESS-01, CLOSE-01, EVIDENCE-01 tasks written
- BA-REQ-PROCESS-01 written in tasks/ba-logic.md
- docs/app-plan.md: full application plan, 7 layers, sprint sequence, gap analysis

## COMMAND
```
AK: run FRM workflow in browser → confirm both download buttons appear in Done Zone → report PASS/FAIL
Then: /architect to merge branch + build Sprint-PARTNER-FIX-01
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
Sprint-DOCX-01:                  90% █████████░ CODE DONE — DOCX-03 smoke pending
Sprint-PARTNER-FIX-01:           0%  ░░░░░░░░░░ QUEUED — Tier 1
Sprint-FOLDER-01:                0%  ░░░░░░░░░░ QUEUED — Tier 1
Sprint-UX-PROGRESS-01:           0%  ░░░░░░░░░░ QUEUED — Tier 1
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
- DOCX-03: .docx download unverified until AK runs complete workflow
- **API credits: exhausted as of 2026-04-23** — all pipeline testing blocked until credits restored
- **Partner prompt BROKEN**: blocks delivery instead of flagging — fix before any output is used in production

## CARRY_FORWARD_CONTEXT
- Full application plan at `docs/app-plan.md` — authoritative sprint order, 7-layer gap analysis, design debt register
- BA-REQ-PROCESS-01 written — process understanding stage designed, per-workflow questions specified, ready for build after BA sign-off
- Partner fix is 2-3 prompt changes — highest priority after DOCX-01 merge
- Sprint-INDEX-01 is the foundation for CHECKPOINT-01, SESSION-ENTRY-01, PROCESS-01 persistence — build it early
- Project name = case folder (slugified). Engagement path: Engagements page sets it.
- Industry field: 18-option selectbox on all workflows
- FRM pipeline: schema_retry fires on empty findings; double-retry graceful skip now works; module index display fixed
- Error log at logs/error_log.jsonl accumulates every crash with category
