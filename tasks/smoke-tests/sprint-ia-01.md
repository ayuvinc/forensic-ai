---
sprint_id: sprint-ia-01
name: Sprint-IA-01 — Navigation Restructure + Multi-Workflow Workspace
branch: feature/sprint-fe-triage
built_by: junior-dev (Session 037)
total_steps: 17
p0_count: 14
p1_count: 3
p0_fail_blocks_qa: true
---

## STEP-00
id: setup-00
severity: P0
area: Setup
prereq: none
action: "In the forensic-ai directory, run: `python3 scripts/seed_test_engagement.py`"
expect: "Terminal prints: 'Seed complete. Run: streamlit run app.py' — no Python errors"
confirm: "What was the last line the script printed?"
diagnose_0:
  - "What error message did you see? Paste the first line of the traceback."
  - "Does `cases/abc-corp-test-engagement/` exist on disk? (check in Finder or ls)"

## STEP-01
id: startup-01
severity: P0
area: Startup
prereq: none
action: "Run: `streamlit run app.py` in the forensic-ai directory"
expect: "Browser tab opens at localhost:8501 with no Python traceback and no blank/white page"
confirm: "What is the first page title shown in the browser tab or main content area?"
diagnose_0:
  - "Is the error in the terminal (Python) or in the browser? Copy the first error line."
  - "Does the terminal show 'You can now view your Streamlit app' before the error?"

## STEP-02
id: sidebar-02
severity: P0
area: Sidebar
prereq: startup-01
action: "Look at the left sidebar. Count the bold section header labels (MAIN, PROPOSALS, etc.)"
expect: "Exactly 5 section headers are visible: MAIN, PROPOSALS, MONITOR, SETTINGS, WORKFLOWS"
confirm: "Read out the 5 headers exactly as they appear in the sidebar."
diagnose_0:
  - "How many section headers do you see? List them as they appear."
  - "Is there a section with pages listed but no header label (pages floating ungrouped)?"

## STEP-03
id: sidebar-03
severity: P0
area: Sidebar
prereq: sidebar-02
action: "Look at the MAIN section in the sidebar. Count the page links inside it."
expect: "MAIN contains exactly 2 links: 'Engagements' and 'Workspace'"
confirm: "Are both 'Engagements' and 'Workspace' visible, in that order?"
diagnose_0:
  - "What links appear under MAIN? List them."
  - "Is there any page link that shows a filename prefix (like '01 Engagements' instead of 'Engagements')?"

## STEP-04
id: sidebar-04
severity: P0
area: Sidebar
prereq: sidebar-02
action: "Look at the PROPOSALS section in the sidebar."
expect: "PROPOSALS contains exactly 2 links: 'Scope' and 'Proposals'. The word 'b' does NOT appear anywhere."
confirm: "Does it say 'Scope' (not '1b Scope' or 'b Scope')?"
diagnose_0:
  - "What exact text appears for the first link under PROPOSALS?"
  - "Is there any link that contains 'b' as part of its label?"

## STEP-05
id: sidebar-05
severity: P0
area: Sidebar
prereq: sidebar-02
action: "Look at the MONITOR and SETTINGS sections."
expect: "MONITOR has 'Case Tracker' and 'Activity Log'. SETTINGS has 'Team' and 'Settings'."
confirm: "Any unexpected entries in either section?"
diagnose_0:
  - "Which section is wrong — MONITOR or SETTINGS? What do you see instead?"

## STEP-06
id: sidebar-06
severity: P0
area: Sidebar
prereq: sidebar-02
action: "Look at the WORKFLOWS section. Count the page links."
expect: "9 workflow links visible: Investigation Report, FRM Risk Register, Due Diligence, Sanctions Screening, Transaction Testing, Policy / SOP, Training Material, PPT Pack, Persona Review"
confirm: "Is 'Persona Review' visible in the WORKFLOWS section?"
diagnose_0:
  - "How many links are in WORKFLOWS? List any that seem missing."
  - "Is 'Persona Review' absent, or is it present but under a different name?"

## STEP-07
id: sidebar-07
severity: P0
area: Sidebar
prereq: sidebar-02
action: "Scan the entire sidebar. Look for any link labelled '00 Setup' or 'Setup'."
expect: "'00 Setup' and 'Setup' are NOT visible anywhere in the sidebar"
confirm: "Confirmed — no Setup link anywhere in the sidebar?"
diagnose_0:
  - "Where does the Setup link appear — which section?"
  - "Does clicking it redirect, or does it load a setup form?"

