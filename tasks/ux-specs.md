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

- Status: APPROVED
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

- Status: APPROVED
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

- Status: APPROVED
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

- Status: APPROVED
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

- Status: APPROVED
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

- Status: APPROVED
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

## Open UX Decisions — RESOLVED

| ID | Decision | AK Choice |
|---|---|---|
| UX-D-01 | Intake form during pipeline run | **Option A** — Collapse to closed expander "Intake Summary". User can re-open to check inputs, cannot edit. |
| UX-D-02 | Case Tracker detail view | **Option A** — Expander below clicked row. Native Streamlit, no side panel hacks. |
| UX-D-03 | "Start New Case" reset scope | **Option B** — Keep firm name pre-filled. Clear client name, jurisdiction, company size, module selections. |
| UX-D-04 | Team bios in Settings | **Option B** — Separate "Team" page in sidebar. Settings stays focused on firm config (name, pricing, currency). |

All 4 decisions approved by AK — 2026-04-16. UX specs are APPROVED. Junior-dev may build.

---
## UX Review — Session 024 (2026-04-19)
---

### UX-007 — Navigation and Information Architecture

**Current state:** 14 pages numbered with gaps (0, 2–13, settings unnumbered). Streamlit renders them in filename-sort order, so the sidebar shows: Scope, Investigation, Persona Review, Policy SOP, Training, FRM, Proposal, PPT Pack, Case Tracker, Team, Due Diligence, Sanctions, Transaction Testing, Settings. There is no visual grouping in the sidebar separating Investigation, Compliance, and Business categories.

**Issues:**
- The gaps in numbering (no page 1, jump from 0 to 2) are confusing. Page 0 (Scope) sits above Investigation but its purpose as "always start here" is not stated anywhere on the page itself.
- "Scope" is the correct entry point for a new engagement, but nothing in the sidebar or landing page makes this the recommended first step. A new user has no signal that Scope precedes Investigation.
- Pages 10 (Team) and 11–13 (DD, Sanctions, TT) appear below Case Tracker in the sidebar. The Case Tracker is a utility, not a workflow — it sitting in the middle of the workflow list breaks the grouping logic.
- "Settings" has no number so it sorts alphabetically after all numbered pages — that is actually correct for a utility, but it is visually disconnected from the "Team" page (page 10) which is also a settings-class utility. A user expecting to find Team near Settings will not find it.
- The landing page three-column grid lists workflow names as plain markdown, not as links. In the current code (`app.py` lines 61–71), they are markdown bullet lists — not clickable navigation.

**Suggested changes:**
  - Renumber pages to eliminate gaps and create logical groupings: 01–03 Investigation, 04–06 Compliance, 07–09 Business, 10 Tracker. Move settings-class pages (Team, Settings) to a distinct namespace (e.g. prefix `99_` or `00_` so they sort to edges).
  - Add a sidebar section dividers using `st.sidebar.markdown("---")` and `st.sidebar.caption("INVESTIGATION")` etc. (Streamlit supports injecting HTML in sidebar via `unsafe_allow_html=True`; this can be injected from `session.py` bootstrap so it applies on every page).
  - Add a persistent "Start here for a new engagement" callout on the Scope page — a single `st.info()` at top: "Run Scope first for any new engagement to identify the right workflow and set up the case."
  - Make the landing page workflow names into `st.page_link()` calls (Streamlit 1.31+) so clicking navigates directly. If `st.page_link` is unavailable in the deployed version, use `st.markdown("[FRM Risk Register](6_FRM)")` with `unsafe_allow_html=False` pattern or display as instructions to click in sidebar.
  - Move Case Tracker to the end of the sidebar, just before Settings/Team.

**Priority:** Medium

---

### UX-008 — Intake Forms: Consistency, Missing Fields, and Validation UX

**Current state:** All non-FRM workflows use `generic_intake_form()` from `streamlit_app/shared/intake.py`. This renders five fields (client name, industry, jurisdiction, description, language) inside a `st.form`, with a "Start" submit button. FRM uses `frm_intake_form()` which adds employee count and module multiselect. The form submits and immediately transitions the page stage — there is no confirmation step between "Start" and "pipeline running."

**Issues:**
- The "Start" submit button label is generic. On every page, the form says "Start" regardless of whether the user is about to run a 2-minute investigation pipeline or a 30-second scoping exercise. This creates no expectation of what is about to happen or how long it will take.
- The generic intake description field (`st.text_area`) is labelled "Engagement description / scope" on all workflows. For a Due Diligence engagement, this field has a very different meaning than for a Proposal. The placeholder text is blank — users get no hint of what level of detail is expected.
- The FRM intake form's module dependency warning fires after submit (validation error rendered below form), not inline during selection. The BA spec (UX-002, stage 1) requires inline warning on checkbox change — the current `frm_intake_form` only validates at submit time via `_validate_module_order()`.
- The `generic_intake_form()` function lives inside a `st.form` block, which means all validation (including required-field checks) only fires on submit. If the user leaves "Client name" blank, they see the error after submit, the form clears, and they must re-type everything. This is standard Streamlit form behavior but is avoidable by not using `st.form` for non-batch-submission scenarios.
- Due Diligence page (`11_Due_Diligence.py`) shows `generic_intake_form()` first, then renders a second set of DD-specific fields (subject type, subject name, jurisdictions, etc.) only after `generic_intake_form` returns a CaseIntake. This two-phase render is visually jarring: the page loads with one form, user fills and submits it, then a second set of fields appears below. The user does not know the second set is coming.
- Settings (firm profile) collects `firm_name`, `logo_path`, `currency`, `pricing_model`, and T&M rates — but not the team member bios or T&C text that the proposal workflow needs (per MEMORY.md "First-Time Setup Wizard Extended Checklist"). These critical proposal inputs have no Streamlit UI path at all.

