# Smoke Test Spec — Page Load Check
# Verify all 17 pages load without crash after Sprint-UX-ERR-01

Status: PENDING
Generated: 2026-04-23
Tester: AK (live Streamlit app at http://localhost:8501)

---

## Pre-conditions
- `streamlit run app.py` running at http://localhost:8501
- No project/engagement needs to be active — just navigate and check render

## Pass criteria per page
- PASS: Page renders any visible content (sidebar, title, form, or message)
- FAIL: Blank white screen OR red error panel with crash report path shown

---

## STEP-A — Sidebar navigation check

**A-1:** Open http://localhost:8501. Verify the sidebar shows page links. Count visible pages.
Expected: ~16–17 pages listed.

---

## STEP-B — Page load: Setup + Engagements

**B-1 Setup (00):** Click "Setup" in sidebar. Verify page renders (firm profile form or setup prompt visible). PASS / FAIL

**B-2 Engagements (01):** Click "Engagements" in sidebar. Verify page renders (project list or "no projects" message visible). PASS / FAIL

---

## STEP-C — Page load: Core workflow pages

**C-1 Scope (01/17):** Click "Scope" in sidebar. Verify page renders. PASS / FAIL
*(Note: shares prefix 01_ with Engagements — may not appear or may shadow Engagements)*

**C-2 Investigation (02):** Click "Investigation" in sidebar. Verify page renders. PASS / FAIL

**C-3 Persona Review (03):** Click "Persona Review" in sidebar. Verify page renders. PASS / FAIL

**C-4 Policy SOP (04):** Click "Policy / SOP" in sidebar. Verify page renders. PASS / FAIL

**C-5 Training (05):** Click "Training" in sidebar. Verify page renders. PASS / FAIL

**C-6 FRM (06):** Click "FRM Risk Register" in sidebar. Verify page renders. PASS / FAIL

---

## STEP-D — Page load: Output + case pages

**D-1 Proposal (07):** Click "Proposal" in sidebar. Verify page renders. PASS / FAIL

**D-2 PPT Pack (08):** Click "PPT Pack" in sidebar. Verify page renders. PASS / FAIL

**D-3 Due Diligence (09):** Click "Due Diligence" in sidebar. Verify page renders. PASS / FAIL

**D-4 Sanctions (10):** Click "Sanctions" in sidebar. Verify page renders. PASS / FAIL

**D-5 Transaction Testing (11):** Click "Transaction Testing" in sidebar. Verify page renders. PASS / FAIL

---

## STEP-E — Page load: Management pages

**E-1 Case Tracker (12):** Click "Case Tracker" in sidebar. Verify page renders. PASS / FAIL

**E-2 Team (13):** Click "Team" in sidebar. Verify page renders. PASS / FAIL

**E-3 Settings (14):** Click "Settings" in sidebar. Verify page renders. PASS / FAIL

**E-4 Activity Log (15):** Click "Activity Log" in sidebar. Verify page renders. PASS / FAIL

**E-5 Workspace (16):** Click "Workspace" in sidebar. Verify page renders. PASS / FAIL

---

## STEP-F — Crash reporter check (optional)

If any page shows a red error panel:
**F-1:** Note the crash report path shown (e.g. `logs/crash_reports/crash_XXXX.json`).
**F-2:** Tell Claude the page name and the error text in the "Show error details" expander.
This confirms Sprint-UX-ERR-01 error boundaries are working and gives a diagnosis path.

---

## Expected result
All 17 pages: PASS
Known risk: 00_Setup, 01_Engagements, 16_Workspace were crashing as of Session 035.
Sprint-UX-ERR-01 error boundaries now catch those — FAIL pages will show a crash panel, not a blank screen.
