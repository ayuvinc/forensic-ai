# BA Logic — GoodWork Forensic AI

_Populated via /ba discovery session — 2026-04-04_

**Archive note:** Sessions 010–011 decisions (features already built) archived to `tasks/ba-logic-archive.md` on 2026-04-20.

---

## Business Logic Decisions

[2026-04-04] Decision: Tool is a writing and organization aid, not an investigator.
Rationale: Maher provides facts, evidence, and analytical conclusions. The tool structures, drafts, and standardizes — it does not reach conclusions independently. Any output that presents a "finding" is structured from Maher's input, not generated as independent analysis.

[2026-04-04] Decision: Sole practitioner model — all roles collapse to one user.
Rationale: Maher IS the junior analyst, project manager, and partner. The multi-agent pipeline simulates the review hierarchy a staffed firm would have. Maher can accept, override, or ignore any agent review output.

[2026-04-04] Decision: Multi-session case work is the primary usage pattern.
Rationale: Cases run 3–8 weeks. Maher works on a case across multiple days and sessions. State must persist reliably. Resume-from-last-state is not a nice-to-have — it is required for the tool to be usable on real engagements.

[2026-04-04] Decision: CXO is the default audience for all deliverables.
Rationale: GoodWork's clients are CXOs. All language, structure, and framing defaults to executive-appropriate. Technical or regulatory depth is present but subordinated to clarity and executive relevance.

[2026-04-04] Decision: No output is client-facing without Maher's review.
Rationale: Tool produces drafts. Maher reviews, edits, and approves before anything goes to a client. The tool does not send emails, submit filings, or publish anything.

[2026-04-04] Decision: Intake questions vary by case type.
Rationale: Investigation intake is different from FRM intake, which is different from proposal intake. Each workflow has its own guided intake conversation. There is no universal intake form.

[2026-04-04] Decision: Value = time saved on grunt work, money saved vs. hiring associates.
Rationale: The business case is not quality improvement alone — it is capacity expansion. A solo practitioner who can produce associate-quality first drafts in hours rather than days can take more cases, respond faster, and keep margins without headcount.

---

## Acceptance Rules

_What must be true for a feature to be considered done._

- Guided intake: produces a Pydantic-validated CaseIntake object from a conversation — no form fields presented to user
- Investigation report: Junior draft → PM review → Partner sign-off → final_report.en.md written to cases/{id}/
- FRM Risk Register: all 8 modules run (within scope); module dependency rules enforced; final_report.en.md written
- Policy/SOP, Training, Proposal: single-pass draft written to cases/{id}/ with audit event recorded
- Resume: if state.json is non-terminal, orchestrator detects and offers resume on next run — no data loss
- Evidence tracking: every document registered via document_manager has a retrievable index entry; model can re-read on demand
- All deliverables: language calibrated for CXO audience; no raw regulatory citations without plain-English explanation
- Audit trail: every agent run, review decision, and state transition appended to audit_log.jsonl
- No client-facing output generated without a human-readable review step in the pipeline

---

## Data Rules

- All case data stored locally in `cases/{case_id}/` — never transmitted without Maher's action
- `audit_log.jsonl` is append-only — no entry is modified or deleted after write
- Artifact writes are atomic: `.tmp` → `os.replace()` — no partial writes
- `state.json` reflects the current pipeline status of the case at all times
- `firm_profile/` stores Maher's firm credentials, pricing, and T&C — loaded at proposal time, not re-entered
- Evidence documents registered in `document_manager` are indexed with bounded retrieval — model reads sections on demand, not the whole document on every call
- Final deliverables: `final_report.en.md` always generated; `final_report.ar.md` generated when language = ar at intake
- Case IDs follow format `{YYYYMMDD}-{6-char alphanumeric}` (e.g. `20260101-A3B4C5`) — generated at intake via uuid4 truncated to 6 chars uppercased

---

## Edge Cases

[2026-04-04] Session interrupted mid-pipeline:
→ state.json holds last valid status; orchestrator detects non-terminal state on next run; offers resume; loads last persisted artifact as starting point. No data loss expected if artifact writes were atomic.

[2026-04-04] Maher disagrees with agent review output:
→ He can override any PM or Partner finding. Approval decisions are his to make. The pipeline records his override in the audit log but does not block on it.

[2026-04-04] Case involves jurisdictions outside UAE:
→ Regulatory mapping is dynamic. Model identifies applicable regulators from client's operating jurisdictions at intake — not hardcoded to UAE. If no authoritative source found for a jurisdiction, disclaimer added to deliverable.

[2026-04-04] Client documents not yet uploaded at intake:
→ Model prompts for documents after intake; Maher can upload later. Case stays at INTAKE_CREATED until documents are available and Maher triggers the pipeline.

[2026-04-04] Firm profile not set up (first run):
→ Setup wizard runs before first menu; collects firm name, team bios, pricing model, T&C. Stored in `firm_profile/`. If skipped, proposal fee section generates with blank rates — pricing completeness check warns Maher before drafting begins (PGP-01).

---

## Open Decisions

[2026-04-04] Should client_proposal be upgraded to full pipeline (Junior → PM → Partner) or remain Mode B (single-pass)?
→ Proposal is the highest-value commercial deliverable. Mode B is faster but has no review layer. Decision pending — see C-01b in tasks/todo.md.

[2026-04-04] What state should Mode B workflows write to state.json on completion?
→ RESOLVED Session 007 (2026-04-04): DELIVERABLE_WRITTEN added to CaseStatus enum and TERMINAL_STATUSES.
  _mark_deliverable_written() called in run.py after choices 4,5,7,8 complete.
  case_tracker renders DELIVERABLE_WRITTEN as green (terminal). See C-02a in tasks/todo.md.

---


---

## Session 022 Decisions — 2026-04-19

---

### BA-R-01 — Report Design Standard
- Status: CONFIRMED (AK session 022)
- Scope: All workflow final reports (DOCX + MD)

**User outcome:** Every client-facing report has a professional cover page, firm branding, standard section structure, and table of contents — regardless of which workflow produced it.

**Business rules:**
- DOCX is the primary client deliverable. MD is internal backup. No PDF for now.
- Section structure: Fixed base + workflow-specific overrides.
  - Base (all workflows): Cover Page → Table of Contents → Executive Summary → Scope & Methodology → Findings → Recommendations → Appendix
  - FRM override: replaces Findings with Risk Register Table + adds Heat Map section
  - Investigation override: 13-section forensic structure (see BA-R-05)
  - DD override: per-subject or consolidated subject profiles (see BA-R-06)
  - TT override: Population → Sample → Procedures → Exceptions Table → Extrapolation → Conclusions (see BA-R-07)
  - Sanctions override: Executive Summary → Screening Scope → Hits Detail → False Positives → Appendix (see BA-R-08)
- Cover page: firm logo, client name, report title, report date, confidentiality notice ("Prepared for [Client] — Confidential & Privileged")
- Header on every page: firm name + report title
- Footer on every page: page number (centred) + confidentiality label (right-aligned)
- Table of contents: auto-generated from DOCX heading styles — Heading 1 = section, Heading 2 = sub-section
- Fonts: Calibri body / Calibri Light headings (standard DOCX defaults if no template loaded)
- AI Review classifications: INTERNAL ONLY — never appear in client DOCX or MD

**Edge cases:**
- No logo path set: cover page renders without logo; no error.
- Template uploaded by consultant uses incompatible styles: BaseReportBuilder falls back to default styles; logs warning.

---

### BA-R-02 — Report Versioning
- Status: CONFIRMED (AK session 022)
- Scope: All final reports across all workflows

**Business rules:**
- Before writing a new final report, existing report moved to `{project_root}/Previous_Versions/`
- Filenames versioned: `final_report.v1.en.md`, `final_report.v2.en.md`, `final_report.v1.en.docx` etc.
- `F_Final/` (P9 projects) or `cases/{uuid}/` (legacy) always contains the LATEST version only
- `Previous_Versions/` subfolder holds all prior versions
- Version counter = count of files already in `Previous_Versions/` + 1

---

### BA-R-03 — Report Template Selection
- Status: CONFIRMED (AK session 022)
- Scope: First report generation per project (per workflow type)

**Business rules:**
- At report generation, if no template exists for this workflow type, offer two paths:
  1. "Use my own template" — `st.file_uploader` for .docx → saved to `firm_profile/templates/{workflow_type}.docx` → update firm.json
  2. "Build a template" — guided mini-wizard: firm name (pre-filled), logo path (pre-filled if set), primary colour (hex), secondary colour (hex), font choice (Calibri / Arial / Times New Roman) → generates and saves template.docx
- If template already exists for this workflow type: skip prompt, load silently
- Template path stored in `firm_profile/firm.json["templates"][workflow_type]`

---

### BA-R-04 — FRM Risk Register Enhanced Output
- Status: CONFIRMED (AK session 022)
- Scope: FRM workflow only

**Business rules:**
- Primary deliverable: DOCX with risk register as a formatted table
  - Columns: Risk ID | Risk Description | Likelihood (1–5) | Impact (1–5) | Rating (L×I) | Risk Level | Owner | Mitigation
  - Rows sorted by Rating descending
  - Heat Map section: 5×5 grid, risks plotted by Likelihood/Impact coordinates
  - Recommendations section: depth determined at intake
- Secondary deliverable: Excel (.xlsx) — same risk table + separate Heat Map sheet
  - Heat map sheet: 5×5 colour-coded grid (red ≥15, amber 8–14, green ≤7)
  - Requires `openpyxl` in requirements.txt
- Recommendation depth — asked at FRM intake:
  - "One-line actions": one sentence per risk (for internal/scoping engagements)
  - "Structured per risk" (DEFAULT): Immediate Action + Medium-Term Control + Responsible Party + Timeline
  - "Consolidated section": all mitigations in a summary section, not inline
  Default: structured. Override if scope indicates internal use only.

---

### BA-R-05 — Investigation Report Structure (Full Forensic Standard)
- Status: CONFIRMED (AK session 022)
- Scope: Investigation workflow only

**Report section order (forensic standard — fixed):**
1. Cover Page
2. Table of Contents
3. Background
4. Scope of Work
5. Note to Reader (limitations, qualifications, disclaimers)
6. Procedures Performed
7. Limitations to Procedures
8. Disclaimers
9. Evidence List (all exhibits, numbered, before Executive Summary)
10. Executive Summary
11. Detailed Findings (narrative; headers + subheaders; footnotes cite Exhibit N)
12. Appendix / Exhibits (uploaded evidence, labelled Exhibit 1, 2…)
13. Annexures (explanatory notes, schedules, third-party data)

**Detailed Findings section:**
- Evidence-led narrative: Procedure Performed → Evidence Observed → Finding → Implication → Conclusion
- Footnotes cite exhibits: "(refer Exhibit 3 — Bank Statement dated 15 Jan 2026)"
- No bare conclusions — every finding references at least one exhibit or stated procedure

**Evidence types (three source streams):**
1. Digital communications (emails, WhatsApp) — model extracts key statements with sender/recipient/date
2. Documentary / financial records — model extracts transactions, patterns, anomalies
3. Verbal statements / interviews:
   - If primary source: findings based on interviews alone; flagged as verbal evidence
   - If corroborating: interviews confirm documentary findings; quoted selectively inline

**Exhibit numbering:**
- Each uploaded document assigned sequential Exhibit number (Exhibit 1, Exhibit 2…)
- Stored in `D_Working_Papers/exhibit_register.json`
- Evidence List section auto-generated from exhibit_register.json

**Investigation Leads Register:**
- Structured register in `D_Working_Papers/leads_register.json`
- Fields: Lead ID, Description, Source, Status (Open/In Progress/Confirmed/Closed/Escalated), Evidence Found, Linked Finding ID
- When lead marked Confirmed: Haiku generates a draft finding narrative; appended to Working Papers
- Open leads at Final Run: listed in report as "Matters Requiring Further Investigation"

---

### BA-R-06 — Due Diligence Report Structure
- Status: CONFIRMED (AK session 022)
- Scope: DD workflow only