**Suggested changes:**
  - Rename the `generic_intake_form()` submit button from "Start" to a workflow-specific label passed as a parameter (e.g. `submit_label="Begin Scoping"`, `"Run Investigation"`, `"Draft Proposal"`). The function already takes `workflow_id` — use it to map to a label.
  - Add `placeholder` text to the description field in `generic_intake_form()` that is contextual per `workflow_id`. Map: `investigation_report` → "e.g. Suspected procurement fraud by vendor — 3 employees under review"; `due_diligence` → "e.g. Pre-acquisition DD on target entity, focus on financial and reputational risks"; `client_proposal` → "e.g. Full FRM assessment for a 500-person logistics company".
  - For FRM module dependency enforcement: move validation out of the post-submit path and into an `st.on_change` callback on the multiselect widget. Auto-add the required module and show `st.info("Module 2 added automatically — required by Module 3.")` inline below the multiselect without clearing the form.
  - For Due Diligence: merge the generic and DD-specific fields into a single combined form (`dd_intake_form()` equivalent to `frm_intake_form()`). This eliminates the two-phase render entirely.
  - Add a "Team" section to the Settings page (or expose a direct link to page 10 from Settings) with a note: "Team bios are required for proposal generation." This surfaces the gap rather than letting the proposal workflow silently generate without team context.
  - Consider removing `st.form` from `generic_intake_form()` and using individual widget + button pattern. Benefit: validation can fire per-field. Cost: more session_state management. Decision needed from AK — log as UX-D-05.

**Priority:** High

---

### UX-009 — Pipeline Progress Display

**Current state:** All pipelines run inside `run_in_status()` which wraps `st.status(label, expanded=True)`. Within the status block, individual agent progress events render as `st.info()`, `st.warning()`, or `st.error()`. The status block title updates to "label — complete" or "label — failed" when done. This is the correct pattern.

**Issues:**
- `st.status` renders as a collapsible panel with a spinner. When expanded=True the log events are visible, but on slower connections or large screens the status block can be cut off below the fold — the user sees the spinner but not the log messages without scrolling.
- All log messages use the format `[agent_name] message text`. The agent names are internal identifiers (`junior_analyst`, `pm_review`, `frm_page`) that are meaningful to a developer but not to Maher. A message like `[junior_analyst] Generating risk items for Module 2...` would be clearer as `[Consultant] Generating risk items for Module 2...` (matching the user-facing rename confirmed in MEMORY.md).
- There is no visual indication of overall pipeline progress (which stage are we on out of N stages). The log shows events in real time but Maher cannot tell if the pipeline is 10% done or 90% done. For a 2-3 minute wait, this matters.
- The FRM `running` stage displays a hard-coded `st.info()` count banner (`f"Running pipeline for {intake.client_name} — {len(selected_modules)} module(s)"`) that does not update as modules complete. This is not a live progress indicator — it is static.
- When a pipeline fails, the page shows `st.error("Pipeline failed: {e}")` plus a "Start Over" button. But the user cannot view the partial results or the audit log from the UI. They are told to check `audit_log.jsonl` manually, which requires terminal access.

**Suggested changes:**
  - Add a `st.progress()` bar above the status block in the `running` stage. For FRM: total steps = number of selected modules × 3 agents. For Investigation/DD/Proposal: total steps = 3 (Junior, PM, Partner). Increment on each `on_progress` INFO event. This requires counting expected events at pipeline start and passing the count into the page — or using a simpler approximation (update bar at 33%, 66%, 100% on known agent-start events).
  - Map agent internal identifiers to user-facing labels in `run_in_status()` or at the point of `PipelineEvent` construction: `junior_analyst` → "Consultant (Draft)", `pm_review` → "Consultant (Review)", `partner` → "Consultant (Sign-off)", `frm_page` → "FRM".
  - Add a static "Estimated time" line above the status block at the start of `running` stage: `st.caption("Estimated time: 2–4 minutes depending on module count and research mode.")` This sets expectations without requiring dynamic measurement.
  - On pipeline failure: add an expander "View pipeline log" that renders the last N log events captured during the failed run (store events in session_state during `on_progress` callbacks). This lets Maher see what failed without opening the terminal.

**Priority:** High

---

### UX-010 — Output Display and Download

**Current state:** The `done` stage on all workflow pages shows: `st.success("... complete — Case ID: ...")`, a `st.download_button()` for the markdown report, and two `st.markdown()` lines showing the case ID and local folder path. FRM also shows an `st.expander("Executive Summary")` with the `deliverable.executive_summary` text. Investigation and DD show only the download button with no inline preview.

