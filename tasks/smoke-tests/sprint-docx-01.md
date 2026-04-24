# Smoke Test Spec — Sprint-DOCX-01
# Verify .docx and .md download buttons appear in Done Zone after FRM workflow run

Status: PENDING
Sprint: Sprint-DOCX-01
AC reference: DOCX-03
Generated: 2026-04-24
Tester: AK (live Streamlit app at http://localhost:8501)

---

## Pre-conditions
- `streamlit run app.py` running at http://localhost:8501
- API credits available (Anthropic key active)
- RESEARCH_MODE=knowledge_only in .env (no Tavily required)
- No active engagement needed — start fresh

## Pass criteria
- PASS: Both download buttons visible in Done Zone; files download without error; no crash
- FAIL: Buttons missing, file corrupt, page crashes, or regression on non-DOCX pages

---

## STEP-A — Start FRM workflow

**A-1:** Open http://localhost:8501. Click "FRM Risk Register" in sidebar.
Expected: FRM intake form renders without crash. PASS / FAIL

**A-2:** Fill in minimal intake — client name, industry (any), jurisdiction (UAE), select 1–2 FRM modules.
Expected: Form accepts input, no validation errors. PASS / FAIL

**A-3:** Click Run (or equivalent trigger button).
Expected: Pipeline starts, forensic tip panel visible during run, progress indicator active. PASS / FAIL

---

## STEP-B — Pipeline completion

**B-1:** Wait for pipeline to complete (knowledge_only — should finish in under 60 seconds).
Expected: Done Zone renders below the run button. PASS / FAIL

**B-2:** Confirm Done Zone shows a success/completion message or final report preview.
Expected: No red error panel, no crash report path. PASS / FAIL

---

## STEP-C — Download buttons (DOCX-03 core check)

**C-1:** Verify "Download .docx Report" button is visible in Done Zone.
Expected: Button present, labelled clearly. PASS / FAIL

**C-2:** Click "Download .docx Report". File download dialog appears or file saves to Downloads.
Expected: File downloads without browser/app error. PASS / FAIL

**C-3:** Open downloaded .docx in Word or LibreOffice.
Expected: File opens without corruption error or "file format not supported" warning. PASS / FAIL

**C-4:** Verify "Download Markdown backup" button is visible in Done Zone.
Expected: Button present with that exact label. PASS / FAIL

**C-5:** Click "Download Markdown backup". File downloads.
Expected: .md file saves without error. PASS / FAIL

---

## STEP-D — Regression check

**D-1:** Navigate to "PPT Pack" page (does not use done_zone.py).
Expected: Page renders normally — no crash, no missing imports. PASS / FAIL

**D-2:** Navigate to "Due Diligence" page.
Expected: Page renders normally. PASS / FAIL

**D-3:** Navigate back to FRM page.
Expected: Page reloads cleanly — no stale session state error. PASS / FAIL

---

## STEP-E — Crash reporter check (if any step failed)

If any step above shows a red error panel:
**E-1:** Note the crash report path (e.g. `logs/crash_reports/crash_XXXX.json`).
**E-2:** Report page name and error text from "Show error details" expander.
This gives diagnosis path without a full debug session.

---

## Expected result
All steps: PASS → Sprint-DOCX-01 COMPLETE → merge feature/sprint-docx-01-download-buttons → main

## On failure
Report which step failed. If C-1/C-2/C-3 fail: Done Zone wiring broken — debug done_zone.py.
If C-4/C-5 fail: Markdown download button missing — check done_zone render logic.
If D-1/D-2 fail: Regression in non-DOCX pages — check recent imports or shared components.
