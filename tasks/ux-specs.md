# UX Specs — GoodWork Forensic AI (Streamlit)

**Author:** /ux agent, Session 017
**Platform:** Streamlit — desktop primary (1280px+). Mobile (375px) noted but Streamlit has limited responsive support; mobile notes flag what breaks, not ideal fixes.
**Design system:** tasks/design-system.md — Montserrat, #D50032, warm neutrals, light theme.
**BA source:** tasks/ba-logic.md — sole practitioner, CXO output audience, multi-session cases, no client-facing output without review.

---

## Status Legend
- DRAFT — written, not yet reviewed by AK
- APPROVED — AK confirmed
- REVISION_NEEDED — feedback received

---

### UX-001 — Landing Page (app.py)

- Status: DRAFT
- Task: P8-04-APP

**User goal:** Orient quickly and navigate to the right workflow.
**Entry point:** `streamlit run app.py` — first screen after startup.

**States:**

- **Default:** GoodWork logo (280px wide, centred-left), subtitle "Forensic AI — Internal Consulting Platform", RESEARCH_MODE banner (warning if knowledge_only, success if live), three-column workflow menu (Investigation / Compliance / Business), each column listing clickable workflow names.
- **Loading:** None — landing is static, no API calls.
- **Error:** If `session.py` bootstrap fails (missing .env), show `st.error("Configuration missing — check .env file")` with link to README. No blank screen.
- **Empty:** N/A — landing is always populated.
- **Success:** User clicks a workflow name → Streamlit navigates to the corresponding page (sidebar page link).

**Mobile (375px):**
- Three columns collapse to a single vertical list. Workflow names become full-width buttons.
- Logo scales to 180px to avoid overflow.
- RESEARCH_MODE banner stacks below logo.

**Interaction rules:**
- RESEARCH_MODE banner: knowledge_only → `st.warning()` with amber left-border style. Live → `st.success()` with green. Rendered before any workflow content on every page (injected by bootstrap).
- Workflow names in the three-column grid are NOT buttons — they are markdown links to sidebar pages. `[FRM Risk Register](/6_FRM)` pattern. Streamlit sidebar handles active state.
- Logo: static image, no hover state, no link.

---

### UX-002 — FRM Risk Register (pages/6_FRM.py)

- Status: DRAFT
- Task: P8-06-FRM

**User goal:** Generate a structured fraud risk register for a client, review each risk item, and download the final report.
**Entry point:** Sidebar → "FRM Risk Register" OR landing page workflow list.

**Stage machine:** `frm_stage` ∈ {intake, running, reviewing, done}

---

#### Stage 1: Intake

**States:**
- **Default:** `frm_intake_form()` renders. Fields: Client name, Industry (dropdown from taxonomy + free text), Jurisdiction(s) (multi-select), Company size, FRM modules to include (multi-checkbox with dependency warnings). Submit button: "Start Analysis".
- **Loading:** N/A — form is synchronous.
- **Error (validation):** If required fields empty on submit → `st.warning("Please complete all required fields before proceeding.")` — no page navigation, form stays.
- **Error (module dependency):** If Module 3 selected but Module 2 not selected → `st.warning("Module 3 depends on Module 2 — Module 2 has been added automatically.")` inline below the checkbox, Module 2 checkbox auto-checked.
- **Empty:** N/A.
- **Success:** Submit → `frm_stage = "running"`, page re-renders to Stage 2.

**Mobile (375px):** Form stacks vertically. Multi-checkbox for modules becomes scrollable. Submit button full-width.