**Issues:**
- Download serves `final_report.en.md` as raw markdown. Maher sees a download button but cannot preview the report content without downloading and opening it. For a 2-3 minute pipeline, seeing the output inline (even a truncated preview) is a significant quality-of-life improvement.
- The download file format is `.md`. The BA/MEMORY.md notes that primary client deliverables should be `.docx` and `.pptx`. The markdown download is a backup. But the UI only offers the markdown download — there is no path to a `.docx` in the current done stages. If `.docx` generation is implemented, the download UI needs to offer both.
- The `st.markdown(f"**Location:** `cases/{intake.case_id}/`")` line shows a local filesystem path. This is only useful if Maher knows where the app is running from. It is noise for a non-developer user and should be removed or placed inside a collapsed "Technical details" expander.
- The "Start New Case" button that resets the stage appears in the sidebar (e.g. `if st.sidebar.button("Start New Case"):`). But the sidebar button only appears once the stage is past "intake". On the `done` stage, Maher may want to start a new case — but the primary CTA for this is buried in the sidebar, not visible in the main content area. The natural next action should be a primary button in Zone C.
- FRM's done stage applies rewrite decisions (Haiku single-turn rewrites) inside the `done` stage render loop using `st.spinner("Finalizing and writing report...")`. This means the report assembly can be unexpectedly slow on the done stage — Maher may click "Finalize" and then wait 30+ seconds with only a generic spinner. There is no explanation of what is happening during this wait.

**Suggested changes:**
  - Add an inline report preview using `st.expander("Preview report", expanded=False)` in Zone C, containing `st.markdown(report_path.read_text())`. This renders the markdown formatted. Limit to first 3000 characters with a "Show full report in preview" toggle if the report is long.
  - Add a "Copy Case ID" button next to the case ID display (or render the case ID as selectable text). Maher frequently needs the case ID to navigate to the case in the tracker — a one-click copy removes friction.
  - Remove or collapse the `**Location:** cases/{id}/` line into a "Technical details" expander alongside the audit log path.
  - Add a "Start New Case" primary button at the bottom of Zone C in the main content area, in addition to the sidebar button. Label it "Start Another [Workflow Name]". This makes the next action obvious without requiring sidebar interaction.
  - For FRM done-stage rewrites: replace the generic `st.spinner("Finalizing...")` with a more informative message: `st.spinner(f"Applying {rewrite_count} rewrite(s) and assembling report...")` where `rewrite_count` is the count of items with action="rewrite" from the reviewed dict.
  - When `.docx` generation is added: show both download buttons side-by-side in a `st.columns(2)` layout — `.docx` left (primary, labelled "Download Word document"), `.md` right (secondary, labelled "Download Markdown backup").

**Priority:** High

---

### UX-011 — Case Tracker: Current Gaps and Phase 9 Readiness

**Current state:** The tracker (`9_Case_Tracker.py`) shows a `st.dataframe()` with columns: Case ID, Workflow, Status (emoji-badged), Last Updated. Below the table, a `st.selectbox()` drives a detail expander showing download buttons and audit log presence. The tracker reads from `cases/index.json` and backfills via `build_case_index()` if the index is absent.

**Issues:**
- The current data model is flat: one row per case. There is no concept of cases grouped under an engagement or project. Phase 9 introduces "engagements" (named projects containing multiple cases). When Phase 9 lands, the tracker will need a hierarchical view, but the current flat dataframe has no path to hierarchy without a significant redesign.
- The selectbox-driven detail view is disconnected from the dataframe row. Maher clicks a row visually, but the selection happens in a separate selectbox below the table. The two-step interaction (click row, then find same case in selectbox) is unnecessary friction. The existing `st.dataframe` does support `on_select` events in newer Streamlit versions.
- Status values shown in the tracker are raw state machine names (`OWNER_APPROVED`, `JUNIOR_DRAFT_COMPLETE`, etc.). These are internal identifiers. For a sole practitioner tool, "Draft Complete", "Under Review", "Approved", "Failed" are more meaningful labels.
- The Workflow column shows human-readable labels (`_WORKFLOW_LABELS` dict), which is correct — but several keys are missing. If a new workflow is added and its key is not in `_WORKFLOW_LABELS`, it renders as the raw key with underscores (the `.replace("_", " ").title()` fallback). This will happen with Phase 9 engagement workflows.
- There is no "Open workflow" action from the tracker. When Maher sees a case with status PIPELINE_ERROR, the guidance text says "open the workflow page and re-run" but does not link to it. He has to manually navigate the sidebar.
- The audit log presence check renders as a `st.caption()` with a hardcoded string: `f"Audit log: **{'present'}**"`. The string `'present'` is always the same regardless of whether the file exists — this is a bug: the f-string always evaluates the truthy branch because `if audit_log.exists()` is checked correctly but the string itself always says `present` in the true branch and `not yet written` in the false branch. Actually on re-reading lines 117-121 this is correct; it is a conditional expression, not a bug. However the display is still only a caption — it should be a link if a file viewer is ever added.