**Business rules:**
- At intake: "How many subjects?" + "Are they related?"
  - Single subject OR unrelated multiple: per-subject format
  - Multiple related subjects: consolidated format with Linkages Table
- Per-subject sections: Identity → Professional Background → Business Interests → Adverse Findings → Connections
- Consolidated format: same 5 elements + cross-reference Linkages Table
- Template option at intake: consultant can upload their own DD template; model calibrates to it

---

### BA-R-07 — Transaction Testing Report
- Status: CONFIRMED (AK session 022)
- Scope: TT workflow — standalone and as sub-report

**Business rules:**
- TT always produces a standalone file: `final_report_tt.en.docx` + `final_report_tt.en.md`
- When chained: standalone TT report generated + 1-page summary auto-embedded in parent report
- Sections: Executive Summary → Population Overview → Sample Selection Rationale → Testing Procedures → Exceptions Table → Extrapolation → Conclusions
- Exceptions Table exported to Excel as well (one sheet, same columns)

---

### BA-R-08 — Sanctions Screening Report
- Status: CONFIRMED (AK session 022)
- Scope: Sanctions workflow only

**Business rules:**
- Sections: Executive Summary → Screening Scope → Hits Detail (per entity) → False Positives → Appendix
- Hits Detail per entity: entity name, matching list entry, confidence level, matching criteria, disposition
- Disposition two-level:
  - Firm policy (firm_profile/sanctions_disposition_policy.json): default per confidence level
  - Per-hit consultant override in review screen: True Match / False Positive / Requires Further Investigation / Escalate
- Final disposition recorded in report and audit_log.jsonl

---

### BA-R-09 — FRM Stakeholder Input Capture
- Status: CONFIRMED (AK session 022)
- Scope: FRM workflow within Phase 9 engagement model

**Business rules:**
- Two capture modes (both in Input Session workspace):
  1. Structured form: Name, Role, Key Concern, Risk View → `D_Working_Papers/stakeholder_inputs.json`
  2. Document upload: interview notes, meeting minutes → `C_Evidence/{timestamp}/`
- Both passed to FRM pipeline context; stakeholders listed in DOCX Appendix

---

### BA-R-10 — Smart Intake Completion (AI Residual Question Pass)
- Status: CONFIRMED (AK session 022)
- Scope: All workflows — post-intake and pre-final-run

**Business rules:**
- Post-intake pass (Haiku): after intake form submit, identifies up to 3 missing/ambiguous items; asks one at a time conversationally; answers stored to `D_Working_Papers/intake_qa.json`; fully skippable
- Pre-final-run pass (Sonnet): before pipeline triggers, reviews all accumulated materials; presents 3–5 flags as warning cards; each card: "Resolve" or "Proceed anyway"; all decisions stored to `D_Working_Papers/prefinalrun_review.json`; pipeline unlocks when all cards acknowledged
- Both passes are non-blocking — consultant can skip
- Pass results injected into agent pipeline context

---

### BA-R-11 — Semantic Embeddings for Evidence Ingestion and Retrieval
- Status: CONFIRMED (AK session 022)
- Scope: All workflows — document ingestion, user review, pipeline context preparation

**Model routing rules (token efficiency):**
| Task | Model |
|------|-------|
| Document chunking + embedding | Local sentence-transformers (free, offline) |
| Per-document intake extraction | Haiku |
| User review semantic search | Local → Haiku synthesis |
| Pre-pipeline context preparation | Sonnet |
| Final report agents | Existing routing (unchanged) |

**Ingestion pipeline (on every document upload):**
1. CHUNK: ~500-token semantic chunks
2. EMBED: sentence-transformers (local, no API call)
3. INDEX: ChromaDB at `D_Working_Papers/vector_index/`
4. EXTRACT (Haiku): entities, key facts, red flags → appended to `D_Working_Papers/case_intake.md`

**Retrieval uses:**
- User review: semantic search by topic → ranked chunks with source citation
- Pipeline: Sonnet assembles targeted context per finding area from vector index

**Fallback:** If sentence-transformers not available (offline env), skip embedding; fall back to full-document context (existing behavior).

**New dependencies:** `sentence-transformers>=2.7.0`, `chromadb>=0.4.0`

---

## Session 024 BA — Sprint-EMB + Phase 9 Schemas + New Workflow Designs (2026-04-19)

---

### BA-P9-01 — ProjectIntake Schema Requirements
- Status: DRAFT
- Scope: `schemas/project.py` — ProjectIntake model; slug derivation and path-traversal guard (R-019)

**User outcome:** Maher names an engagement in plain language ("GiveBrite DD") and the system creates a safe, predictable filesystem path for it — with no risk of accidental file writes outside the `cases/` directory.

