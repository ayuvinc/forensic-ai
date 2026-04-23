# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
architect

## NEXT_TASK
**Session 049: Fix 01_Scope.py rename + sprint selection (priority reorder needed)**

Session 048 completed:
- Page load smoke test: 19/19 P0 PASS, QA_APPROVED, zero crashes
- Sprint-UX-ERR-01 error boundaries confirmed working across all 17 pages
- 3 new BA requirements captured from live smoke test:
  - BA-REQ-FORMATTING-01: Word (.docx) output + format selector in every intake (prime requirement)
  - BA-REQ-CLOSE-01: "Mark Complete / Close" button on all engagements, workflows, cases
  - BA-REQ-SANCTIONS-EVIDENCE-01: Evidence capture per citation hit (copy, URL, timestamp, per-hit determination)
- Results: releases/smoke-test-page-load-check-20260423.md
- ba-logic.md updated with all 3 requirements

**Outstanding items — architect must resolve at session open:**

1. **01_Scope.py prefix collision** — rename pages/01_Scope.py to pages/17_Scope.py (or confirm number). Quick fix, no logic changes. Must do before next sprint.

2. **Sprint priority reorder** — three new BA requirements change the queue. Architect must re-evaluate:
   - BA-REQ-FORMATTING-01 (.docx output) affects ALL workflows — high user impact
   - BA-REQ-CLOSE-01 (close button) affects Engagements + Case Tracker — medium impact
   - BA-REQ-SANCTIONS-EVIDENCE-01 (evidence chain) — compliance-critical, aligns with R-NEW-13
   - Original queue: Sprint-SMOKE-01 → Sprint-UX-WIRE-01 → Sprint-UX-STREAM-01
   - New question: does .docx sprint move above SMOKE-01 given it was called a prime requirement?

3. **P1 observations from smoke test** (full list in releases/smoke-test-page-load-check-20260423.md):
   - Page 00 label "Setting" → "Setup"
   - Page 02 label "Investigation Report" → "Investigation" (OBS-02 long deferred)
   - Persona Review sidebar restructure (WORKFLOWS injected into main sidebar)
   - Page dimming on state transitions → Sprint-UX-WIRE-01
   - Sanctions disposition hits not shown inline before memo generation
   - Workspace needs list-to-select UI
   - Setup page slow to load

## COMMAND
```
/session-open session_id=049
```
Then: confirm 01_Scope.py rename + architect sprint priority decision

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
Sprint-UX-ERR-01:                100% ██████████ DONE — confirmed by smoke test
Page load smoke test:            100% ██████████ QA_APPROVED Session 048
Sprint-SMOKE-01 (formal suite):  0% ░░░░░░░░░░ QUEUED
Sprint-DOCX-01 (.docx output):   0% ░░░░░░░░░░ NEW — priority TBD
Sprint-UX-WIRE-01:               0% ░░░░░░░░░░ QUEUED
Sprint-UX-STREAM-01:             0% ░░░░░░░░░░ QUEUED
```

## CARRY_FORWARD_CONTEXT

Session 048 P1 observations (full detail in smoke test report):
- OBS-01: Page 00 label "Setting" not "Setup"
- OBS-02: Page 02 label "Investigation Report" not "Investigation" (long deferred)
- OBS-03: 01_Scope / 01_Engagements prefix collision — must rename
- OBS-04: Persona Review sidebar restructure when page loads
- OBS-05: Full page dims on state transitions — Sprint-UX-WIRE-01
- OBS-06: Sanctions disposition hits not shown inline
- OBS-07: No verifiable evidence per citation in Sanctions memo
- OBS-08: No .docx output — BA-REQ-FORMATTING-01
- OBS-09: No close/complete button — BA-REQ-CLOSE-01
- OBS-10: Workspace needs list UI
- OBS-11: Setup page slow to load

## BLOCKERS_AND_ENV_LIMITATIONS
- Sprint-KB-01 smoke check: DEFERRED (no API credit); CLI only, RESEARCH_MODE=knowledge_only
- R-NEW-13 OPEN: evidence-chain enforcement prompt-only — production cases blocked
- BA-REQ-SANCTIONS-EVIDENCE-01: Sanctions output not evidenced — do not use for real compliance files until resolved