**Suggested changes:**
  - Map status values to human-readable labels in the tracker using a `_STATUS_LABELS` dict: `INTAKE_CREATED` → "Intake Complete", `JUNIOR_DRAFT_COMPLETE` → "Draft Ready", `PM_REVIEW_COMPLETE` → "PM Reviewed", `PARTNER_REVIEW_COMPLETE` → "Partner Reviewed", `OWNER_APPROVED` → "Approved", `DELIVERABLE_WRITTEN` → "Complete", `PIPELINE_ERROR` → "Error — action needed".
  - Replace the selectbox+expander pattern with Streamlit's `st.dataframe(on_select="rerun", selection_mode="single-row")` (available in Streamlit 1.35+). The selected row index can then drive the detail panel directly below the table, removing the duplicate selectbox.
  - Prepare the tracker for Phase 9 hierarchy by adding an `engagement_id` column to the index schema now (even if it is null for all existing cases). When Phase 9 lands, group rows by `engagement_id` using `st.expander(engagement_name)` containing the case rows for that engagement.
  - Add a "Resume / Open" button in the detail expander that navigates to the correct workflow page using `st.switch_page()` (Streamlit 1.31+). Map `workflow` key to page path: `frm_risk_register` → `pages/6_FRM.py`, etc. This resolves the "how do I re-run a failed case" UX gap.
  - Add a "Client" column to the tracker dataframe populated from `client_name` in the index. Currently the tracker shows Workflow and Status but not which client the case belongs to — on a busy tracker with 20+ cases, this makes it hard to find a specific case by client name.

**Priority:** High

---

### UX-012 — Phase 9 Engagements: Structural UI Suggestion

**Current state:** No Phase 9 UI exists yet. The current app treats every pipeline run as an independent case with a unique `case_id`. There is no grouping, naming, or navigation concept for multi-case engagements.

**Issues:**
- Phase 9 "engagements" contain multiple cases (e.g., one FRM run + one Investigation + one DD report all for the same client under one engagement). Without an engagement-level UI wrapper, Maher will have no way to see all cases for one client together.
- There is no current "engagement home" — a page that shows the state of a whole engagement across its constituent cases, with links to resume any individual case.
- The Case Tracker does not distinguish between a standalone ad-hoc case and a case that belongs to a named engagement.

**Suggested changes:**
  - Add a new page `01_Engagements.py` (or rename `0_Scope.py` and make it the engagement home). This page is the entry point for all new engagements and the dashboard for existing ones.
  - Engagement home layout (two panels):
    - Left panel (1/3 width): list of named engagements. Each shown as a card with: Engagement name, Client, Status (most advanced case status), Last activity date. "New Engagement" button at top.
    - Right panel (2/3 width): selected engagement detail — shows all cases under it as a mini-tracker, with a "Run New Workflow" button that pre-fills the client/case context.
  - "New Engagement" flow: prompts for engagement name, client, and optional description. Creates an `engagement_id` and stores it. All subsequent workflow runs for this client are tagged with the engagement_id at intake — either via a "Continue Engagement" path on each workflow page, or by auto-detecting client name match.
  - Engagement status roll-up rule: if any case in the engagement is PIPELINE_ERROR → show amber warning dot on the engagement card. If all cases are complete (OWNER_APPROVED or DELIVERABLE_WRITTEN) → show green. Otherwise blue.
  - The existing 0_Scope page should become a step inside the New Engagement flow, not a standalone workflow. Scoping produces the engagement-level context that then propagates into individual case intakes.

**Priority:** Medium (Phase 9 work — not for immediate build, but inform schema design now)

---

### UX-013 — Document Library and Embedding Visibility (Sprint-EMB)

**Current state:** Documents are uploaded per-case via `st.file_uploader` on Investigation, FRM, DD, and TT pages. After upload, they are registered in `DocumentManager` and confirmed with a `st.caption("✓ filename — registered")` line. There is no persistent document library view. There is no indication of embedding status once Sprint-EMB lands.

**Issues:**
- After a document is registered, there is no way to see the list of documents in a case without downloading files from the local filesystem. The tracker shows audit log presence but not document index contents.
- When Sprint-EMB adds semantic chunking and retrieval, Maher needs to know which documents are indexed, how many chunks exist, and whether embedding is complete — otherwise he cannot trust whether the agent is working from the right source material.
- Currently the file uploader is transient: if Maher refreshes the page mid-session, the file list in the uploader resets. The underlying `DocumentManager` index is persistent (disk-based), but the UI has no way to show "you already uploaded 3 documents for this case."
- There is no way to add documents to an existing case after the initial pipeline run. If Maher receives additional evidence mid-engagement, he has no UI path to register it without re-running the intake.

**Suggested changes:**
  - Add a "Documents" tab or expander on each workflow's done stage (and in the Case Tracker detail view) showing: filename, file size, registration date, doc_type, and (post-Sprint-EMB) embedding status ("Indexed — 42 chunks" or "Pending indexing").
  - Implement a persistent document panel that loads from `DocumentManager`'s index for the current case_id on page load. This replaces the transient uploader display with an accurate reflection of what is actually registered. Show: "3 documents registered for this case" with a list, plus the uploader for adding more.
  - For Sprint-EMB: add a visible "Index status" badge on each document row. States: "Indexed", "Pending", "Failed". On hover/expand: chunk count, embedding model used, indexed at timestamp. This is the minimum Maher needs to trust that semantic retrieval is working.
  - Add an "Add Documents" button in the Case Tracker detail view for cases in non-terminal states. This opens a per-case document upload modal (or navigates to the workflow page with the case pre-loaded) without re-running intake.
  - Suggest a standalone `Document Library` page (or a tab in the Case Tracker) listing all documents across all cases, filterable by case/client. This matters once Maher has 20+ cases — he will need to find a document he uploaded weeks ago.