**Interaction rules:**
- Module dependency enforcement fires on checkbox change (not only on submit).
- "Start Analysis" button: primary style (#D50032). Disabled if required fields empty (grey, not red).
- No "Back" button from Stage 2 onward — pipeline is not reversible.

---

#### Stage 2: Running

**States:**
- **Default:** `st.spinner("Running analysis...")` with `run_in_status()` log below. Log entries use severity: `st.error()` for CRITICAL, `st.warning()` for WARNING, `st.info()` for INFO.
- **Loading:** Spinner persists for entire pipeline duration (2-3 min expected). Log updates in real time via `st.empty()`.
- **Error (pipeline crash):** If `PipelineError` raised → `st.error("Pipeline failed: [error message]")`. Show "Start Over" button. Do NOT show partial results as final.
- **Error (RESEARCH_MODE=knowledge_only):** At stage start, show `st.warning("Running in Knowledge Only mode — no live regulatory data. Citations will be limited.")` as a persistent banner above spinner.
- **Empty:** N/A.
- **Success:** Pipeline completes → `frm_stage = "reviewing"`, page re-renders to Stage 3.

**Mobile (375px):** Spinner and log stack vertically. Log text wraps. No layout changes needed.

**Interaction rules:**
- User cannot interact during running state — no buttons exposed except browser back (which would lose the run).
- Log is append-only during run. Max visible lines: 20 (older lines scroll off). Full log in `audit_log.jsonl`.
- If pipeline returns 0 risk items → treat as CRITICAL severity event in log, advance to reviewing stage with empty state warning.

---

#### Stage 3: Reviewing

**States:**
- **Default:** One `st.expander` per risk item, collapsed by default. Header shows: Risk Title | Module | Rating (1-25 as colored badge). Below expanders: "Finalise Register" button (disabled until all items actioned).
- **Loading:** N/A — review is synchronous user action.
- **Error (no items):** `st.warning("No risk items were generated. This may occur in knowledge_only mode with minimal intake data. You can still finalise with an empty register or start over.")` + two buttons: "Finalise Anyway" / "Start Over".
- **Empty:** Same as error (no items) — not a blank expander list.
- **Success (all actioned):** "Finalise Register" button enables. User clicks → `frm_stage = "done"`.

**Expander content (expanded state):**
```
Risk Title: [title]
Module: [module name]
Description: [description]
Likelihood: [1-5] | Impact: [1-5] | Rating: [1-25]
Regulatory basis: [text]
Recommendations: [bullet list]

Action:  [ Approve ▾ ]   [optional note field]
```
Selectbox options: Approve / Flag for revision / Skip.
"Flag for revision" reveals a text input: "Describe the issue". Required before expander can be closed with Flag selected.

**Rating badge colors:**
- 1-8 (Low): green background
- 9-15 (Medium): amber background
- 16-25 (High): red (#D50032) background

**Mobile (375px):** Expanders stack full-width. Badge stays inline with title. Note field full-width below selectbox.

**Interaction rules:**
- "Finalise Register" button: disabled (grey) until every expander has a selectbox value set (Approve / Flag / Skip). No partial finalisations.
- Flag without note → `st.warning("Please describe the issue before continuing.")` inline in expander.
- Approved count / Total count shown as `st.metric()` above expanders: "Items Approved: 4/12".
- User can re-open expanders and change action at any time before finalising.

---

#### Stage 4: Done

**States:**
- **Default:** `st.success("Risk Register complete.")` banner. Case ID chip. Download button: "Download final_report.en.md". Link to cases/{id}/ folder path (plain text — not a hyperlink since local).
- **Loading:** `run_frm_finalize()` call — show spinner "Assembling report..." before success banner.
- **Error (finalize fails):** `st.error("Report assembly failed: [error]")`. Show "Retry Finalise" button.
- **Empty:** N/A.
- **Success:** Report file exists in cases/{id}/. Download button active.

**Mobile (375px):** Success banner full-width. Download button full-width below.

**Interaction rules:**
- `st.download_button()` serves `final_report.en.md` as a file download.
- "Start New Case" button below download — resets `frm_stage = "intake"` and clears session state for this workflow.
- Case ID rendered in `.case-id-chip` CSS class (monospace, subtle background).

---

### UX-003 — Generic Workflow Page Shell (applies to pages 2,3,4,5,7,8,0,11,12,13)

- Status: DRAFT
- Task: P8-08a..j

**User goal:** Complete a specific workflow (Investigation, DD, Proposal, etc.) and download the output.
**Entry point:** Sidebar navigation or landing page workflow list.

**Shell pattern — 3 zones:**
```
┌─────────────────────────────────────────┐
│ Zone A: Intake Form                     │
│ generic_intake_form() — workflow-specific│
├─────────────────────────────────────────┤
│ Zone B: Pipeline Status                 │
│ run_in_status() — appears after submit  │
├─────────────────────────────────────────┤
│ Zone C: Output + Download               │
│ appears after pipeline completes        │
└─────────────────────────────────────────┘
```

**States:**

- **Default (pre-submit):** Zone A visible only. Zone B and C hidden.
- **Loading (pipeline running):** Zone A collapses (st.expander, closed). Zone B visible with spinner + severity log. Zone C hidden.
- **Error (pipeline):** Zone B shows `st.error()` with message. "Start Over" button resets to default. Zone C hidden.
- **Error (validation):** Zone A shows inline `st.warning()`. Page stays in default state.
- **Empty (no output):** Zone C shows `st.warning("No output was generated. Check the pipeline log above.")`. Download button hidden.
- **Success:** Zone C shows `st.success()`, case ID chip, `st.download_button()`.

**Mobile (375px):** All three zones stack vertically. Form inputs full-width. No layout difference — Streamlit is single-column on mobile.

**Interaction rules:**
- "Run [Workflow Name]" button: primary (#D50032). Disabled during pipeline run.
- Pipeline log: severity-tagged (CRITICAL/WARNING/INFO) per ARCH-INS-01.
- After success: "Start New Case" button resets page state.
- Zone A collapses into a closed `st.expander` titled "Intake Summary" during run — intake data is preserved but not editable.

**Sanctions-specific override (page 12):**
- If `RESEARCH_MODE=knowledge_only`: show `st.error("WARNING: Sanctions screening in knowledge_only mode does not query live OFAC/UN/EU lists. Results cannot be used for compliance purposes.")` with checkbox "I understand this is not a live screening — proceed anyway." Run button disabled until checkbox ticked.

**Proposal-specific addition (page 7):**
- After success: `st.checkbox("Also generate PPT prompt pack for this engagement?")`. If checked → `frm_stage` equivalent advances to PPT pack workflow using same case_id.

---

### UX-004 — Case Tracker (pages/9_Case_Tracker.py)

- Status: DRAFT
- Task: P8-09a + ARCH-INS-02

**User goal:** See all cases at a glance, check status, and download deliverables without navigating to the file system.
**Entry point:** Sidebar → "Case Tracker".

**States:**

- **Default:** Full-width `st.dataframe()` with columns: Case ID | Workflow | Status | Last Updated | Actions. Sorted by Last Updated descending (newest first).
- **Loading:** `st.spinner("Loading cases...")` while reading `cases/index.json`.
- **Error (index missing):** If `cases/index.json` absent AND `cases/` empty → `st.info("No cases yet. Run a workflow to create your first case.")` with link to landing page. Not an error — it's an empty state.
- **Error (index missing, cases exist):** Backfill: scan `cases/*/state.json` once, rebuild index.json, then render. Show `st.warning("Case index rebuilt from folder scan.")`.
- **Empty:** Same as "index missing, cases empty" above.
- **Success (row selected):** Expander below table shows: all deliverables for that case, download buttons per file, path to audit_log.jsonl.

**Status badge colors (in dataframe):**
- `OWNER_APPROVED` / `DELIVERABLE_WRITTEN` → green pill
- `INTAKE_CREATED` / in-progress states → blue pill
- `PIPELINE_ERROR` → red pill
- `PM_REVISION_REQUESTED` / `PARTNER_REVISION_REQ` → amber pill

**Mobile (375px):** Table scrolls horizontally. Status column and Actions column pinned right. Case ID truncated to 12 chars with tooltip.

**Interaction rules:**
- Click row → expander opens below table row (not a modal). One expander open at a time.
- Download buttons in expander: one per deliverable file (`final_report.en.md`, `final_report.ar.md` if present).
- "Refresh" button top-right of table: re-reads `cases/index.json`.
- `st.dataframe()` column widths: Case ID 160px, Workflow 180px, Status 140px, Last Updated 160px, Actions auto.
- PIPELINE_ERROR cases: expander shows error.json content with "What to do" guidance text (not raw stack trace).

---

### UX-005 — Settings / Firm Profile (pages/settings.py)

- Status: DRAFT
- Task: P8-10a

**User goal:** Update firm profile (name, logo path, pricing, team credentials) without re-running the setup wizard.
**Entry point:** Sidebar → "Settings".

**States:**

- **Default:** Two-column layout — label left (40% width), input right (60% width). Fields: Firm Name, Logo Path, Default Currency (AED/USD/SAR select), Pricing Model (T&M / Lump Sum / Retainer select), T&M Day Rate, T&M Hour Rate. "Save" button bottom-right. Current values pre-loaded from `firm_profile/firm.json`.
- **Loading:** On page load, `st.spinner("Loading firm profile...")` while reading firm.json.
- **Error (file read):** If `firm_profile/firm.json` missing → `st.warning("Firm profile not yet set up. Fill in the fields below to create it.")`. Fields render empty, not broken.
- **Error (save fails):** `st.error("Save failed: [error]")`. File not written. "Try Again" button.
- **Empty:** Same as file read error — empty fields, not blank page.
- **Success:** `st.success("Firm profile saved.")` for 3 seconds (use `st.empty()` with time.sleep(3) then clear), then return to default state showing saved values.

**Mobile (375px):** Two-column collapses to single column — labels above inputs. Save button full-width at bottom.

**Interaction rules:**
- "Save" button: primary (#D50032). Only enabled if Firm Name field is non-empty.
- Logo Path: `st.text_input()` — user types the path. No file picker (Streamlit `st.file_uploader` would copy to a temp path, not save to assets/). Add helper text: "Enter the path to your logo file relative to the repo root (e.g. assets/logo.png)".
- Pricing fields: only visible when Pricing Model = T&M. Hide when Lump Sum or Retainer selected.
- No delete or reset button — settings are not destructive. User edits and saves.

---

### UX-006 — Document Upload (P8-11, inline on Investigation / FRM / DD / TT pages)

- Status: DRAFT
- Task: P8-11a

**User goal:** Upload case documents before running the pipeline so the agent reads them during draft generation.
**Entry point:** Inline in Zone A (intake form) on Investigation, FRM, DD, TT pages — below the intake fields, above the Run button.

**States:**

- **Default:** `st.file_uploader("Upload case documents (optional)", accept_multiple_files=True, type=["pdf","docx","txt","xlsx"])`. Below it: "Uploaded documents will be read by the agent during analysis. Max 10MB per file."
- **Loading (upload):** Streamlit handles file upload progress natively. After upload: show list of uploaded file names as `st.caption()` entries.
- **Error (file too large):** Streamlit rejects files >200MB by default. Add `st.warning("Maximum file size is 10MB per document.")` as static helper below uploader.
- **Error (registration fails):** If `DocumentManager.register_document()` raises → `st.error("Failed to register [filename]: [error]")`. Other files unaffected.
- **Empty:** No files uploaded → uploader shows "Drag and drop files here / Browse files". Pipeline runs without document context (knowledge-only for that case).
- **Success:** Files uploaded and registered → list renders as: `✓ [filename] — registered`. Run button enables normally.

**Mobile (375px):** File uploader is full-width. File list stacks vertically. No layout changes needed.

**Interaction rules:**
- Document registration happens on upload (before Run) — not deferred.
- Max 10 files per case (practical limit, not enforced by Streamlit natively — add count check: if >10, `st.warning("Maximum 10 documents per case.")`).
- Accepted types: pdf, docx, txt, xlsx only. Shown in uploader label.
- Uploaded file names displayed with file size: `report.pdf — 2.3 MB`.
- If user removes a file from uploader, do NOT un-register from DocumentManager — document index is append-only. Show note: "Removed from uploader — already registered in case index."

---

## Open UX Decisions (AK Review Required)

| ID | Question | Options | Impact |
|---|---|---|---|
| UX-D-01 | Should intake form collapse during pipeline run? | A: Collapse to expander (current spec) — B: Hide entirely | Low — affects Zone A visibility during run |
| UX-D-02 | Case Tracker: click-to-expand row OR separate detail panel? | A: Expander below row (current spec) — B: Side panel | Medium — affects layout complexity |
| UX-D-03 | After FRM "Start New Case" — clear all session state or keep firm/intake defaults? | A: Clear all — B: Keep firm name, clear case data | Low — UX convenience |
| UX-D-04 | Should Settings page show team member bios (from firm_profile/team.json)? | A: Yes, extend settings — B: Separate "Team" page | Medium — scope of Settings page |