**Business rules:**
  - `project_name`: free-text string, 1–80 chars. Required. No validation on content — Maher can name projects however he likes.
  - `project_slug`: derived automatically from `project_name` at validation time (not stored separately by the user — it is a computed field):
    1. Lowercase the entire string
    2. Replace all whitespace sequences with a single hyphen
    3. Strip all characters that are not `[a-z0-9-]`
    4. Collapse consecutive hyphens to one
    5. Strip leading and trailing hyphens
    6. If the result is empty after stripping: raise `ValueError("project_name produces an empty slug — please provide at least one alphanumeric character")`
    7. Enforce maximum slug length of 60 chars (truncate before stripping trailing hyphen)
  - Path-traversal guard (R-019 — mandatory, non-negotiable): before any filesystem write, `project_slug` must be re-validated against a strict allowlist pattern `^[a-z0-9][a-z0-9-]{0,58}[a-z0-9]$` (or single char `^[a-z0-9]$`). If it fails: raise `ValueError` — do not create any directory.
  - Additionally: reject slugs that are or contain `.`, `..`, `/`, `\`, `~`, `$`, `%`, null bytes, or any Unicode character outside ASCII. These are blocked at validation, not just stripped — if the source string contains them after slugification, it means the slug is too aggressively sanitised and the name is ambiguous. Raise a clear error prompting Maher to rename.
  - `service_type`: one of the confirmed GoodWork workflow identifiers (e.g. `investigation_report`, `frm_risk_register`, `due_diligence`, `sanctions_screening`, `transaction_testing`, `policy_sop`, `training_material`, `client_proposal`). Required.
  - `created_at`: UTC datetime, set at intake.
  - `primary_jurisdiction`: string, default `"UAE"`.
  - `operating_jurisdictions`: list of strings, default `["UAE"]`.
  - `language_standard`: one of `["acfe_internal", "expert_witness", "regulatory_submission", "board_pack"]`, default `"acfe_internal"` (per BA-P9-05).
  - `client_name`: string, required. Used for cover page and context only — not part of slug derivation.
  - `industry`: string, optional. Pre-populated via taxonomy picker if available.
  - `language`: `"en"` or `"ar"`, default `"en"`.
  - `engagement_letter_registered`: bool, default `False`. Set to `True` when `register_engagement_letter()` is called on this project. Pipeline cannot run until this is `True` (existing gate, carried forward).
  - Slug collision detection: before creating the project directory, check whether `cases/{slug}/` already exists. If it does: surface to Maher — "A project at `cases/{slug}/` already exists. Open it or choose a different name?" Do not silently overwrite.
  - Backward compatibility: existing `CaseIntake` UUID-based cases are not affected. `ProjectIntake` is additive — both models coexist. `CaseTracker` renders both.

**Edge cases:**
  - `project_name` is entirely non-ASCII (e.g. Arabic): slug becomes empty after stripping → raise `ValueError` with message "Project name must contain at least one Latin alphanumeric character for the filesystem path. Please provide a short English identifier."
  - `project_name` is a single space or only special chars: same as above.
  - Two different project names produce the same slug (e.g. "GiveBrite DD" and "GiveBrite-DD"): collision detected at filesystem check; Maher prompted to distinguish them.
  - Maher provides a name with `../` in it (deliberate or accidental): stripped during slug derivation; but the path-traversal guard validates the final slug independently and would catch any residual traversal patterns.

**Out of scope:** Slug validation of `client_name` (used for display only, never written to filesystem directly). Renaming a project after creation (no rename workflow in v1).

**Open questions for AK:**
  - Should `service_type` be set at project creation, or can a project be created without a service type and have it selected at first final run? (Matters for whether `ProjectIntake` has `service_type` as required or optional.)
  - Should a single project support multiple service types simultaneously (e.g. DD + Sanctions on the same project), or is it always one service type per project slug? The BA-P9-01 session decision said same project_name + same service_type = same folder, implying service_type is part of the key — clarify whether the slug encodes the service type.

---

### BA-P9-02 — InputSession Schema Requirements
- Status: DRAFT
- Scope: `schemas/project.py` — InputSession model; lifecycle states from creation through final-run trigger

**User outcome:** Every time Maher opens a project to add materials (without running the pipeline), a session record is created automatically. He can see a history of what was added in each session and when.

**Business rules:**
  - `InputSession` represents one working session where Maher adds materials to a project but does not trigger the AI pipeline. It is NOT a pipeline run — it is a pre-pipeline accumulation record.
  - Fields:
    - `session_id`: UUID4, generated at session start.
    - `project_slug`: FK to `ProjectIntake.project_slug`. Required.
    - `session_type`: `Literal["input", "final_run"]`. Set at session start. An `input` session adds materials; a `final_run` session triggers the pipeline.
    - `started_at`: UTC datetime.
    - `ended_at`: UTC datetime, optional. Set when session is explicitly closed or when `session_type == "final_run"` completes.
    - `documents_added`: list of `doc_id` strings (registered via `DocumentManager` during this session).
    - `notes_added`: list of note file paths written during this session (relative to project root).
    - `key_facts_added`: integer count of new key facts appended to `key_facts.json` during this session.
    - `red_flags_added`: integer count of new red flags appended to `red_flags.json` during this session.
    - `pipeline_triggered`: bool, default `False`. Set `True` when `session_type == "final_run"` and pipeline is actually invoked.
    - `pipeline_run_id`: optional string, populated when pipeline is triggered. References the orchestrator run record.
    - `status`: `Literal["open", "closed", "pipeline_complete", "pipeline_failed"]`.
  - Lifecycle:
    1. `open` — session created; Maher is actively working. Materials added here are logged.
    2. `closed` — input session ended without pipeline trigger. All materials persisted. Session can be resumed (creates a new `InputSession`, not reopens the old one).
    3. `pipeline_complete` — `final_run` session; pipeline ran to completion.
    4. `pipeline_failed` — `final_run` session; pipeline failed before completion. Error stored in associated `CaseState.error`.
  - Session log persistence: each `InputSession` is serialised to `A_Engagement_Management/session_log.jsonl` (append-only, one line per session close event). This is distinct from `audit_log.jsonl` which records agent-level events.
  - Auto-save on close: if Maher closes the app without explicitly ending the session, the session is auto-saved with `status = "closed"` and `ended_at = now()`. Unsaved text notes are flushed to `D_Working_Papers/session_notes_{YYYYMMDD_HHMMSS}.md` before close.
  - Transition to formal Case: when `pipeline_triggered = True`, the orchestrator creates a `CaseState` object with a new `case_id` (UUID format) linked to the `project_slug`. The `InputSession` becomes the provenance record for that case run. Multiple `final_run` sessions can exist for the same project (e.g. first run produces a draft; Maher adds more documents and runs again — second `final_run` session, new `CaseState`).
  - A project can have many `InputSession` records. The most recent `final_run` session with `pipeline_complete` is the "current version" of the project.

**Edge cases:**
  - App crash during an `open` session: on next launch, detect `open` sessions in `session_log.jsonl`. Offer to review what was added. Session status updated to `closed` with a `crash_recovery` flag.
  - `final_run` session with `pipeline_failed`: session status set to `pipeline_failed`. Maher can retry — creates a new `final_run` session (does not reopen the failed one). All materials from prior sessions remain accumulated.
  - Maher opens a `final_run` session but decides not to trigger: allowed. `session_type` can be changed before pipeline trigger. Ends as `closed`.
  - Zero materials in project, `final_run` attempted: blocked with warning (BA-P9-01 edge case carried forward). Maher must acknowledge "zero-information baseline only" before proceeding.

**Out of scope:** Session sharing between users. Real-time sync of session state to cloud. Session comments or annotations on individual documents within the session record (those go in notes).

**Open questions for AK:**
  - Should `InputSession` be visible in the Streamlit UI as a history tab, or is it purely a machine record for resumability and audit? (Affects whether it needs display fields like `session_title` or `summary`.)
  - When a `final_run` session completes, should the previous pipeline outputs (E_Drafts/) be automatically versioned, or does Maher manually trigger versioning? (Relates to BA-R-02.)

---

### BA-P9-03 — ProjectState Schema Requirements
- Status: DRAFT
- Scope: `schemas/project.py` — ProjectState model; relationship to existing `CaseState`

**User outcome:** Maher can see the full status of a named project — how many sessions it has had, which pipeline runs have completed, which are in progress, and what the overall project health is — without having to cross-reference multiple JSON files manually.

**Business rules:**
  - `ProjectState` is the project-level aggregation over one or more `CaseState` records and multiple `InputSession` records. It does NOT replace `CaseState` — it wraps it.
  - Fields:
    - `project_slug`: string. Primary key. Must match `ProjectIntake.project_slug`.
    - `project_name`: string. Display name (denormalised from `ProjectIntake` for convenience).
    - `service_type`: string. From `ProjectIntake`.
    - `created_at`: UTC datetime.
    - `last_updated`: UTC datetime. Updated on every input session close and every pipeline state transition.
    - `total_input_sessions`: integer. Count of all `InputSession` records for this project.
    - `total_pipeline_runs`: integer. Count of all `CaseState` records linked to this project.
    - `latest_case_id`: optional string. The `case_id` of the most recent pipeline run (most recent `CaseState`).
    - `latest_pipeline_status`: optional `CaseStatus`. Denormalised from the most recent `CaseState.status`.
    - `latest_final_report_path`: optional string. Relative path to the most recent final report (`.docx` or `.md`). Populated by post-hook `persist_artifact`.
    - `document_count`: integer. Total documents registered across all sessions. Sourced from `DocumentIndex`.
    - `has_engagement_letter`: bool. Denormalised from `ProjectIntake.engagement_letter_registered`.
    - `language_standard`: string. From `ProjectIntake`.
    - `case_ids`: list of strings. All `case_id` values linked to this project (all pipeline runs, in chronological order).
    - `project_health`: `Literal["no_materials", "materials_only", "pipeline_running", "draft_ready", "final_approved", "error"]`. Computed field — not stored by Maher, derived at read time:
      - `no_materials` — project created, zero documents, zero notes
      - `materials_only` — documents/notes present, no pipeline run yet
      - `pipeline_running` — a `CaseState` with non-terminal status exists
      - `draft_ready` — latest `CaseState.status` is `PARTNER_REVIEW_COMPLETE` or `OWNER_READY`
      - `final_approved` — latest `CaseState.status` is `OWNER_APPROVED` or `DELIVERABLE_WRITTEN`
      - `error` — latest `CaseState.status` is `PIPELINE_ERROR`
  - Persistence: `ProjectState` is serialised to `cases/{project_slug}/project_state.json`. This file is the single source of truth for the project-level status that the Case Tracker reads.
  - Update triggers: `ProjectState` is updated (recomputed + overwritten atomically) after:
    1. Any `InputSession` closes
    2. Any `CaseState` transition (hooked via `post_hooks.append_audit_event`)
    3. Any document registration
  - Relationship to `CaseState`: one project → many `CaseState` records. Each `CaseState` has a `case_id` (UUID) and a `project_slug` field (new field to add to `CaseState`). `ProjectState.case_ids` lists all of them.
  - Case Tracker rendering: Case Tracker reads `project_state.json` for new-format projects. For legacy UUID cases (no `project_state.json`), it reads `state.json` directly. Both paths must produce a renderable row in the tracker table.
  - Audit trail: `audit_log.jsonl` at the project root records all events across all pipeline runs in this project. It is project-scoped, not case-scoped, in the new model.

**Edge cases:**
  - Project with no pipeline runs: `latest_case_id = None`, `latest_pipeline_status = None`, `project_health = "materials_only"` (or `"no_materials"` if nothing uploaded).
  - Pipeline run fails and Maher retries: `case_ids` has two entries; `latest_case_id` points to the retry; `latest_pipeline_status` reflects the retry's current status.
  - `project_state.json` is missing but project folder exists (e.g. manual creation or corruption): Case Tracker detects missing file, logs a warning, renders the row with `project_health = "error"` and a "Repair" action that regenerates `project_state.json` from existing `state.json` and `document_index.json`.
  - Legacy UUID case opened: no `ProjectState` for it. Case Tracker renders it directly from `state.json`. No migration required.

**Out of scope:** Cross-project aggregation (no firm-level summary schema in v1). Project archiving or deletion. `ProjectState` as a user-editable file (it is machine-written only).

**Open questions for AK:**
  - Should `CaseState` gain a `project_slug` field in this sprint, or is the link maintained only in `ProjectState.case_ids`? (Bidirectional link vs one-directional.) Architect preference affects schema diff.
  - Should `project_health` be a computed Pydantic property (derived at model construction) or a stored field updated by hooks? Stored is more resilient across restarts; computed is always fresh. Trade-off is resumability vs consistency.

---

### BA-EMB-01 — EmbeddingEngine Business Rules
- Status: DRAFT
- Scope: `tools/embedding_engine.py` — EmbeddingEngine class; wiring into `DocumentManager.register_document()`

**User outcome:** When Maher uploads a document, it is automatically embedded so that later, when the AI pipeline drafts findings, it can retrieve only the relevant 3–5 chunks for each finding area — instead of forcing the full document into every agent call.

**Business rules:**

**When to embed:**
  - Embedding runs as a step inside `DocumentManager.register_document()`, after text extraction and section indexing, before returning the `DocumentEntry`.
  - Embedding is always async from the user's perspective — it must not block the "document registered" confirmation Maher sees. Implementation: run embedding synchronously but after the index save, so the UI is unblocked.
  - Only embed documents where text extraction succeeded. If `text == "[EXTRACTION FAILED: ...]"`, skip embedding and log a warning to `audit_log.jsonl`.
  - Duplicate documents (detected by hash): do not re-embed. The existing vector entries are still valid.

**Chunking rules:**
  - Target chunk size: 500 tokens (~2,000 chars). Use a sliding window with 10% overlap (~50 tokens) to preserve context across chunk boundaries.
  - Split on sentence boundaries where possible (do not cut mid-sentence). Fallback: split on paragraph breaks. Final fallback: hard split at char limit.
  - Each chunk carries metadata: `doc_id`, `project_slug`, `case_id`, `chunk_index` (integer), `section_id` (from `DocumentSection` if available), `filename`, `source_excerpt` (first 100 chars of chunk for display in search results).
  - Minimum chunk size: 100 chars. Chunks shorter than this are merged into the previous chunk.
  - Excel files: each sheet is treated as a separate chunk group. Row data is chunked by row batches (50 rows per chunk) rather than by character count.

**Model and index:**
  - Embedding model: `all-MiniLM-L6-v2` (default sentence-transformers model, ~80MB download). This model downloads automatically on first use via `sentence-transformers` library. The download is ~90MB and requires internet connectivity.
  - Vector store: ChromaDB, persistent collection at `cases/{project_slug}/D_Working_Papers/vector_index/` (P9 projects) or `cases/{case_id}/vector_index/` (legacy).
  - Collection name: `case_{project_slug}` (or `case_{case_id}` for legacy). One collection per project.
  - Each document adds its chunks to the project's shared collection — not a separate collection per document.

**Fallback behaviour (R-NEW-07 — mandatory):**
  - On `EmbeddingEngine` instantiation: attempt to import `sentence_transformers` and `chromadb`. If either import fails: set `self.available = False`. Log once to stderr: "sentence-transformers or chromadb not available — falling back to full-document context". Do not raise an exception.
  - If `self.available = False`: `embed_document()` is a no-op. `retrieve_chunks()` returns `None`. Callers must check the return value and fall back to full-document reading via `DocumentManager`.
  - If model download fails (network unavailable): catch the download exception, set `self.available = False` with the same fallback behaviour. Log: "sentence-transformers model download failed — offline mode detected, falling back to full-document context".
  - Fallback is silent to Maher — he should never see an error from the embedding system. It either works or it does not; the pipeline continues either way.
  - `DocumentEntry` gains an `embedding_status` field: `Literal["embedded", "skipped_extraction_failed", "skipped_fallback", "pending"]`. Set at registration. Used by pipeline to decide retrieval strategy.

**Retrieval contract — what the agent receives:**
  - Entry point: `EmbeddingEngine.retrieve_chunks(query: str, project_slug: str, n_results: int = 5, doc_ids: list[str] | None = None) -> list[ChunkResult] | None`
  - Returns `None` if `self.available = False` (caller falls back to full-document context).
  - `ChunkResult` fields: `chunk_text` (the chunk), `doc_id`, `filename`, `section_id` (optional), `chunk_index`, `distance` (ChromaDB cosine distance), `source_citation` (formatted string: `"{filename} — {section_title or 'Section unknown'}, chunk {chunk_index}"`).
  - Results are ranked by distance (ascending — lower = more similar). Top `n_results` returned.
  - Optional `doc_ids` filter: restricts retrieval to chunks from specified documents only (for when the pipeline knows which documents are relevant).
  - Maximum total chars returned across all chunks: 8,000 chars (configurable via `config.EMBEDDING_RETRIEVE_MAX_CHARS`). If top-N chunks exceed this limit, truncate the lowest-ranked chunks (not the text within a chunk — drop whole chunks).
  - Agent-facing context format: the pipeline wraps `ChunkResult` list into a formatted context block before injecting into the agent prompt:
    ```
    [RELEVANT EVIDENCE — retrieved from vector index]
    Source: {source_citation}
    ---
    {chunk_text}
    ---
    [END EVIDENCE BLOCK]
    ```
  - Provenance preserved: `source_citation` is included so the agent can attribute findings to the correct document and section.

**What gets indexed:**
  - All document types that produce extractable text: `.txt`, `.md`, `.pdf`, `.docx`, `.csv`, `.eml`, `.msg`.
  - Excel (`.xlsx`, `.xls`): indexed in row-batch chunks (see chunking rules above).
  - Engagement letter: indexed like any other document — no special exemption.
  - Documents where extraction fails (`[EXTRACTION FAILED: ...]`): not indexed. `embedding_status = "skipped_extraction_failed"`.

**Edge cases:**
  - Empty document (zero chars after extraction): `embedding_status = "skipped_extraction_failed"`. No chunks created. No error raised.
  - Very short document (<100 chars total): treated as a single chunk. Embedded as-is.
  - Collection already exists when re-registering after crash: ChromaDB `get_or_create_collection` handles idempotency. Duplicate chunk detection: check by `doc_id + chunk_index` metadata before inserting.
  - Project has many documents and vector index grows large: no size cap in v1. Flag as a future concern if index exceeds 1GB.
  - `n_results` requested is larger than total chunks in collection: return all available chunks. No error.

**Out of scope:** Fine-tuning or custom embedding models. Per-agent embedding collections. Cross-project retrieval. Hybrid BM25 + vector search (v1 vector only).

**Open questions for AK:**
  - Should the embedding step happen synchronously inside `register_document()` (adds latency per upload but keeps things simple) or asynchronously in a background thread (faster UX but adds complexity)? Given Streamlit's threading model, async is non-trivial. BA recommendation: synchronous in v1, with a spinner shown while embedding runs.
  - Should `retrieve_chunks()` be exposed as a tool that agents can call themselves (tool_use loop), or should the orchestrator pre-fetch chunks before invoking each agent? BA recommendation: orchestrator pre-fetches once per finding area and injects as context — cleaner than giving agents a retrieval tool.

---

### BA-WORK-01 — Interim Workpaper Generation
- Status: CONFIRMED — 2026-04-19 (AK answered all 3 questions)
- Scope: NEW DESIGN — mid-engagement workpaper as a named deliverable, available inside the Input Session workspace

**AK decisions (2026-04-19):**
- Trigger: available at ANY point after Junior draft exists — mid-pipeline OR post-pipeline. Maher has full control.
- Structure: Maher-driven at generation time. Generator presents each of the 9 sections as opt-in/opt-out, asks if anything additional is needed. Fixed structure rejected — Maher configures per workpaper.
- Promotion: workpapers CAN be promoted to final reports. Maher reviews, confirms, system applies full report template, writes to `F_Final/` with `PROMOTED_FROM_WORKPAPER` flag in audit_log.

**User outcome:** Partway through an engagement, Maher can generate a professional interim workpaper that documents what has been found so far — structured finding notes, open questions, evidence references, and a status summary. This is NOT a final report. It is an internal document that keeps the engagement organised and can be shared with a supervisor, co-consultant, or used as a progress memo to the client.

**Background (domain context):** In physical forensic engagements, consultants maintain working papers throughout — structured notes on what has been reviewed, what findings are emerging, what questions remain open. These are the audit trail between "raw evidence" and "final report". A sole practitioner like Maher currently has no structured way to capture this mid-engagement state in the tool. Without it, he either keeps informal notes outside the tool (breaking the audit trail) or waits until the full pipeline run to see any structured output.

**Business rules:**

**Trigger:**
  - Available from the Input Session workspace, from the moment at least one document is registered and at least one session note or key fact has been added. Not available on a zero-material project.
  - Triggered manually by Maher: "Generate Interim Workpaper" button in the Streamlit workspace sidebar. Never auto-triggered.
  - Can be generated multiple times. Each generation creates a new versioned file (`D_Working_Papers/interim_workpaper.v1.md`, `v2`, etc.). Previous versions are preserved, not overwritten.
  - Does NOT require the full 3-agent pipeline. It is a single-agent (Sonnet) generation, much faster (~30 seconds target).

**What goes in an interim workpaper:**
  1. **Header**: Project name, client name, engagement type, date generated, "PRELIMINARY — NOT FOR DISTRIBUTION" watermark (in the DOCX header and MD front-matter).
  2. **Materials reviewed to date**: auto-generated from `DocumentIndex` — list of all registered documents with brief summary of each (from `DocumentEntry.summary`).
  3. **Key facts established**: pulled from `D_Working_Papers/key_facts.json` — formatted as a numbered list with source attribution.
  4. **Red flags identified**: pulled from `D_Working_Papers/red_flags.json` — formatted by severity (high → medium → low). Each red flag includes source and action status.
  5. **Emerging findings** (Sonnet-generated): model reviews accumulated materials (via embedding retrieval if available, else full-document) and drafts 3–7 emerging finding narratives. Each finding: title, evidence observed so far, implication (tentative), open questions to confirm or refute. Language standard: ACFE Internal Review regardless of project setting (workpapers are always internal). All findings labelled "PRELIMINARY — subject to further investigation".
  6. **Leads register status**: pulled from `D_Working_Papers/leads_register.json` — open leads listed with current status. Confirmed leads flagged as likely to be in final report.
  7. **Matters pending / open questions**: compiled from `open_questions` in emerging findings + open leads + any unanswered items from `D_Working_Papers/intake_qa.json`.
  8. **Next steps**: Sonnet proposes 3–5 specific next steps based on open questions and red flags. Maher can edit these before saving.
  9. **Audit trail summary**: count of sessions, documents registered, facts recorded — a one-line status.

**Generation pipeline:**
  - Single agent: Sonnet (not the full Junior → PM → Partner chain).
  - Model is explicitly instructed: "This is a preliminary internal workpaper. Do not present findings as conclusions. Use qualified language throughout ('evidence suggests', 'it appears', 'further review required'). Every finding must reference at least one registered document by filename."
  - No PM or Partner review step. Maher reviews the output directly.
  - Language standard injection: ACFE Internal Review, hardcoded for workpapers (not overridable).
  - Output formats: `.md` only (no DOCX for workpapers — internal document, not client-facing). Saved to `D_Working_Papers/interim_workpaper.v{N}.md`.
  - Workpaper generation does NOT transition `CaseState`. It is not a pipeline event. It does NOT write to `E_Drafts/` or `F_Final/`.
  - Audit log entry: `append_audit_event` records a `WORKPAPER_GENERATED` event (new event type) with version number and Sonnet model used.

**Evidence chain enforcement:**
  - Every emerging finding must cite at least one `DocumentEntry` by `doc_id` and `filename`. If no supporting evidence exists in the registered materials, the finding must be labelled "ANALYTICAL INFERENCE — no documentary evidence found yet".
  - Findings labelled ANALYTICAL INFERENCE are highlighted in the output with a warning: "This observation is based on the model's analysis of the client/industry context, not on a registered document. Do not include in final report without documentary support."
  - This is how workpapers differ from the full pipeline: the evidence chain is tracked but the bar is lower — provisional findings with explicit provenance labels are acceptable here, whereas the Partner agent would reject them.

**Edge cases:**
  - No documents registered yet: "Generate Interim Workpaper" is greyed out with tooltip "Upload at least one document to generate a workpaper."
  - Only engagement letter registered (no substantive evidence): workpaper can still be generated. Sections 3–6 will be sparse; model notes this explicitly in the output.
  - Workpaper generated, then more documents uploaded, then workpaper generated again: both versions preserved. Version history shown in sidebar. Maher can compare.
  - Workpaper content conflicts with later final report (common — findings evolve): workpapers are explicitly internal. The DOCX header "PRELIMINARY — NOT FOR DISTRIBUTION" is the control. No reconciliation logic needed between workpaper and final report.
  - Maher wants to share the workpaper with a client: the tool does not prevent it, but the "PRELIMINARY — NOT FOR DISTRIBUTION" header is always present. If Maher wants a client-facing interim memo, he should run the full pipeline (which has the Partner review gate).

**Out of scope:** Workpaper → final report auto-merge (promotion is manual, not automatic). Workpaper review by a separate agent (one-pass Sonnet, reviewed by Maher). Workpapers for Mode B workflows (Proposal, Policy, Training — one-pass, no workpaper needed).

**Promotion audit chain (Codex finding — required before WORK-01 build):**
- Source workpaper is IMMUTABLE after generation. No edits, no overwrites. Version N stays frozen.
- Promotion creates a NEW artifact: new output ID, new filename (`final_report.en.md` not `workpaper_...`), new header/footer regime (removes PRELIMINARY banner, applies full report template).
- Mandatory audit event on promotion: `WORKPAPER_PROMOTED` with fields: `source_workpaper_version`, `source_workpaper_path`, `promoted_at` (ISO-8601), `promoted_by: "Maher"`, `new_output_id`.
- Final report produced by promotion is indistinguishable from a pipeline-generated final report in the output folder — but audit_log.jsonl always contains the WORKPAPER_PROMOTED lineage event.
- If audit_log.jsonl is missing or corrupt at promotion time: BLOCK promotion. Do not allow a final report to exist without a traceable origin.

**Open questions for AK:** None — all resolved 2026-04-19.

---

### BA-CONV-01 — Conversational Evidence Mode
- Status: CONFIRMED — 2026-04-19 (AK answered placement and scope questions)
- Scope: NEW DESIGN — exploratory conversation mode over registered case documents; distinct from the pipeline and from general chat

**AK decisions (2026-04-19) — UPDATED post-Codex review:**
- Placement: persistent collapsible chat panel on ALL engagement pages.
- Implementation: NOT via bootstrap(). bootstrap() is a one-time initializer (session.py:52 early return) — wrong place for rendering on every rerun.
- Correct implementation: new `streamlit_app/shared/engagement_shell.py` — wraps all engagement workflow pages (NOT settings, NOT tracker). Calls bootstrap() for init, then renders the chat panel on every rerun. Each engagement page calls `engagement_shell.render(st)` at top instead of calling bootstrap() directly.
- Settings, Case Tracker, Team, and 00_Setup pages continue to call bootstrap() only — no panel injected.

**User outcome:** Maher can open a registered case document and have a back-and-forth conversation with the model about it — asking "What does this email chain say about the approval process?", "Does this transaction pattern suggest structuring?", "Flag anything suspicious in pages 12–18" — without triggering the full pipeline. The conversation is saved as a working paper, so leads and observations from the conversation are not lost.

**Background (domain context):** Evidence review in forensic work is non-linear. A consultant reads a bank statement, notices an anomaly, asks a question, follows a thread, backtracks, re-reads a different document. The current pipeline model forces a linear flow: ingest → pipeline run → review output. That is the right model for final deliverables. But it is the wrong model for discovery. Discovery is conversational. The gap is: Maher currently has no way to have that conversational exploration within the tool, with the output preserved as case evidence.

**Business rules:**

**When it is available:**
  - Conversational Evidence Mode (CEM) is available in the Input Session workspace for any project that has at least one document registered.
  - Entry point: "Explore Documents" or "Evidence Chat" button in the Streamlit workspace sidebar.
  - Available at any time during the project lifecycle — before, during, and after pipeline runs. It is independent of pipeline state.

**How it differs from a pipeline run:**
  - CEM is NOT a pipeline run. It does not create a `CaseState`. It does not trigger Junior, PM, or Partner agents. It does not write to `E_Drafts/` or `F_Final/`.
  - CEM is NOT general chat. The model is strictly scoped to the registered documents of this project. It may not introduce external knowledge as findings — only as context ("this pattern is consistent with a structuring scheme, which is a form of AML…"). External knowledge as explanation is allowed; external knowledge as evidence is not.
  - The model in CEM operates as a "document assistant", not as a drafting agent. It surfaces, quotes, and explains what is in the documents. It does not draft findings or conclusions.

**Conversation mechanics:**
  - Model used: Sonnet (for analytical depth; Haiku is insufficient for multi-document evidence reasoning).
  - System prompt for CEM: "You are reviewing the documents registered for this forensic engagement. You can only present findings and observations that are directly supported by the registered documents. For each observation, state the source document and quote the relevant passage. You may explain forensic concepts, fraud patterns, and regulatory context as background. You must not present inferences as conclusions. All observations are preliminary."
  - Context injection: at conversation start, the model receives:
    1. `DocumentIndex` summary (all registered documents: filename, doc_type, brief summary).
    2. `key_facts.json` and `red_flags.json` (accumulated context from prior sessions).
    3. The first user message.
  - On each user turn: if the query references specific content (e.g. "look at the bank statement"), `EmbeddingEngine.retrieve_chunks()` is called with the user query to fetch relevant chunks. Chunks are injected as context before the model responds. If embedding is unavailable: `DocumentManager.find_relevant_docs()` is used to identify relevant documents, and `read_excerpt()` is used to retrieve content.
  - Document-specific conversations: Maher can say "focus on [filename]" — all subsequent retrieval is filtered to that `doc_id`.
  - Multi-document reasoning: Maher can ask "compare the vendor list in the PO register with the vendor list in the payment run" — model retrieves from both documents and reasons across them.
  - No context window per turn limit is imposed by CEM, but total injected context per turn (chunks + conversation history) is capped at `config.CEM_CONTEXT_CHARS` (default: 16,000 chars). Oldest conversation turns are dropped first when this limit is approached (sliding window on conversation history).

**State saving — what gets preserved:**
  - CEM conversation persistence: the full conversation (user turns + model turns) is saved to `D_Working_Papers/evidence_chat_{YYYYMMDD_HHMMSS}.md` on session close. Append-only. Each new CEM session in the same project creates a new file.
  - Lead capture: during the conversation, Maher can click "Save as Lead" on any model response. This extracts the model's observation and appends it to `D_Working_Papers/leads_register.json` with:
    - `source: "evidence_chat"`, `session_file: "evidence_chat_{timestamp}.md"`, `status: "Open"`, `description`: the model's observation text.
  - Key fact capture: Maher can click "Save as Key Fact" on any model response. Appends to `D_Working_Papers/key_facts.json` with `source_doc_id` and `source_excerpt` from the chunk that generated the observation.
  - Red flag capture: same mechanism — "Save as Red Flag" button on model responses.
  - All saved leads, facts, and red flags from CEM are then available in the Input Session workspace and are passed to the pipeline on the next Final Run.
  - Conversation is NOT automatically converted into a pipeline input. Maher explicitly promotes observations by clicking "Save as Lead/Fact/Red Flag". Unsaved observations are in the chat transcript only.

**Evidence chain integrity:**
  - Every model response in CEM that makes an evidentiary observation must include a source attribution inline: "(Source: {filename}, {section or chunk reference})". Model is instructed to do this in the system prompt.
  - Model may NOT make an evidentiary observation if no registered document supports it. If asked "Do you think there's fraud here?", model responds: "Based on the documents registered so far, I can note the following observations…" and lists only document-supported items.
  - CEM conversations are stored but are NOT part of the formal audit trail (`audit_log.jsonl`). They are working materials. The formal audit trail event is only written when a Lead, Key Fact, or Red Flag is saved from the conversation.

**Session management:**
  - CEM session starts when Maher opens the "Explore Documents" view.
  - CEM session ends when Maher closes the view or explicitly clicks "End Conversation".
  - On session end: conversation saved to `D_Working_Papers/evidence_chat_{timestamp}.md`. Summary of leads/facts/flags saved during the session shown to Maher before close.
  - Conversation history is NOT loaded on next CEM session start (each conversation starts fresh). Prior conversations are accessible as read-only files in the Working Papers view.

**Edge cases:**
  - Maher asks about a document that has not been registered: model responds "I don't have access to that document. Please register it in the Evidence folder first."
  - Maher asks a general knowledge question unrelated to the case: model responds in context ("In the context of this engagement…") and directs back to the registered documents. It does not refuse, but it also does not provide general advice detached from the case.
  - Very long conversation (>50 turns): oldest turns are dropped from context (sliding window). A banner warns Maher when history is being trimmed. Full transcript is still preserved in the saved file.
  - Maher closes the app mid-conversation without ending the session: auto-save to `D_Working_Papers/evidence_chat_{timestamp}_recovered.md`. Any leads/facts/flags already clicked "Save" on are preserved in the JSON files (they are saved on click, not on session close).
  - Model produces a response that Maher believes misquotes the document: Maher can click "Flag Response" — this appends a `FLAGGED` annotation to the conversation transcript. Flagged responses are not saved as leads/facts. No further automated action.
  - Embedding unavailable (fallback mode): CEM still works via keyword search + excerpt. Performance degrades — model receives less targeted context. Banner shown: "Semantic search unavailable — using keyword matching. Results may be less precise."

---

## Session 024 — Report Templates & Config

### BA-TPL-01 — Report Template Management System
- Status: DRAFT
- Scope: Settings → Templates tab; `firm_profile/templates/` directory; `update_report_template` tool; `OutputGenerator.generate_docx()` fallback logic

**User outcome:** Maher can manage branded Word templates per workflow type from the Settings page. Base templates are pre-installed and always present as a fallback. Uploading a custom template overrides the base for that workflow type without deleting it.

**Business rules:**
  - One template slot per workflow type. Supported workflow types: `frm_risk_register`, `investigation_report`, `client_proposal`, `due_diligence`, `sanctions_screening`, `transaction_testing`, `workpaper`.
  - Base templates ship with the product as `firm_profile/templates/{workflow_type}_base.docx`. They are read-only — never deletable and never overwritten by an upload. They serve as permanent fallback.
  - Custom templates are stored as `firm_profile/templates/{workflow_type}_custom.docx`. Uploading a new custom template for a workflow type that already has one triggers versioning before saving: the existing `_custom.docx` is renamed to `{workflow_type}_custom.v{N}.docx` where N is the next available integer. The new file is then saved as `_custom.docx`.
  - The Settings page exposes a **Templates** tab. For each workflow type, the tab shows: (a) whether a custom template exists, (b) the version history (list of `_custom.v{N}.docx` files), and (c) an upload control to replace the current custom template.
  - Upload is handled via the `update_report_template(workflow_type: str, file_bytes: bytes)` AI tool call. The tool: (1) validates the file is a valid .docx (magic bytes check), (2) checks file size ≤ 5 MB, (3) opens the file with `python-docx` and extracts named paragraph styles, (4) verifies that all seven required styles are present: `GW_Title`, `GW_Heading1`, `GW_Heading2`, `GW_Body`, `GW_TableHeader`, `GW_Caption`, `GW_Disclaimer`, (5) if valid, rotates the existing custom template (versioning step above), then saves the new file.
  - `OutputGenerator.generate_docx()` resolves the template path at generation time: checks for `{workflow_type}_custom.docx` first; if absent or if the file is unreadable, falls back to `{workflow_type}_base.docx`. The resolution is logged to audit_log as `{event: "template_resolved", template: "<filename>", fallback: true/false}`.
  - If `_custom.docx` exists but is missing one or more required named styles at generation time, `OutputGenerator` falls back to the base template and logs a warning: `{event: "template_fallback", reason: "missing_required_styles", missing: [...], fallback_to: "{workflow_type}_base.docx"}`.
  - Template versioned history is retained indefinitely (no auto-purge). Maher can download any version from the Templates tab but cannot re-activate a past version directly — they must re-upload it.

**Edge cases:**
  - Upload is not a valid .docx (e.g. a .pdf or a renamed file): tool returns error `"invalid_file_type"`. No file is saved. UI shows: "File must be a valid .docx document."
  - File exceeds 5 MB: tool returns error `"file_too_large"`. No file is saved. UI shows: "Template file must be under 5 MB."
  - File is a valid .docx but is corrupted (python-docx raises on open): tool returns error `"file_corrupted"`. No file is saved. UI shows: "The uploaded file could not be read. Please check the file and try again."
  - One or more required named styles are missing: tool returns error `"missing_required_styles"` with a list of the missing style names. No file is saved. UI shows the list so Maher can correct the template in Word before re-uploading.
  - `firm_profile/templates/` directory does not yet exist at upload time: tool creates it before saving.
  - Base template file is missing from the install (e.g. corrupted install): `OutputGenerator` raises a hard error and surfaces it to Maher in the UI. Generation is blocked until the base template is restored.
  - Maher uploads the same file a second time (identical bytes): tool still proceeds normally — versioning runs, a new `_custom.docx` is saved, and the previous one is versioned. No de-duplication check.

**Out of scope:** PPTX template management (separate feature, not in this sprint). Multi-user template sharing or a cloud template library. In-app template editing or style management (Maher edits templates in Microsoft Word externally). Automated style injection (tool does not add missing styles — it rejects uploads that lack them).

**Open questions for AK:**
  - Should the Templates tab show a preview thumbnail of the first page of each template, or is a filename + upload-date listing sufficient for v1?
  - Do versioned templates (`_custom.v{N}.docx`) need a UI to download them, or is access via the file system acceptable for now?
  - Should `GW_Disclaimer` be mandatory for all workflow types, or only for investigation_report and sanctions_screening? Some workflows (e.g. training_material) may not have a disclaimer section.

---

### BA-TPL-02 — Engagement-Time Template Selection
- Status: DRAFT
- Scope: Intake UI (Zone A, all workflow types); case `state.json`; audit_log; one-time upload flow

**User outcome:** At the start of every engagement, Maher is explicitly asked which report template to use before the pipeline runs. There is no silent default. The choice is recorded in the case state and audit trail.

**Business rules:**
  - The template selector is the last item rendered in Zone A (intake) for every workflow type, immediately before the Run button. It is never hidden or auto-skipped.
  - The selector presents up to three options, depending on what templates exist for the workflow type:
    - **(a) Global saved template** — shown only if `{workflow_type}_custom.docx` exists in `firm_profile/templates/`. Label: "Use saved template: {workflow_type}_custom.docx (uploaded {date})". This option is pre-selected by default when available.
    - **(b) One-time upload for this engagement** — always shown. When selected, a file uploader appears inline in Zone A. The uploaded file is validated (same .docx + size check as BA-TPL-01) but is NOT saved to `firm_profile/templates/`. It is stored temporarily for this pipeline run only (in memory or as a temp file scoped to the session). After the engagement run completes, the file is discarded.
    - **(c) No template — plain Word output** — always shown. OutputGenerator generates a document using python-docx defaults (no named styles applied, no firm branding). This is the correct option for quick internal drafts.
  - If no custom template exists for the workflow type, option (a) is suppressed. Maher sees only (b) and (c). There is no "use base template" option exposed to Maher — the base template is an internal fallback only.
  - Maher's selection is stored in `state.json` under the key `report_template_used`. Value format:
    - Option (a): `{"source": "global", "filename": "frm_risk_register_custom.docx", "resolved_at": "<ISO timestamp>"}`
    - Option (b): `{"source": "one_time", "filename": "<original upload filename>", "resolved_at": "<ISO timestamp>"}`
    - Option (c): `{"source": "none", "filename": null, "resolved_at": "<ISO timestamp>"}`
  - Template selection is recorded in `audit_log.jsonl` at the moment Maher clicks Run (not at the moment of selection). Event format: `{event: "template_selected", workflow: "<workflow_type>", template: "<filename or null>", scope: "global" | "one_time" | "none", case_id: "<id>", timestamp: "<ISO>"}`.
  - If Maher does not interact with the template selector (e.g. scrolls past it and clicks Run without choosing), the system applies the pre-selected default: (a) if a custom template exists, (c) otherwise. The audit event is still written with `scope: "global"` or `scope: "none"` as appropriate.
  - The one-time upload (option b) does NOT trigger the `update_report_template` AI tool. It is a direct file read by `OutputGenerator` with the same validation checks (valid .docx, ≤ 5 MB, required styles present). If validation fails, Run is blocked and the error is shown inline.
  - For one-time uploads, missing required styles cause a warning (not a hard block): "Template is missing styles: [list]. Output will use default formatting for those sections." Maher can proceed or cancel and fix the template.

**Edge cases:**
  - Maher selects option (a) (global template) but the file has been deleted from `firm_profile/templates/` between selection and the time OutputGenerator runs: OutputGenerator falls back to the base template. A warning banner is shown in Zone B: "Saved template not found — using base template instead." The audit event is updated with `fallback: true`.
  - Maher selects option (b) and uploads a file, then changes selection to option (c): the uploaded file is discarded immediately (removed from memory/temp). No file persists.
  - Maher uploads a file for option (b) that fails validation (invalid .docx, too large, or corrupted): the Run button remains disabled. The error is shown inline next to the uploader. Maher must either fix the file or choose a different option before Run is enabled.
  - The workflow type has no base template in `firm_profile/templates/` (broken install): same hard error as BA-TPL-01 — generation is blocked, error surfaced to Maher.
  - Maher resumes an in-progress case (non-terminal state.json): the template selector is not re-shown. The template recorded in `state.json` at first run is used. Maher cannot change the template mid-engagement without starting a new case.

**Out of scope:** Allowing Maher to change the template after a pipeline run has started. Template preview inside the Streamlit UI. Applying different templates to different sections of the same report. PPTX template selection (separate).

**Open questions for AK:**
  - For option (b) one-time uploads: if the upload is missing required styles and Maher proceeds with the warning, should the fallback for those specific sections come from the base template's styles or from python-docx defaults? Base template styles would produce more consistent output but is slightly more complex to implement.
  - Should the template selector state be preserved if Maher refreshes the browser mid-intake (before clicking Run)? Or is losing the selection on refresh acceptable in v1?
  - Is there a case where Maher wants to save a one-time upload as the new global template immediately after using it? If so, a "Save to firm templates" checkbox on option (b) would cover this without a separate Settings round-trip.

**Out of scope:** Real-time collaboration in CEM (multiple users). CEM conversations as discoverable legal documents (they are working papers, explicitly marked as such). Automated Lead extraction without Maher clicking "Save as Lead" (never auto-extract — Maher controls what enters the case record). CEM for Mode B workflows (Proposal, Policy, Training — these do not have evidence documents in the forensic sense).

---

## Session 024 — Setup, Activity Ledger, Knowledge Architecture

---

### BA-SETUP-01 — First-Run Setup Page (00_Setup.py)
- Status: CONFIRMED — 2026-04-19
- Scope: Streamlit-native first-run setup replacing CLI wizard as primary onboarding path

**User outcome:** Maher completes full setup in browser on first run. App unlocks all workflows only after setup is verified complete. CLI wizard (core/setup_wizard.py) retained as recovery tool only.

**Business rules:**
  - Detection: on every bootstrap(), check readiness from actual artifacts — NOT from setup.json alone:
    1. `.env` readable and `ANTHROPIC_API_KEY` non-empty
    2. `firm_profile/firm.json` readable and `firm_name` non-empty
    3. `firm_profile/team.json` readable and contains at least one member
    4. `firm_profile/pricing_model.json` readable
    5. `assets/templates/` contains at least `base_report_base.docx`
  - setup.json is a CACHE of the last readiness check result — not the authority. If missing or corrupt: rebuild from facts above. Never lockout a working install due to missing setup.json.
  - If readiness check fails: `st.switch_page("pages/00_Setup.py")` — all other pages redirect here until complete.
  - Setup sequence (exact order):
    1. Write `.env` with ANTHROPIC_API_KEY (required), TAVILY_API_KEY (optional), RESEARCH_MODE
    2. Write `firm_profile/firm.json` — firm name (required), logo path, tagline
    3. Write `firm_profile/team.json` — at least one team member (required)
    4. Write `firm_profile/pricing_model.json` — pricing model (required)
    5. Verify all 5 readiness checks pass
    6. Write `firm_profile/setup.json` with `setup_complete: true, setup_version: 1, completed_at: ISO-8601`
    7. Call `load_dotenv(override=True)` to pick up new .env without restart
    8. Redirect to landing page
  - TAVILY_API_KEY is optional — app degrades to knowledge_only mode without it. No block.
  - Custom templates are optional — app uses assets/templates/ bases. No block.
  - If Maher skips a required step and tries to proceed: BLOCK with exact missing items listed. No silent degradation for required items.
  - core/setup_wizard.py retained as CLI recovery tool only — not the primary path.

**Edge cases:**
  - .env written but ANTHROPIC_API_KEY is invalid: setup shows "Test connection" button. Failed test blocks completion. Partial .env stays on disk — next attempt overwrites it.
  - setup.json deleted mid-use on a working install: readiness check passes (all artifacts present), setup.json rebuilt silently, app continues normally. No lockout.
  - Maher reinstalls app on new machine: firm_profile/ is gitignored so it is empty. Setup runs from scratch. cases/ are also gone — expected. Document this in README.
  - load_dotenv(override=True) called after .env write: config-dependent clients (Anthropic, Tavily) must be rebuilt after this call. Add a `config.reload()` function that re-reads env and rebuilds clients.

**Out of scope:** Multi-user onboarding. Cloud deployment setup. Automated backup of firm_profile/.

**Open questions for AK:** None.

---

### BA-ACT-01 — Activity Ledger
- Status: CONFIRMED — 2026-04-19
- Scope: App-wide structured activity log capturing all user and system actions

**User outcome:** Maher can open the Activity Log page, search by date/time and category, and see a complete record of everything the app has done — every page visit, pipeline run, file write, settings change, and error.

**Business rules:**
  - ALL actions are logged — no filtering at write time. Categories:
    - SESSION: app opened, app closed, page navigated to, session duration
    - SETUP: first run completed, API key added/updated/tested, firm profile updated, team member added/edited, pricing updated, T&C updated
    - ENGAGEMENT: new engagement created, engagement opened, engagement status changed
    - PIPELINE: workflow started, agent started, agent completed, revision requested, pipeline completed, pipeline failed, pipeline resumed
    - DOCUMENT: document uploaded, document registered, document indexed, document removed
    - DELIVERABLE: draft generated, review decision (approve/flag/skip), final report written, workpaper generated, workpaper promoted to final (with WORKPAPER_PROMOTED fields), report downloaded
    - KNOWLEDGE: historical report ingested, knowledge file updated, library indexed
    - TEMPLATE: template uploaded, template validated, template set as active, template reset to base
    - SETTINGS: any settings change with old_value → new_value
    - ERROR: pipeline error, API error, file write failure, embedding failure
  - Event schema (every event):
    ```json
    {
      "event_id": "uuid4",
      "timestamp_utc": "ISO-8601",
      "category": "PIPELINE",
      "action": "agent_completed",
      "actor": "system",
      "engagement_id": "slug-or-null",
      "case_id": "id-or-null",
      "detail": {},
      "status": "SUCCESS|FAILURE|WARNING"
    }
    ```
  - Storage: `logs/activity.jsonl` — append-only JSONL. Created on first app run. Never truncated by the app.
  - Log rotation: when `logs/activity.jsonl` exceeds 50MB, rename to `logs/activity_{YYYYMMDD}.jsonl` and start a new file. Old files retained indefinitely.
  - `logs/` directory is committed to repo as an empty directory (add `logs/.gitkeep`). Log files themselves are gitignored (`logs/*.jsonl`).
  - UI: dedicated `Activity Log` page in sidebar. Date range picker + category filter + free-text search on action/detail fields. Paginated (50 events per page). Export as CSV button.
  - Access: open — no PIN, no restriction (Path A, single user).

**Edge cases:**
  - Log write fails (disk full, permissions): log failure silently, never crash the app due to logging. Emit WARNING to Streamlit sidebar once per session if log writes are failing.
  - Log file corrupt: Activity Log page shows error "Log file unreadable" with path. App continues normally — logging resumes to a new file.
  - Very large log (years of use): pagination + date filter handles this. No performance impact on app startup.

**Out of scope:** Remote log shipping. Log encryption. Role-based log access (Path A).

**Open questions for AK:** None.

---

### BA-KL-01 — Three-Layer Learning Knowledge Architecture
- Status: CONFIRMED — 2026-04-19 (Codex Part 4 design accepted)
- Scope: Knowledge base that learns from base regulatory knowledge + user historical data + approved engagement artifacts

**User outcome:** Every draft the tool produces gets smarter over time — drawing on Maher's past work and approved case patterns as well as static regulatory frameworks, all with explicit source labels so Maher knows where every suggestion came from.

**Three-layer architecture:**

**Layer 1 — BASE (highest authority)**
  - Source: `knowledge/` committed files (frm_framework.md, investigation_framework.md, etc.)
  - Index: `knowledge/manifest.json` — doc_id, domain, version, effective_date, supersedes, authority_level
  - ChromaDB collection: `kb_base`
  - Authority: wins for law, regulation, methodology statements
  - Update process: add new versioned file, mark old as superseded in manifest. Never silent overwrite.
  - Label on retrieval: `BASE`

**Layer 2 — USER (firm precedent)**
  - Source: `firm_profile/historical_registers/` and `firm_profile/historical_reports/`
  - Ingestion: `KnowledgeLibrary.ingest()` + mandatory `sanitise()` — hard-fail gate, not best-effort
  - Sanitised index: `firm_profile/knowledge/user/index.jsonl` + chunks in `firm_profile/knowledge/user/chunks/{hash}.json`
  - ChromaDB collection: `kb_user_sanitised`
  - Authority: firm-preferred framing, deliverable patterns, anonymised precedent. Never case evidence.
  - Label on retrieval: `FROM_SIMILAR_ENGAGEMENT`

**Layer 3 — ENGAGEMENT (case patterns)**
  - Source: `cases/{id}/` — harvested only after OWNER_APPROVED or DELIVERABLE_WRITTEN status
  - Export: `cases/{id}/knowledge_export/approved_patterns.json`
  - Promoted index: `firm_profile/knowledge/engagement/index.jsonl` + chunks
  - ChromaDB collection: `kb_engagement`
  - Extracted fields: workflow, industry, jurisdiction, approved finding themes, risk patterns, recommendation types, citation domains, partner sign-off outcomes, revision count
  - NEVER ingest: raw case evidence, client identifiers, document text
  - Label on retrieval: `FROM_PRIOR_ENGAGEMENT`
  - `allowed_use: ["pattern","drafting_hint"]`, `forbidden_use: ["evidence","citation"]`

**Inference-time precedence:** BASE > USER > ENGAGEMENT. Conflicts: prefer higher authority, expose conflict in metadata.

**Retrieval contract — structured bundle not raw chunks:**
```json
{
  "query": "...",
  "base_hits": [{"doc_id":"...","chunk_id":"...","label":"BASE","authority":"high"}],
  "user_hits": [{"entry_id":"...","label":"FROM_SIMILAR_ENGAGEMENT","similarity":0.82}],
  "engagement_hits": [{"entry_id":"...","label":"FROM_PRIOR_ENGAGEMENT","similarity":0.76}],
  "rules": {
    "evidence_usable_layers": ["BASE"],
    "drafting_hint_layers": ["USER","ENGAGEMENT"]
  }
}
```

**Cold start:** Day one — only BASE exists. USER and ENGAGEMENT return empty. Never an error. System degrades gracefully as layers fill.

**Risks:**
  - R-KL-01: PII leakage from Layer 2 if sanitise() is best-effort — must be HARD FAIL gate
  - R-KL-02: Evidence contamination from Layer 3 if prior engagement patterns allowed as citations
  - R-KL-03: Regulatory staleness in Layer 1 without versioned review cadence
  - R-KL-04: Model over-anchoring on prior patterns — misleading early in an engagement

**Out of scope:** Cross-firm knowledge sharing. Automated regulation update crawling (v1). Fine-tuning on engagement data.

---

### BA-FE-01 — AI Questions Stage (Post-Intake Clarification)
- Status: CONFIRMED — 2026-04-20
- Scope: FE-01 — all 10 workflow pages; the stage inserted between intake and pipeline run

**User outcome:** After completing intake, Maher sees any clarifying questions the AI identified. He answers them one at a time before the pipeline runs, or skips the stage entirely. Answers are injected into the agent context so the draft is better grounded in case-specific detail.

**Business rules:**
  - Questions are rendered one at a time using `st.chat_message` style. Each question appears as an AI message; Maher types a free-text answer and clicks Send before the next question appears.
  - A single "Skip" button is visible at all times during the questions stage. Clicking it ends the stage immediately regardless of how many questions remain.
  - Answered questions are appended to `D_Working_Papers/case_intake.md` in the format: `Q: <question text>\nA: <answer text>`.
  - Skipped (unanswered) questions are also written to `case_intake.md` in the format: `Q: <question text>\nA: [SKIPPED]`. The agent downstream sees these and knows what context is missing.
  - The questions stage is non-blocking: Maher can always skip all questions and reach the pipeline run. Zero mandatory questions.
  - State machine transition: `intake_complete → ai_questions → running`. Skipping advances directly to `running`.
  - Questions are generated by AIC-01 (already built in Sprint-AIC). The FE layer only renders AIC-01 output — it does not generate questions itself.
  - The stage is only shown if AIC-01 returns at least one question. If AIC-01 returns an empty list, the stage is skipped automatically and the pipeline proceeds.

**Edge cases:**
  - AIC-01 returns zero questions: stage is skipped silently; no UI shown; state advances to `running` automatically.
  - AIC-01 call fails (API error): stage is skipped silently; warning appended to session notes; pipeline proceeds with original intake.
  - Maher answers some questions then navigates away (browser back / page switch): partially answered questions are written to `case_intake.md` up to the last Send; remaining questions are logged as `[SKIPPED]`.
  - Maher refreshes the browser mid-stage: session state is lost; stage restarts from question 1. Answers already written to `case_intake.md` are preserved on disk but the in-memory question index resets.

**Out of scope:** Structured-choice (radio/dropdown) responses — free-text only in v1. Branching question trees. Saving question sets as templates. Showing questions in the Final Run panel (questions stage is intake-only).

**Open questions for AK:** None.

---

### BA-FE-02 — Workspace Conditional Panels (All Workflows)
- Status: CONFIRMED — 2026-04-20
- Scope: FE-06 — `pages/16_Workspace.py` Input Session mode; workflow-specific panels for every service type

**User outcome:** When Maher opens the workspace for any engagement, he sees panels relevant to that specific workflow type — not a generic set of inputs. The workspace adapts so the right data collection tools are present before Final Run.

**Business rules:**

  **Shared panels (all workflows):**
  - Semantic Search (EMB-03 — already built)
  - AIC Follow-up (inline, post-questions stage — passive display)
  - Context Budget bar (already built)

  **Workflow-specific panels:**

  | Service Type | Panel Name | Fields |
  |---|---|---|
  | Investigation Report | Exhibit Register | exhibit_id, description, date (WF-01b — already built) |
  | Investigation Report | Investigative Leads | lead_id, description, status (WF-01b — already built) |
  | FRM Risk Register | Stakeholder Inputs | name, role, key_concern, risk_view (FR-01 — already built) |
  | Due Diligence | Subject Register | name, type (Individual/Entity), relationship (Target/Related Party/Other) |
  | Sanctions Screening | Screening Targets | name, type (Individual/Entity), nationality |
  | Transaction Testing | Transaction Populations | population_name, date_range, count, source_system |

  - Panel visibility is determined by `state.service_type` (loaded from ProjectManager). Panels for other service types are not rendered — not hidden or collapsed.
  - New panels (DD Subject Register, Sanctions Screening Targets, TT Transaction Populations) persist to `D_Working_Papers/` as JSON files using the same atomic write pattern as stakeholder_inputs.json.
  - File names: `dd_subjects.json`, `sanctions_targets.json`, `tt_populations.json`.
  - All new panels are append-only: adding a subject/target/population appends to the list; no delete in v1.
  - Each entry gets a `saved_at` ISO timestamp on write (same pattern as `_save_stakeholder()`).

**Edge cases:**
  - `state.service_type` not recognised (e.g. legacy case type): show shared panels only; no workflow panel rendered; no error.
  - JSON file corrupted on disk: panel loads with empty list and a warning caption; does not crash.
  - Maher adds a DD subject with an empty name: form validation blocks save; error shown inline ("Name is required").
  - Sanctions target with empty name: same — blocked with inline error.
  - TT population with empty name or count ≤ 0: blocked with inline error ("Population name and count are required").

**Out of scope:** Editing or deleting existing subjects/targets/populations in v1. Cross-engagement subject lists. Bulk import from CSV. Workflow panels for Proposal, Policy/SOP, Training Material (Mode B workflows — no evidence collection).

**Open questions for AK:** None.

**Open questions for AK:** None.

---

## Session 036 BA — Product IA Redesign (2026-04-21)

---

### BA-IA-01 — Engagement as Root Entity (Multi-Workflow)
- Status: CONFIRMED — AK session 036
- Resolves: BA-P9-01 open question "Should a single project support multiple service types simultaneously?"

**AK decision:** YES. An engagement is the root entity for all work. A single engagement can contain multiple workflows (Investigation, FRM, DD, Sanctions, TT, Policy, Training) running independently. Each workflow produces its own work papers and draft report. All outputs accumulate in the engagement folder. Maher assembles the final combined deliverable himself.

**Business rules:**
- `service_type` at engagement creation is the PRIMARY type (for labeling and default workflow) — not a constraint on which workflows can be run.
- Additional workflows can be launched against the same engagement from the Engagement detail page or Workspace.
- Each workflow run maps to a `case_id` in `ProjectState.cases[workflow_type]`. Multiple workflow types coexist under one engagement slug.
- Work papers, draft reports, and data analysis from all workflows accumulate in the engagement's A-F folder structure. No workflow is siloed.
- There is NO automatic combined deliverable — Maher reviews all workflow outputs and assembles the final client document manually (or triggers a future "Compile Report" feature).

**Impact on current schema:** `ProjectState.cases: dict[str, str]` already supports this. No schema change required. Navigation and UI are the affected surfaces.

---

### BA-IA-02 — Two-Arc Product Model
- Status: CONFIRMED — AK session 036

**Arc 1 — Proposal (pre-engagement)**
- Purpose: win the work before an engagement is created.
- Flow: Proposal deck (pitch) → Scoping conversation → Scope of Work letter (draft → client signs).
- Output: signed engagement letter stored in `firm_profile/proposals/{slug}/` or uploaded to the engagement's `A_Engagement_Management/` folder.
- Creating an engagement from Arc 1: once the letter is signed, Maher creates an engagement and links the signed letter as the engagement foundation. The engagement can also be created independently (if scoping happened outside the tool).
- Arc 1 is standalone — it can exist without an engagement (for prospects who don't convert).

**Arc 2 — Engagement (root for all work)**
- Purpose: execute the work, produce deliverables.
- Created either: (a) from Arc 1 signed letter, or (b) independently.
- Contains: Input Sessions, multiple workflow runs, work papers, reports.
- Engagement is the primary navigation home for Maher during active case work.

---

### BA-IA-03 — Navigation Model
- Status: CONFIRMED — AK session 036

**Business rules:**
- Workflow pages (Investigation, FRM, DD, Sanctions, TT, Policy, Training) are NOT primary sidebar navigation. They are sub-workflows launched from inside an Engagement or Workspace.
- Primary sidebar navigation contains: Engagements, Workspace, Proposals, Case Tracker, Activity Log, Team, Settings.
- Workflow pages remain as separate Streamlit pages but appear in a clearly labelled secondary section ("Workflows") at the bottom of the sidebar — accessible directly for power users, but the primary path is through Engagement.
- The `01b_Scope.py` page is repositioned as part of the Proposal arc (scoping step), not as a standalone page.
- The landing screen (app.py) is updated to reflect the two-arc model.

---

### BA-IA-04 — Project Name + Minimum Workstream Constraint
- Status: CONFIRMED — AK session 036

**AK decision:** Engagements are named Projects. Each project must have at least 1 workstream — 0 workstreams is not a valid state.

**Business rules:**
- Every engagement (ProjectState) has a `project_name` field set by Maher at creation (e.g. "ABC Corp Fraud Investigation Q1 2026"). This is distinct from `client_name` (who the client is) and `slug` (the filesystem identifier).
- At project creation, Maher must select at least 1 workstream. The creation form/intake does not allow submission with 0 workstreams selected.
- Workstreams can be added later (1 → N). The minimum constraint is at creation only — a project cannot be created empty.
- Workspace display: a project always has at least 1 workstream section visible. "No workflows run yet" is valid at the individual workstream level (workstream added but not yet executed), but never at the project level.
- `service_type` on ProjectState should be renamed/aliased to reflect that it represents the primary workstream, not the only one. For now it remains for backward compatibility but should be read as "primary_workstream_type".

**Impact on schema:** `ProjectState` needs a `project_name: str` field. Intake validation must enforce `len(initial_workstreams) >= 1`. This is a minor schema change — additive, no breaking change to existing state.json files (project_name defaults to slug if absent).

**Impact on UI:** Engagement creation form must include: (1) Project Name input, (2) workstream selector with at least 1 required. Workspace must never render an empty project.

---

### BA-IA-05 — AUP (Agreed-Upon Procedures) as Investigation Type + Standalone Mode
- Status: CONFIRMED — AK session 036

**AK decision:** Add AUP as investigation type 8. AUP can also be used outside a full investigation project as a scoped standalone delivery. Scope is strictly defined by the agreed procedures list — no scope creep, no unilateral expansion.

**Business rules:**
- Investigation intake: when Maher selects type = "Agreed-Upon Procedures", intake captures the procedures list explicitly — each numbered procedure is a discrete item. This list locks the scope. Nothing outside the list is reported.
- Agent output structure for AUP: one section per procedure → (a) procedure as stated, (b) what was done, (c) factual finding. No conclusions section. No "therefore" or implication language.
- Partner hard rule for AUP: enforce no-opinion constraint. If Junior or PM output contains recommendation language, conclusions, or implied fault, Partner must flag and strip before approval. AUP reports are factual observation reports only — AICPA/IAASB standards apply.
- AUP is NOT a substitute for an investigation. If Maher's described scope implies a conclusion is needed, the system should prompt: "This sounds like an investigation, not an AUP. Do you want to change the type?"
- Standalone AUP: can be run as a workstream type in any project, or as a standalone one-off outside a project (same pattern as Policy/SOP — Mode B entry point is acceptable for AUP).

**Impact on investigation_framework.md:** Add type 8 — Agreed-Upon Procedures. Add AUP-specific agent behavior notes (procedures-list intake, no-conclusions rule, section-per-procedure structure).
**Impact on schema:** `investigation_type` is already a string field — no schema change. AUP is a valid value.
**Impact on workflow:** Investigation intake branching — detect AUP type and switch to procedures-list intake flow. Junior system prompt gains AUP mode guardrail.

---

### BA-IA-06 — Custom / Other Investigation Type
- Status: CONFIRMED — AK session 036

**AK decision:** Add "Other / Custom" as investigation type 9. Real-world investigations frequently span categories or don't map to any predefined type. Forcing a category on a non-fitting investigation degrades output quality and forces Maher to lie about the nature of the work.

**Business rules:**
- When Maher selects type = "Other / Custom", intake captures a free-text description of the nature, subject, and objectives of the investigation. This description becomes the structural anchor — not a predefined template.
- No forced section headers for Custom type. Before drafting begins, the Junior proposes a report structure based on Maher's description. Maher confirms or adjusts. Only then does drafting proceed.
- All other investigation rules apply (evidence chain, three-agent pipeline, audit trail, authoritative citations).
- Partner review for Custom type: Partner must confirm that the proposed structure and conclusions are internally consistent with the stated objectives — there is no regulatory checklist to apply, so coherence and defensibility are the primary review criteria.
- Custom type does NOT bypass the privilege flag (BA-future) or conflict check (BA-future) — those apply to all investigation types.

**Impact on investigation_framework.md:** Add type 9 — Other / Custom. Add custom-type intake and structure-confirmation flow notes.
**Impact on schema:** No change — `investigation_type` is a free string field.
**Impact on workflow:** Investigation intake must present "Other / Custom" as a valid selection and branch into free-text description mode.

---

### BA-IA-07 — Hybrid Intake Architecture: Structured Fields + Remarks-Triggered Conversation
- Status: CONFIRMED — AK session 036

**AK decision:** Intake across all workflows must be redesigned as a hybrid model. Structured fields (dropdowns, checkboxes, radio buttons) handle scope-defining parameters. Each structured field or field group has an optional Remarks cell. If Remarks is non-empty, the model triggers a targeted conversation to resolve the nuance. If Remarks is empty, the field value is accepted as-is — no conversation, fast path through intake.

**The core principle:**
- Dropdown/selector = selects the lane (maps to agent behavior, report structure, scope parameters)
- Remarks cell = safety valve for edge cases, unusual circumstances, cross-category situations
- Remarks non-empty → targeted conversation fires for that field only
- Remarks empty → fast path, no conversation
- Result: clean cases are fast; complex cases get exactly the conversation they need, where they need it

**Intake flow (all workflows):**

```
STEP 1 — Structured fields
  Present dropdowns / checkboxes / radio buttons for all scope-defining parameters.
  Each field or field group has an optional "Remarks" text area (collapsed by default).

STEP 2 — Remarks scan
  After Maher completes all structured fields:
  For each field where Remarks is non-empty:
    → Model reads the Remarks and asks 1–2 targeted clarifying questions
    → Maher answers
    → Conversation output is merged into the structured field value / appended as refined context

STEP 3 — Confirmation
  Model presents intake summary: all structured values + any refined context from conversations.
  Maher confirms or corrects.
  Intake is locked. Agents receive the final structured + refined intake object.

STEP 4 — Agent handoff
  Agents always receive structured parameters (clean enum values) + narrative context (refined from conversations).
  Agents never receive raw free text that requires inference to determine scope.
```

**Fields requiring Remarks cells (minimum):**

| Workflow | Field | Why Remarks needed |
|---|---|---|
| All | Primary jurisdiction | "UAE + offshore holding structure" needs elaboration |
| Investigation | Investigation type | "Type 3 but also involves AML aspects" — cross-category |
| Investigation | Regulators implicated | "Possibly DFSA but matter is ongoing — uncertain" |
| Investigation | Evidence available | "Some documents withheld by client — access limited" |
| FRM | Modules in scope | "Module 4 but only for one subsidiary" |
| DD | DD depth | "Enhanced but time-constrained to 5 days" |
| DD | Subject jurisdictions | "Registered UAE but ops in 4 countries" |
| TT | Transaction types | "Vendor payments but specifically construction subcontractors" |
| AUP | Procedures list | Each procedure may need a Remarks cell for scope clarification |
| Custom | All fields | By definition, Custom type needs more elaboration everywhere |

**Conversation trigger rules:**
- Trigger if: Remarks cell for a field is non-empty AND length > 10 characters (ignore accidental single words)
- Do NOT trigger for: narrative/background fields (client description, allegation detail) — these are always free text, no trigger needed
- Maximum 2 follow-up questions per Remarks cell — do not let intake conversation expand into a full discussion
- If Maher's answer introduces a new scope item not in the structured fields, add it as a tagged custom scope note — do not re-open the structured fields

**What this replaces:**
- The current fully conversational guided_intake.py approach, which asks all questions as free text and relies on inference throughout
- Fully free-text investigation type / audience / jurisdiction fields across all workflows

**What this does NOT replace:**
- Narrative fields: client background, allegation description, specific circumstances — these remain free text with no structured equivalent
- FRM guided exercise conversation — the 4-question per-risk-area loop remains conversational (it is already structured around a fixed question set)
- AUP procedures list entry — this is inherently free text per procedure, but each procedure can have a Remarks cell

**Impact on `guided_intake.py`:**
Significant redesign required. The intake engine needs:
1. A structured-field renderer (dropdowns, checkboxes, radio buttons per workflow)
2. A remarks scanner that identifies non-empty Remarks after structured fields are complete
3. A targeted conversation runner that fires for each field with Remarks (max 2 questions)
4. A confirmation + lock step that produces the final `CaseIntake` object

**Impact on all intake Pydantic schemas:**
Each workflow's intake schema must separate structured fields (typed enums/lists) from narrative fields (strings). Currently many fields are plain strings where they should be enums with an optional remarks string alongside.

**Sprint assignment:** Sprint-IA-02 — intake redesign is a separate sprint from Sprint-IA-01 (navigation). The two are independent. Navigation ships first.

---

### BA-IA-08 — Partner Always Signs Off; Never Blocks
- Status: CONFIRMED — AK session 036

**AK decision:** The Partner agent must never block or stall the pipeline. It always signs off. Where a deliverable does not meet the full standard (no authoritative citations, weak evidence chain, incomplete regulatory mapping), the Partner approves and appends explicit section-level disclaimers. The consultant then decides whether to address the gap or proceed.

**Business rules:**
- Partner sign-off is unconditional on delivery. The pipeline must always complete.
- Where `authoritative_citations = 0` for a section or topic: Partner appends disclaimer — "Research limitations: no authoritative sources were identified for [topic]. Findings are based on [general sources / knowledge base only] and should be independently verified before reliance."
- Where evidence chain has gaps: Partner appends — "Evidence limitation: [specific gap]. This finding should be treated as indicative pending [additional evidence]."
- Where regulatory mapping is incomplete: Partner appends — "Regulatory note: authoritative regulatory guidance for [jurisdiction/topic] was not identified at the time of this review. Consult [relevant regulator] directly before reliance."
- The disclaimer is attached to the specific affected section — not a blanket footer on the whole report.
- The consultant reviews every disclaimer before the deliverable goes to a client. Maher decides what to address and what to pass on with the disclaimer intact.

**Rationale:** Blocking sign-off stalls the engagement. In real practice, a Partner would sign a report with a limitation note rather than refuse to sign until perfect sources are found. The disclaimer approach mirrors real-world professional practice: transparency over perfection.

**Impact on Partner agent prompts:** Remove any instruction to block or reject based on citation count. Replace with instruction to identify gaps, append section-level disclaimers, and approve.
**Impact on agent_base.py guardrail:** Remove hard block on `authoritative_citations = 0`. Replace with disclaimer-append trigger.
**Impact on CLAUDE.md:** Updated this session.

---

### BA-IA-09 — Policy/SOP Guided Co-Build Mode
- Status: CONFIRMED — AK Session 041

**AK decision:** Policy and SOP workflows must use a guided co-build model — not single-pass draft. Model and Maher build the document section by section, synchronously. Maher approves, edits, or regenerates each section before the next one drafts. This applies to ALL types: all 6 fixed policy types, all 5 fixed SOP types, and Custom.

**Co-build flow (all types):**
```
STEP 1 — Intake (HybridIntakeEngine, Sprint-IA-03-W5)
  Structured fields: doc type, jurisdiction, industry, description, gap_analysis
  Remarks on jurisdiction → conversation if non-empty

STEP 2 — AIC questions (existing render_intake_questions — unchanged)

STEP 3 — Structure proposal
  Model proposes section headings based on doc type + jurisdiction + description
  Maher: approve / reorder / add section / remove section
  Output: locked section list

STEP 4 — Per-section sync loop
  For each section in order:
    Model drafts the section (Haiku for body, Sonnet for review pass)
    Maher: Approve → advance | Edit inline → save and advance | Regenerate with instructions → re-draft
  No section N+1 drafts until section N is approved

STEP 5 — Final assembly
  All approved sections assembled into full document
  Standard done zone: DOCX + MD download
```

**Custom type — additional intake step (before STEP 3):**
```
STEP 2b — Custom scoping conversation
  Model asks 4–5 structured questions to define scope:
    1. What is the full name of this document?
    2. Who does it apply to (entity types, roles, geographies)?
    3. What regulations, standards, or frameworks should it reference?
    4. Does an existing version exist? (if yes → gap analysis mode)
    5. What is the primary risk or gap this document addresses?
  Answers recorded to D_Working_Papers/custom_doc_scoping.json
  These answers are injected into the structure proposal prompt (STEP 3)
```

**Business rules:**
- A section cannot be skipped — Maher must explicitly approve or regenerate before advancing. There is no "skip" button.
- If Maher edits a section inline, the edited text is the approved version — no re-draft unless Maher triggers it.
- Gap analysis mode: model reads any uploaded existing document, identifies gaps against the selected standard, and drafts only the gap sections. Existing sections shown as read-only in the review loop.
- Section count is not fixed — it is determined by the structure proposal and confirmed by Maher. Typical range: 6–14 sections.
- Model uses jurisdiction + regulatory framework from intake to cite applicable regulations inline. Standard: authoritative citations preferred; disclaimer appended if none found (per BA-IA-08).
- All section approvals recorded in audit_log.jsonl: event type "section_approved", section title, action (approved/edited/regenerated), timestamp.

**What this replaces:**
- Current single-pass `run_policy_sop_workflow` pipeline → replaced by multi-step co-build orchestrator
- The single "Run" button → replaced by structure proposal confirmation + per-section controls

**What this does NOT change:**
- HybridIntakeEngine intake wiring (Sprint-IA-03-W5) — co-build starts after intake completes
- AIC questions stage — unchanged
- Done zone (DOCX + MD download) — unchanged
- Audit trail — co-build adds events; existing hooks unchanged

**Sprint assignment:** Sprint-IA-04 — to be designed in a dedicated architect session before build starts.

---

## Session 044–045 BA — Sprint-QUAL-01: Pipeline Quality Fixes (2026-04-23)

### BA-QUAL-01 — PM Review Mode-Awareness
- Status: CONFIRMED — already implemented (Sprint-10L-Phase-A, SRL-01, commit 5b6b0d9)
- Root cause: PM requested revision in knowledge_only mode for missing citations. Fixed by `_build_mode_section()` in `agents/project_manager/prompts.py`.

**Business rules (confirmed):**
- In knowledge_only mode, PM MUST NOT request revision due to: absent citations, empty source_url fields, generic (non-client-specific) output.
- In knowledge_only mode, PM MAY request revision for: empty findings list, factually wrong regulatory reference, structural schema violation, logical inconsistency.
- In live mode: authoritative citations are required for all regulatory claims — original enforcement applies.
- These rules are implemented; no code change required. Verification only.

---

### BA-QUAL-02 — Junior Findings Floor
- Status: CONFIRMED — 2026-04-23
- Root cause: Junior returns empty findings list in knowledge_only mode when no client documents are available. PM then correctly requests revision (empty findings is a rejection criterion). This creates a revision loop.

**Business rules:**
- Junior MUST return at least 3 findings in every response. No exceptions.
- If no client documents are available AND research mode is knowledge_only: Junior derives findings from domain knowledge and regulatory baseline for the stated industry and jurisdiction. These are explicitly labelled as "baseline findings — not yet verified against client-specific evidence."
- An empty findings list is never acceptable output. If Junior cannot identify any findings, it must return 3 framework-level findings with risk_level="low" and a note that client-specific evidence is required.
- This applies to all workflows, not just investigation_report.
- Scope: `agents/junior_analyst/prompts.py` — `build_system_prompt()`.

---

### BA-QUAL-03 — Schema Retry Wiring
- Status: CONFIRMED — 2026-04-23
- Root cause: When Junior returns malformed JSON, `orchestrator.py` sets `context["schema_retry"] = True` and `context["schema_error"] = str(e)` for the next attempt. Junior's `agent.py` does not read these keys; `prompts.build_system_prompt()` has no schema_retry parameter. Junior repeats the same response without knowing it failed validation.

**Business rules:**
- On schema retry, Junior MUST receive an explicit prepended instruction: "SCHEMA RETRY — your previous response failed validation: {schema_error}. Fix this specific issue in your response before doing anything else."
- The retry instruction must prepend the full system prompt, not append — so the model sees the constraint first.
- `schema_retry` and `schema_error` are internal orchestrator context keys — never user-supplied. No injection risk.
- Scope: `agents/junior_analyst/agent.py` (read from context) + `agents/junior_analyst/prompts.py` (accept params, prepend instruction).

---

## Session 046 BA — Sprint-UX-ERR-01: Crash Reporter (2026-04-23)

### BA-ERR-01 — Structured Crash Reports
- Status: CONFIRMED — 2026-04-23
- Scope: When a Streamlit page crashes (bootstrap failure) or the pipeline raises an unhandled exception, the system must write a structured JSON crash report file and display a diagnostic-friendly error panel.

**User outcome:** Maher sees a clean error panel (not a raw Python traceback) with the path to a crash report file. He can drag that file into a Claude conversation to diagnose the issue without needing developer access to logs.

**Business rules:**
- Every page crash writes a structured crash report to `logs/crash_reports/crash_{YYYYMMDD_HHMMSS}.json` before displaying any error UI.
- Crash report contains: `timestamp_utc`, `page`, `exception_type`, `exception_message`, `traceback`, `session_context` (active_project slug, workflow_type, pipeline_status only — no case content), `recent_activity` (last 10 lines of activity.jsonl if present, else []).
- Crash report MUST NOT contain: case document content, file paths under `cases/`, PII from case files.
- Error panel shows: clean message ("Something went wrong loading this page."), crash report file path via `st.code()`, caption ("Share this file with Claude to diagnose the issue."), collapsed expander with exception type + message for technical users.
- Raw Python tracebacks must not appear in the primary error display — only inside the collapsed expander.
- Pipeline crashes (PipelineError) are also covered — `pipeline.py` wraps the pipeline run in try/except and writes crash report + shows styled panel.
- `logs/crash_reports/` is gitignored; `logs/crash_reports/.gitkeep` preserves the directory.
- Sprint assignment: Sprint-UX-ERR-01.

---