**Priority:** Medium (design now; Sprint-EMB implements embedding status; document panel is buildable now)

---

### UX-014 — Conversational Evidence Mode: UI Design Suggestion

**Current state:** No conversational evidence mode exists yet. This feature is being designed this session. Current evidence interaction is one-directional: upload documents → pipeline reads them → output generated.

**Issues:**
- The pipeline model is batch: Maher uploads all documents, runs the pipeline, gets output. There is no way to interject mid-pipeline with additional context, ask the agent a question about a document, or explore a specific finding before the full report is generated.
- For complex investigations, Maher may want to test a hypothesis ("does the evidence support a fraud triangle here?") before committing to a full pipeline run.

**Suggested changes:**
  - Conversational evidence mode should be a distinct page or tab, not embedded in an existing pipeline page. Suggested page: `14_Evidence_Chat.py` or a tab within the Investigation page.
  - Layout: two-panel design.
    - Left panel (1/3): document list for the current case (from DocumentManager index). Each document has a checkbox "Include in context". Selected documents are available for the conversation.
    - Right panel (2/3): chat interface using `st.chat_input()` and `st.chat_message()`. Each message exchange is logged to `audit_log.jsonl` with role, timestamp, and referenced document IDs.
  - The agent in this mode is the Consultant (junior) — single-turn, no PM/Partner review loop. This is explicitly an exploration mode, not a draft-generation mode.
  - Add a clear visual banner: "Evidence Exploration Mode — outputs here are not reviewed deliverables. Use the Investigation pipeline for reviewed reports." This addresses the CLAUDE.md use-case note about boundary clarity between assisted output and partner-reviewed output.
  - From the chat, Maher should be able to action a finding: a "Add to report draft" button below each agent response that tags the exchange as a finding candidate. These tagged items can be passed into a subsequent Investigation pipeline run as pre-seeded findings.
  - Conversation history for a case should persist across sessions (stored in `cases/{id}/evidence_chat.jsonl`), so Maher can return to an exploration thread days later.

**Priority:** Medium (being designed this session — spec here feeds into the design discussion)

---

### UX-015 — Interim Workpaper Generation: Trigger and Placement

**Current state:** No interim workpaper generation exists yet. Full pipeline outputs a final report. There is no intermediate deliverable for work-in-progress states.

**Issues:**
- On a 4-week investigation, Maher may need to share a workpaper after week 2 showing findings-to-date. The current tool has no path for this — only final reports are generated.
- There is no UI trigger for a "generate workpaper now" action mid-case.

**Suggested changes:**
  - Workpaper generation should be triggerable from two places:
    1. The Case Tracker detail expander — a "Generate Workpaper" button visible for cases with status `JUNIOR_DRAFT_COMPLETE` or `PM_REVIEW_COMPLETE` (i.e., draft material exists but final report is not approved yet).
    2. A secondary action button in the pipeline `done` stage on Investigation and FRM pages — labelled "Generate Interim Workpaper" placed below the primary download button. This is for post-pipeline workpaper slices (e.g., Module 2 only, or findings up to a certain date).
  - Workpaper should be visibly distinct from final report. Suggested: header banner "INTERIM WORKPAPER — NOT FOR CLIENT DISTRIBUTION" injected by the generation template. This prevents accidental client delivery of unreviewed material.
  - Download label: "Download Workpaper (.md)" — use a different filename pattern than `final_report.en.md` to avoid confusion. Suggested: `workpaper_{case_id}_{YYYYMMDD}.md`.
  - No pipeline re-run needed for workpaper generation — it assembles from already-persisted artifacts (`junior_output.v{N}.json`, `pm_review.v{N}.json`) with a lighter formatting pass. The trigger should be a synchronous operation, not a 2-minute pipeline run.

**Priority:** Medium (design now; implement when workpaper generation is built in Phase 9)

---

### UX-016 — Visual Design: Professional Forensic Brand

