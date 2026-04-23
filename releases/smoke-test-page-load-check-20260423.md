# Smoke Test — Page Load Check
Date: 20260423
Sprint: page-load-check
Tester: AK (manual, live Streamlit app)
Overall: PASS

## Summary
| Step | Area | Severity | Result | Notes |
|------|------|----------|--------|-------|
| A-1 | Sidebar | P0 | PASS | 20 pages visible (expected ~17; both 01_ pages showing) |
| B-1 | Setup (00) | P0 | PASS | Renders — labelled "Setting" not "Setup"; slow to load |
| B-2 | Engagements (01) | P0 | PASS | Renders cleanly |
| C-1 | Scope (01 collision) | P1 | PASS | Both 01_Scope and 01_Engagements visible as separate sidebar entries; Streamlit tolerating collision on this machine |
| C-2 | Investigation (02) | P0 | PASS | Renders — sidebar label still "Investigation Report" not "Investigation" (OBS-02 deferred) |
| C-3 | Persona Review (03) | P0 | PASS | Renders correct content; sidebar restructures to MONITOR/SETTINGS/WORKFLOWS sections when on this page |
| C-4 | Policy / SOP (04) | P0 | PASS | Full co-build intake form renders cleanly — Sprint-IA-04 confirmed working |
| C-5 | Training Material (05) | P0 | PASS | Renders cleanly |
| C-6 | FRM Risk Register (06) | P0 | PASS | Renders cleanly |
| D-1 | Proposal (07) | P0 | PASS | Renders cleanly |
| D-2 | PPT Pack (08) | P0 | PASS | Renders cleanly |
| D-3 | Due Diligence (09) | P0 | PASS | Renders cleanly |
| D-4 | Sanctions Screening (10) | P0 | PASS | Renders and workflow ran to completion; 2 P1 product gaps noted |
| D-5 | Transaction Testing (11) | P0 | PASS | Renders cleanly |
| E-1 | Case Tracker (12) | P0 | PASS | Renders cleanly |
| E-2 | Team (13) | P0 | PASS | Renders cleanly |
| E-3 | Settings (14) | P0 | PASS | Renders cleanly |
| E-4 | Activity Log (15) | P0 | PASS | Renders cleanly |
| E-5 | Workspace (16) | P0 | PASS | Renders — should present list-to-select UI |

## P0 Failures (blocks QA_APPROVED)
None.

## P1 Observations (documented, does not block)

### OBS-01 — Sidebar label: "Setting" not "Setup" (page 00)
Page 00_Setup.py renders but sidebar shows "Setting". Minor label fix needed.

### OBS-02 — Sidebar label: "Investigation Report" not "Investigation" (page 02)
Pre-existing deferred item. No change.

### OBS-03 — 01_ prefix collision (pages 01_Engagements + 01_Scope)
Both pages visible as separate entries. Streamlit tolerating on this machine but filesystem sort order is not guaranteed. Rename 01_Scope.py required before production.

### OBS-04 — Persona Review sidebar restructure (page 03)
When on Persona Review, sidebar reorganises to MONITOR/SETTINGS/WORKFLOWS with workflow types listed inline. Significant navigation shift — may confuse users. Sprint-UX-WIRE-01 item.

### OBS-05 — Page dimming on state transitions (Sanctions page observed)
Full page re-run on each state change causes visible dimming. Sprint-UX-WIRE-01 (@st.fragment) will fix this.

### OBS-06 — Sanctions: disposition hits not shown inline (page 10)
Workflow generated the final memo but never showed the individual citation hits for review before generating. User cannot review/accept/reject each hit before the memo is produced. Review step missing.

### OBS-07 — Sanctions: no verifiable evidence in report (page 10)
Report describes citations but contains no captured source records (OFAC entry copy, UN document, URL + timestamp). For a compliance product, each citation needs attached evidence. Especially critical in knowledge_only mode where citations are model-generated, not real API hits.

### OBS-08 — Word output not available (all pages)
All outputs render as markdown/text only. No .docx download button present. AK confirmed: Word formatting is a prime requirement for all outputs. A "Preferred output format" selector (Word / Markdown / both) must be in every intake form.

### OBS-09 — No "Mark Complete / Close" button (all pages)
Engagements, workflows, and cases have no user-facing button to mark them complete/closed. State machine has terminal states but no UI trigger.

### OBS-10 — Workspace: no list-to-select UI (page 16)
Workspace should present a selectable list of workspaces/cases. Current layout does not.

### OBS-11 — Setup page slow to load (page 00)
Noticeably slower than other pages. Likely heavy import or initialisation at module level.

## BA Requirements Captured This Session

**BA-REQ-FORMATTING-01:** All workflow outputs must generate .docx as primary deliverable. "Preferred output format" selector in every intake. Word formatting quality is prime — not optional.

**BA-REQ-CLOSE-01:** All engagements, workflows, and cases must have a user-facing "Mark Complete / Close" button to explicitly set terminal state from the UI.

## QA Signal
QA_APPROVED
Reason: All 19 P0 steps passed. No page crashed or showed blank screen. Sprint-UX-ERR-01 error boundaries confirmed working (no silent crashes). 11 P1 observations documented for sprint backlog.
