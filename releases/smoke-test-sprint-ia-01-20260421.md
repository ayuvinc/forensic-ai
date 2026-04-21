# Smoke Test — Sprint-IA-01 — Navigation Restructure + Multi-Workflow Workspace
Date: 20260421
Sprint: sprint-ia-01
Branch: feature/sprint-fe-triage
Tester: AK (manual)
Overall: FAIL

## Summary
| Step | Area | Severity | Result | Notes |
|------|------|----------|--------|-------|
| STEP-00 | Setup | P0 | PASS | Last line: "Seed complete. Run: streamlit run app.py" |
| STEP-01 | Startup | P0 | PASS | First page title: "Engagements" |
| STEP-02 | Sidebar | P0 | PASS | Headers: Main, Proposals, Monitor, Settings, Workflows. keyboard_double + expand_more icons visible (transient font-load issue — not present in later screenshots) |
| STEP-03 | Sidebar | P0 | PASS | Engagements and Workspace visible in that order |
| STEP-04 | Sidebar | P0 | PASS | Link reads "Scope" — no "b" prefix |
| STEP-05 | Sidebar | P0 | PASS | MONITOR and SETTINGS correct — no unexpected entries |
| STEP-06 | Sidebar | P0 | PASS | 9 workflow links present including Persona Review |
| STEP-07 | Sidebar | P0 | PASS | No Setup link visible anywhere in sidebar |
| STEP-08 | Pages | P0 | PASS | Left panel shows all engagement cards, right panel shows detail |
| STEP-09 | Pages | P0 | PASS | Banner: "Arc 1 — Proposal: Step 2 of 3 (Proposal Deck). Complete Scope first..." |
| STEP-10 | Pages | P0 | FAIL | URL: localhost:8501/b_Scope — page filename still has "b" prefix. Page heading clean. |
| STEP-11 | Pages | P1 | PASS | Case Tracker and Activity Log both loaded cleanly — no warnings |
| STEP-12 | Pages | P1 | PASS | Both workflow pages loaded cleanly. AK note: "Investigation Report" label — AK prefers "Investigation" |
| STEP-13 | Pages | P0 | FAIL | Workspace picker: "Engagement case_test_001 not found." — seed creates legacy format, Workspace expects A-F format |
| STEP-14 | Multi-Workflow | P0 | FAIL | Active Engagements empty — abc-corp-test-engage in Legacy Cases (5). Seed script creates legacy-format cases. |
| STEP-15 | Multi-Workflow | P0 | CONDITIONAL PASS | Persona Review in Service type dropdown + WORKFLOWS sidebar. Run Workflow selectbox untestable — no A-F engagement. Intent confirmed via alternate path. |
| STEP-16 | Workspace | P0 | FAIL | abc-corp-test-engagement is legacy format — not selectable in Workspace picker. Workflow Outputs expander untestable. |

## P0 Failures (blocks QA_APPROVED)
- **STEP-10**: Scope page URL slug is `/b_Scope` — page filename still has "b" prefix. Page heading is clean. Fix: rename the page file to remove the "b" prefix so URL slug becomes `/Scope`.
- **STEP-13**: Workspace picker triggers "Engagement case_test_001 not found." Root cause: seed script writes legacy-format cases; Workspace page expects A-F format. Fix: rewrite `scripts/seed_test_engagement.py` to create an A-F format engagement with ProjectState structure.
- **STEP-14**: Active Engagements section empty — seed cases land in "Legacy Cases (5)" (confirmed via screenshot). Same root cause as STEP-13.
- **STEP-16**: Workspace Workflow Outputs expander untestable — no A-F engagement exists. Same root cause as STEP-13/14.

## P1 Failures (documented, does not block)
- none

## Observations (outside spec)
- **P1-OBS-01** (STEP-02): Material Icons rendering as literal text ("keyboard_double", "expand_more") overlapping sidebar nav labels — transient font-load issue, not present in later screenshots. Monitor on next run.
- **OBS-02** (STEP-12): Sidebar link reads "Investigation Report" — AK preference is "Investigation". Label rename to consider.
- **OBS-03** (STEP-13): No back/home button when Workspace is in error state. AK requests back navigation on all pages and workflow screens.

## Fix Summary (3 items — all related to 2 root causes)
| # | Root Cause | Fix |
|---|-----------|-----|
| FIX-01 | Scope page filename has "b" prefix | Rename file — remove "b_" from filename so URL slug is `/Scope` |
| FIX-02 | Seed script creates legacy-format cases | Rewrite `scripts/seed_test_engagement.py` to produce A-F format engagement with ProjectState structure |
| FIX-03 (OBS) | No back navigation in error state | Add back/home button to Workspace and workflow pages (post-merge UX task) |

## QA Signal
**QA_REJECTED**
Reason: 4 P0 failures — Scope page URL slug wrong (FIX-01) and seed script format mismatch blocking STEP-13/14/16 (FIX-02). Fix required before merge. Re-run `/smoke-test sprint_id=sprint-ia-01` after fixes.