## STEP-08
id: pages-08
severity: P0
area: Pages
prereq: sidebar-02
action: "Click 'Engagements' in the sidebar."
expect: "Page loads showing engagement list and a 'New Engagement' button — no error panel, no traceback"
confirm: "Does the page show a left panel with engagement cards and a right detail panel?"
diagnose_0:
  - "What error text appears? Is it a Python exception or a missing import message?"
  - "Does the page show a red 'Page failed to load' banner?"

## STEP-09
id: pages-09
severity: P0
area: Pages
prereq: sidebar-02
action: "Click 'Proposals' in the sidebar."
expect: "Page loads AND shows a blue/info banner near the top about 'Arc 1 — Proposal: Step 2 of 3'"
confirm: "What does the banner say exactly? (read the first few words)"
diagnose_0:
  - "Does the page load without errors but the banner is missing?"
  - "Or does the page fail to load entirely? Paste the first error line."

## STEP-10
id: pages-10
severity: P0
area: Pages
prereq: sidebar-02
action: "Click 'Scope' in the sidebar."
expect: "Page loads — no error. The browser tab or page title should NOT say 'b Scope' or '1b Scope'."
confirm: "What is the page heading shown in the main content area?"
diagnose_0:
  - "Does the page crash or load incorrectly?"
  - "What exact text appears as the page title or heading?"

## STEP-11
id: pages-11
severity: P1
area: Pages
prereq: sidebar-02
action: "Click 'Case Tracker' in the sidebar, then 'Activity Log'."
expect: "Both pages load without error panels"
confirm: "Any warnings or partial loads on either page?"
diagnose_0:
  - "Which page failed — Case Tracker or Activity Log (or both)?"
  - "What error text appears?"

## STEP-12
id: pages-12
severity: P1
area: Pages
prereq: sidebar-02
action: "Click 'Investigation Report' under WORKFLOWS. Then click 'FRM Risk Register'."
expect: "Both workflow pages load without error panels"
confirm: "Any warnings visible on either page?"
diagnose_0:
  - "Which page failed?"
  - "What error text appears? Is it a missing import or a missing session key?"

## STEP-13
id: pages-13
severity: P0
area: Pages
prereq: sidebar-02
action: "Click 'Workspace' in the sidebar."
expect: "Workspace page loads — shows engagement picker or active engagement header without error"
confirm: "Does it show an engagement picker dropdown, or does it show an engagement header directly?"
diagnose_0:
  - "What error panel text appears?"
  - "Is the error 'Page failed to load' or a different message?"

## STEP-14
id: multi-wf-14
severity: P0
area: Multi-Workflow
prereq: pages-08
action: "On the Engagements page, click the 'abc-corp-test-engagement' card in the left panel (if visible). If not visible, click 'New Engagement' — we'll check the selectbox instead."
expect: "Right panel shows engagement detail with a 'Run Workflow' section containing a selectbox"
confirm: "Is the selectbox visible in the right panel?"
diagnose_0:
  - "Is the left panel empty (no engagement cards shown)? The seed script may not have registered it."
  - "Does clicking the card change the right panel, or does nothing happen?"

## STEP-15
id: multi-wf-15
severity: P0
area: Multi-Workflow
prereq: multi-wf-14
action: "Open the 'Select workflow' dropdown in the engagement detail panel. Scroll through all options."
expect: "'Persona Review' is visible as one of the workflow options in the selectbox"
confirm: "How many options are in the dropdown? Is 'Persona Review' the last one?"
diagnose_0:
  - "What options DO appear in the dropdown? List them."
  - "Does the dropdown show 8 items (missing Persona Review) or 9?"

## STEP-16
id: workspace-16
severity: P0
area: Workspace — Multi-Workflow Outputs
prereq: pages-13
action: "In the Workspace page, select 'abc-corp-test-engagement' from the picker (or navigate to it). Look for an expander labelled 'Workflow Outputs'."
expect: "'Workflow Outputs (3 runs)' expander is visible and expanded. Inside: 3 sections — Investigation Report, FRM Risk Register, Due Diligence — each with a download button."
confirm: "Do the download buttons appear? What file extension do they show (.md or .docx)?"
diagnose_0:
  - "Is the 'Workflow Outputs' expander missing entirely, or present but empty?"
  - "If empty: does it say 'No workflows run yet'? The seed data may not have been picked up."
  - "If expander is missing: the 16_Workspace.py edit may not have taken effect — check git status."
