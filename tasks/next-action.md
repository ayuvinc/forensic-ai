# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
architect (after DOCX-03 smoke pass)

## NEXT_TASK
**DOCX-03 smoke verify → Sprint-DOCX-01 merge → architect sprint planning**

Session 049 completed on branch `feature/sprint-docx-01-download-buttons`:

**Sprint-DOCX-01 (all code done, one AK step remaining):**
- DOCX-01 through DOCX-02e: .docx + .md download buttons in st.columns(2) on all 8 output surfaces
- DOCX-03: AK must run FRM knowledge_only end-to-end, confirm both buttons appear, .docx opens in Word → call PASS or FAIL

**Ad-hoc fixes committed same branch:**
- JuniorDraft.recommendations coercion (dict → str)
- FRM schema_retry on HookVetoError (empty findings crash fixed)
- Industry dropdown (18 options) across all 5 workflow configs
- Project name field on all 8 workflow intakes → used as case folder name (replaces date-hex UUID)
- logs/error_log.jsonl: structured error log for pattern analysis

**Pending design questions (architect must decide before next sprint):**
1. CLI error runner sprint — build a headless pipeline runner that exercises each workflow, catches exceptions, appends to error_log.jsonl → gives us an error inventory without API cost
2. Sprint priority reorder — BA-REQ-FORMATTING-01 (done), BA-REQ-CLOSE-01 (close button), BA-REQ-SANCTIONS-EVIDENCE-01 (evidence chain), Sprint-SMOKE-01, Sprint-UX-WIRE-01
3. Error UX workarounds — defer until error_log.jsonl accumulates data from real runs

## COMMAND
```
AK: run FRM workflow in browser → confirm both download buttons → report PASS/FAIL
Then: /architect to merge branch + plan next sprint
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
Sprint-DOCX-01:                  90% █████████░ CODE DONE — DOCX-03 smoke pending
Sprint-SMOKE-01 (formal suite):  0%  ░░░░░░░░░░ QUEUED
Sprint-UX-WIRE-01:               0%  ░░░░░░░░░░ QUEUED
Sprint-UX-STREAM-01:             0%  ░░░░░░░░░░ QUEUED
Sprint-CLI-ERR-01 (error runner):0%  ░░░░░░░░░░ NEW — design pending
```

## BLOCKERS_AND_ENV_LIMITATIONS
- R-NEW-13 OPEN: evidence-chain enforcement prompt-only — production cases blocked
- BA-REQ-SANCTIONS-EVIDENCE-01: Sanctions output not evidenced — do not use for real compliance files
- BA-REQ-CLOSE-01: No Mark Complete/Close button yet
- Sprint-KB-01 smoke check: DEFERRED (no API credit)
- DOCX-03: .docx download unverified until AK runs a complete workflow

## CARRY_FORWARD_CONTEXT
- Project name = case folder (slugified). Engagement path: Engagements page sets it. Standalone path: each workflow asks for it.
- Industry field is now a selectbox (18 options) on all workflows — no longer free text
- FRM pipeline: schema_retry fires on empty findings; recommendations dict→str coercion added
- Error log at logs/error_log.jsonl accumulates every crash with category — read this before designing error UX workarounds