**Current state:** `session.py` injects a CSS block via `st.markdown(_CSS, unsafe_allow_html=True)` on every page. The CSS covers: Montserrat font import, primary button color (#D50032 GoodWork red), hover state (#761E2F), severity badge styles (critical/warning/info), case-id-chip (monospace), and h2 styling with red bottom border.

**Issues:**
- The CSS is injected inside `bootstrap()` which is called on every page, but only on first bootstrap (`if "bootstrapped" in st.session_state: return`). After the first page load, subsequent page navigations will not re-inject the CSS because `bootstrapped` is already set. This means style may not apply on page navigation in some Streamlit versions — confirm whether this is causing inconsistent styling across pages.
- Montserrat is loaded via Google Fonts CDN (`@import url(...)`). In air-gapped or restricted network environments (not uncommon in a forensic consulting context), this import will silently fail and fall back to system fonts. The fallback chain `'Helvetica Neue', Arial, sans-serif` is reasonable but should be tested.
- The severity badge classes (`.severity-critical`, `.severity-warning`, `.severity-info`) are defined but `pipeline.py`'s `_render_event()` function does not apply these CSS classes — it uses `st.error()`, `st.warning()`, `st.info()` which render Streamlit's own styled components. The custom CSS classes are defined but unused. Either use them (via `st.markdown(f'<div class="severity-info">...</div>', unsafe_allow_html=True)`) or remove them.
- The `h2` rule applies a red bottom border and bold to all `<h2>` elements. Streamlit renders `st.subheader()` as `<h3>`, not `<h2>`. So the styled heading rule only hits `st.header()` which is rarely used in these pages. Most page section headers are `st.subheader()` — they are unstyled by the current CSS.
- There is no `.streamlit/config.toml` file present (or if present, it was not reviewed). Streamlit's built-in theming via `config.toml` (`[theme]` section) is the most robust way to set primary color, background, text color, and font — it applies globally without CSS injection and survives page navigation. The current approach of CSS injection is a workaround that is less reliable.
- The sidebar has no visual brand identity beyond the firm name text. A professional forensic tool should have a clear header with the firm name in a styled typeface, and a subtle separator before the navigation items.

**Suggested changes:**
  - Create `/Users/akaushal011/forensic-ai/.streamlit/config.toml` with:
    ```toml
    [theme]
    primaryColor = "#D50032"
    backgroundColor = "#FFFFFF"
    secondaryBackgroundColor = "#F5F2F0"
    textColor = "#282827"
    font = "sans serif"
    ```
    This sets brand colors natively. Montserrat cannot be set via config.toml but can still be injected via CSS — keep the font import in `_CSS` but remove the button color overrides that duplicate what config.toml handles.
  - Fix the `h2` vs `h3` mismatch: either change the CSS selector to `h2, h3` to catch `st.subheader()`, or replace uses of `st.subheader()` with `st.markdown("## Section Title")` on pages where the styled heading matters (intake form headers, section dividers in done stage).
  - Remove unused severity CSS classes from `_CSS` or wire them up. Recommendation: wire them up. In `pipeline.py`'s `_render_event()`, render CRITICAL and WARNING events using `st.markdown(f'<div class="severity-critical">[agent] {message}</div>', unsafe_allow_html=True)` to get the left-border accent style from the existing CSS. INFO events can remain as `st.info()`.
  - Move the `_CSS` constant from `session.py` to a dedicated `streamlit_app/shared/styles.py` module and call `inject_styles(st)` separately from `bootstrap()`. This separates concerns and makes styles easier to update without touching session initialization logic.
  - Add a sidebar footer with `st.sidebar.caption(f"GoodWork Forensic AI · {today}")` and a divider. This gives the sidebar a finished, professional look.
  - Long-term suggestion (not for current sprint): commission a dark/light mode toggle. Forensic professionals reviewing documents for long sessions often prefer dark mode. Streamlit config.toml does not support runtime toggle, but a CSS class swap can be achieved with st.markdown injection.

**Priority:** Medium

---

### UX-017 — Settings Page: Incomplete Firm Profile Coverage

**Current state:** The Settings page (`settings.py`) covers: firm name, logo path, default currency, pricing model, and T&M rates. It reads/writes `firm_profile/firm.json`. The page explicitly notes it does NOT cover `firm_profile/firm_profile.json` (CLI setup_wizard) or `firm_profile/pricing_model.json` (CLI proposal flow) — those remain CLI-only.

**Issues:**
- MEMORY.md states the extended setup checklist requires: firm name, logo path, team member bios, pricing model, and standard T&C text. The Settings page covers 1 and 2 from this list. Team bios are on page 10 (Team). T&C text has no Streamlit UI path at all.
- The split between `firm.json` (Streamlit) and `firm_profile.json` / `pricing_model.json` (CLI only) means Maher must use the CLI for some firm configuration tasks. This is a maintenance liability — two sources of truth for firm profile data.
- Settings currently has no way to preview what a proposal will look like with the current firm profile. Maher fills in these fields in isolation and only discovers issues when generating a proposal.
- There is no "first run" onboarding indicator in Settings. A new user who has never filled in the Settings page will generate proposals with blank firm name and no credentials — there is no warning in the proposal workflow about this gap.

**Suggested changes:**
  - Add a "Terms & Conditions" text area to the Settings page (or a dedicated tab): a large `st.text_area("Standard T&C text", height=200)`. Store in `firm.json` under key `tc_text`. Surface in proposal generation.
  - Consolidate `firm_profile.json` and `pricing_model.json` into `firm.json` — make `firm.json` the single source of truth read by both Streamlit and CLI paths. This is a backend refactor but it eliminates the two-source problem.
  - Add a completeness indicator at the top of the Settings page: a visual checklist (e.g., `st.metric()` tiles or `st.progress()`) showing: Firm Name (set/not set), Logo (set/not set), Pricing (set/not set), T&C (set/not set), Team bios (set/not set — link to Team page). If any item is missing, show amber warning. If all set, show green "Firm profile complete — ready for proposals."
  - In the Proposal workflow intake, add a pre-flight check: before rendering the proposal form, read `firm.json` and check required fields. If firm name is blank, show `st.warning("Firm profile incomplete — go to Settings before generating a proposal.")` with a direct link to the Settings page.

**Priority:** Medium

---

## Open UX Decisions — Session 024

| ID | Question | Options | Status |
|---|---|---|---|
| UX-D-05 | Remove `st.form` from `generic_intake_form()` for per-field validation vs. keep form for clean batch submission UX | A: Remove form, individual widgets + button. B: Keep form, accept post-submit-only validation. | Needs AK decision |
| UX-D-06 | Phase 9 engagement home — new page vs. rework of 0_Scope.py | **RESOLVED: Option A** — New `01_Engagements.py`, Scope becomes a step inside New Engagement flow. 2026-04-19. | RESOLVED |
| UX-D-07 | Conversational evidence mode placement — standalone page vs. tab vs. persistent panel | **RESOLVED: Option C (new)** — Persistent collapsible chat panel on ALL engagement pages. Single shared component via bootstrap(). Right-edge slide-out panel. 2026-04-19. | RESOLVED |

---

### UX-018 — Settings / Config Page (full overhaul)

**Current state:** Settings page (`settings.py`) covers only firm name, logo path, currency, pricing model, and T&M rates. Team bios are on a separate page (page 10). T&C text has no UI path. Word templates for output documents have no UI path at all.

**Issues:**
- The page covers only 2 of the 5 items required by the extended setup checklist (MEMORY.md). Team bios, T&C text, and report templates are inaccessible from Settings.
- T&C text has no Streamlit UI path — if Maher needs to update the standard T&C, he must edit JSON files directly.
- Logo is captured as a file path string (`st.text_input`) rather than an actual file upload. Maher must know the repo-relative path, which is a developer-level detail.
- Report templates are a new firm_profile concern (firm_profile/templates/) with no UI at all. Maher cannot upload, preview, or manage Word templates from the app.
- No completeness indicator exists. Maher cannot tell at a glance which sections are fully configured before generating proposals or reports.
- The single flat page structure makes it difficult to extend Settings as new configuration categories are added.

**Suggested changes:**

Redesign the Settings page as a four-tab layout using `st.tabs(["Firm Profile", "Pricing", "Team & T&C", "Report Templates"])`. All tabs use a consistent two-column layout: label column 40% width, input column 60% width. Each tab has its own "Save" button. A completeness badge renders at the top of the page (above the tabs) showing which sections are fully filled in.

**Completeness badge:**
- Render as a row of `st.metric()` tiles or inline colored chips, one per tab section.
- States per section: "Complete" (green), "Incomplete" (amber), "Not started" (grey).
- Logic: Firm Profile complete if firm_name and logo file both set. Pricing complete if pricing_model set AND (if T&M, rates are non-zero). Team complete if at least one team member with name and credentials. T&C complete if tc_text non-empty. Templates complete if at least one workflow has a custom template uploaded.
- Show a summary line: "3 of 5 sections complete — firm profile ready for proposals" (or "incomplete — proposals may be missing firm context").

**Tab 1 — Firm Profile:**
- Firm Name: `st.text_input("Firm name")` — required, pre-loaded from firm.json.
- Logo: `st.file_uploader("Logo file", type=["png","jpg","svg"])`. On upload, save file to `assets/logo.png` and store path in firm.json. Show current logo filename if already set: `st.caption("Current: assets/logo.png")`.
- Default Currency: `st.selectbox("Default currency", ["AED", "USD", "SAR", "GBP", "EUR"])`.
- Tagline (optional): `st.text_input("Tagline (optional)")` with helper text: "Used on proposal cover pages. Leave blank to omit."
- Save button: primary (#D50032), disabled if Firm Name is empty.

**Tab 2 — Pricing:**
- Pricing Model: `st.selectbox("Pricing model", ["T&M", "Lump Sum", "Retainer"])`.
- If T&M selected: show Day Rate (`st.number_input`) and Hour Rate (`st.number_input`), both in the selected currency.
- If Lump Sum selected: show Lump Sum Note (`st.text_area("Lump sum note", height=80)`) — free text for how lump sums are typically structured (used in proposals).
- If Retainer: show Retainer Note (`st.text_area("Retainer note", height=80)`).
- Completeness indicator inline below the pricing fields: `st.info("Pricing complete")` or `st.warning("Day rate is zero — proposals will show AED 0/day. Update before generating a proposal.")`.
- Save button per tab.

**Tab 3 — Team & T&C:**
- Team member list: up to 6 members, rendered as `st.expander(f"Team member {n}: {name or 'Empty'}")` per slot.
- Inside each expander: Name (`st.text_input`), Title (`st.text_input`), Credentials (`st.text_input`, e.g. "CFE, CPA, ACA"), Bio (`st.text_area`, height=100).
- Add/remove: "Add Member" button appends a new expander slot (up to 6). "Remove" button inside each expander removes that slot.
- T&C text area: `st.text_area("Standard Terms & Conditions", height=300)` with helper: "This text is included in all client proposals. Paste your standard T&C or write it here."
- Link to Team page: `st.caption("For detailed team management, see the Team page in the sidebar.")` with `st.page_link()` if Streamlit 1.31+.
- Save button saves both team JSON and T&C to firm.json.

**Tab 4 — Report Templates:**
- Show a table (rendered via `st.dataframe` or manual `st.columns` rows) with one row per supported workflow type.
- Columns: Workflow | Current Template | Last Updated | Actions.
- Workflow rows: Investigation Report, Due Diligence Report, FRM Risk Register, Transaction Testing Report, Sanctions Report, Client Proposal.
- Current Template column: shows filename of uploaded custom template, or "Base GoodWork template" if none uploaded.
- Last Updated column: timestamp of last template upload, or "—" if base template.
- Actions per row (rendered as inline buttons in the Actions column):
  - "Upload Custom": opens an inline `st.file_uploader` (shown conditionally for that row only, using session_state keyed by workflow_id). Accepts .docx only, max 5MB. On upload: validate required Word styles (see below), save to `firm_profile/templates/{workflow_id}.docx`, update template metadata JSON.
  - "Preview": show a `st.popover` or `st.expander` with template name and a list of styles detected in the document: e.g. "GW_Heading1, GW_Body, GW_FindingTitle, GW_Disclaimer — 4 required styles found".
  - "Reset to Base": show `st.warning("This will remove your custom template. The base GoodWork template will be used instead.")` followed by a "Confirm Reset" button. Requires explicit confirmation before deletion.
- Upload validation: after .docx upload, check for required Word styles using python-docx (`doc.styles`). Required styles per workflow type are defined in a config dict. Show result inline below the uploader:
  - Pass: `st.success("Valid: 7 required styles found.")` — save button enables.
  - Partial: `st.warning("Warning: Missing styles GW_Disclaimer, GW_Caption — base styles will be used for those sections.")` — save still allowed (non-blocking).
  - Fail: `st.error("Invalid template: missing required styles GW_Heading1, GW_Body. Upload a valid GoodWork-format template.")` — save blocked.
- File size enforcement: if uploaded file >5MB, reject with `st.error("File too large — maximum 5MB per template.")`.
- Save button: saves the uploaded template file and metadata. Does not re-validate — validation fires on upload event.

**Mobile (375px):** Tabs stack as a horizontal scrollable tab bar (Streamlit default). Two-column layout collapses to single column. Save button full-width.

**Priority:** High

---

### UX-019 — Engagement-Time Template Selection

**Current state:** All workflow pages run the pipeline and generate output using either the base GoodWork template or whatever is saved as the default in firm_profile/templates/. There is no mechanism at intake time to choose a different template, override the default for a specific engagement, or upload a one-off template without affecting the firm-level default.

**Issues:**
- If Maher is running a report for a client who has their own Word template preferences (e.g., a Big 4 format), he has no way to use that template for one engagement without overwriting his firm-level default.
- There is no visual confirmation at intake showing which template will be used. Maher has no way to verify the correct template is selected before a 2-3 minute pipeline run.
- The pipeline currently receives no `report_template_path` parameter — it falls back to base template silently. If the firm-level template is corrupted or missing, the pipeline fails with a generic error rather than a graceful fallback with a visible warning.

**Suggested changes:**

Add a `st.expander("Report template", expanded=False)` to Zone A (intake form) on every workflow page. Placement: below the last intake field, above the Run button. This is a collapsible section so it does not add visual weight to the intake form for users who accept the default.

**Expander contents:**

Radio button group with three options:
1. "Use saved template: [filename]" — shown only if a custom template exists for this workflow in `firm_profile/templates/{workflow_id}.docx`. Label uses the actual filename. Pre-selected by default if a saved template exists.
2. "Upload for this engagement only" — one-off upload, does not overwrite the firm-level default. Selecting this option reveals an inline `st.file_uploader` immediately below the radio group: accepts .docx only, no explicit size limit stated in UI (backend enforces 5MB). The uploaded file is stored temporarily in session_state and passed to the pipeline — it is not persisted to firm_profile/templates/.
3. "Plain Word output (no template)" — pipeline generates output with default python-docx styling only. No GoodWork brand, no custom styles. Useful for draft-stage output or when no template is available.

**Default selection logic:**
- If `firm_profile/templates/{workflow_id}.docx` exists → pre-select option 1 ("Use saved template").
- If no saved template → pre-select option 3 ("Plain Word output").
- Option 2 is never pre-selected (it requires explicit user action).

**Confirmation line:**
After any selection is made (including the default), show a single confirmation line below the radio group using `st.caption()`:
- Option 1: `"Template: {filename} — {style_summary}"` where `style_summary` is read from template metadata JSON (e.g. "Big 4 style, GoodWork brand"). If metadata is absent, show: `"Template: {filename} — style details not available"`.
- Option 2 (file uploaded): `"Template: {uploaded_filename} — engagement-only, not saved to firm profile"`.
- Option 2 (no file yet): `"Upload a .docx file to continue"` — Run button disabled until file is uploaded.
- Option 3: `"Plain Word output — no brand template applied"`.

**Session state and pipeline integration:**
- Selected template path stored in `st.session_state["report_template_path"]` for the current workflow page.
- For option 2, the uploaded file bytes are stored in `st.session_state["report_template_bytes"]` — the pipeline handler saves these to a temp file before passing the path downstream.
- `report_template_path` is passed to the pipeline as a keyword argument. Pipelines that do not yet support template injection ignore this argument (no breaking change).
- At pipeline start in Zone B, log the template selection as an INFO event: `[Setup] Using template: {filename}` or `[Setup] Plain Word output — no template`.

**Fallback behavior:**
- If option 1 is selected but the template file is missing at pipeline start (e.g., deleted since page load) → `st.warning("Saved template not found — falling back to plain Word output.")` shown in Zone B log. Pipeline continues with plain output, does not fail.

**Mobile (375px):** Expander collapses by default — no layout impact. When expanded, radio buttons and file uploader stack full-width. Confirmation line wraps as needed.

**Priority:** High
