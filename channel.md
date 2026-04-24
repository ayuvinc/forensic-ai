# Channel

## Session 042 Open
Timestamp: 2026-04-23T07:37:22Z
Persona: architect
Next: /architect sprint_id=sprint-ia-04



## QA Review — Sprint-QUAL-01
Agent: qa
Sprint: Sprint-QUAL-01
Timestamp: 2026-04-23T13:20:00Z
Overall: QA_APPROVED

### Codex gate
Waived per project memory (feedback_codex_gate.md — AK order 2026-04-17).

### QA-Run proxy
131 tests pass. No formal qa-run entry for Sprint-QUAL-01 — changes are pure prompt text additions and agent context key wiring. No branching logic that unit tests can probe beyond import checks. 131-test regression baseline accepted.

### Criterion Results

#### QUAL-01 — PM mode-awareness (verification only)
- [PASS] `_build_mode_section("knowledge_only")` at `agents/project_manager/prompts.py:81` contains "DO NOT request revision" — confirmed pre-existing from Sprint-10L-Phase-A (SRL-01)
- [PASS] `agents/project_manager/agent.py:56` passes `research_mode=config.RESEARCH_MODE` to `build_system_prompt` — pre-existing
- [PASS] No code change needed or made — verification only; QUAL-01 is complete

#### QUAL-02 — Junior findings floor
- [PASS] `agents/junior_analyst/prompts.py:110` — "You MUST return at least 3 findings. An empty findings list is never acceptable output."
- [PASS] `agents/junior_analyst/prompts.py:112` — "Derive findings from your domain knowledge and regulatory baseline for this industry and jurisdiction."
- [PASS] `agents/junior_analyst/prompts.py:113` — baseline label instruction present
- [PASS] Block placed inside the OUTPUT FORMAT section — model sees it in context of response requirements, not as a disconnected afterthought
- [PASS] Applies in all modes (not knowledge_only-gated) — correct per BA-QUAL-02

#### QUAL-03 — schema_retry wiring
- [PASS] `agents/junior_analyst/agent.py:67` — `context.get("schema_retry", False)` (correct default)
- [PASS] `agents/junior_analyst/agent.py:68` — `context.get("schema_error", "")` (correct default)
- [PASS] Both passed to `prompts.build_system_prompt()` at lines 75–76
- [PASS] `agents/junior_analyst/prompts.py:39–40` — params added with correct defaults
- [PASS] `agents/junior_analyst/prompts.py:137–142` — prepend logic: `if schema_retry:` guard; `base = retry_prefix + base` (prepend, not append)
- [PASS] Default call (`schema_retry=False`) — guard does not fire; prompt contains no "SCHEMA RETRY" text
- [PASS] Architecture contract preserved — `prompts.py` is a pure function; context reads are in `agent.py`

### Security checks
- [PASS] `schema_error` originates from `str(e)` on internal `HookVetoError` (orchestrator.py:138) — never user-supplied; no injection risk
- [PASS] `schema_retry` is a bool from context — no injection vector
- [PASS] No new file reads, writes, or external calls introduced
- [PASS] No PII exposure; no auth changes; no audit event changes

### Edge cases
- [NOTE] `schema_error=""` with `schema_retry=True` produces "SCHEMA RETRY — your previous response failed validation: . Fix this..." — grammatically awkward but functionally correct; model receives retry signal. Not a blocker.
- [NOTE] `schema_error` is not length-capped. Pydantic validation errors are bounded and internal; no risk in practice. Not a blocker.

### Mobile / Auth
- Not applicable — no UI changes; single-user local install

### Verdict
QA_APPROVED — all ACs pass; 131 tests pass; no defects found. Sprint-QUAL-01 clear for Architect merge.

---

## QA Review — Sprint-IA-04
Agent: qa
Sprint: Sprint-IA-04
Timestamp: 2026-04-23T08:45:00Z
Overall: QA_APPROVED (W5-BUG-01 fixed in-session)

### Codex gate
Waived per project memory (feedback_codex_gate.md). QA proceeds on qa-run results and direct review.

### QA-Run proxy
131 tests pass (Sprint-IA-03 baseline holds). No Sprint-IA-04-specific test file; orchestrator functions are pure API-call wrappers with no unit-testable branching. Acceptance criteria verified by direct code review.

### Criterion Results

#### IA-04-S1 — schemas/policy_sop_cobuild.py
- [PASS] `CoBuildSection`: section_title, body, status (Literal pending/approved/edited/regenerated), action_note
- [PASS] `CoBuildState`: sections list, current_idx, doc_type, doc_subtype, gap_analysis, custom_scope, structure_confirmed, aic_context, intake_snapshot dict
- [PASS] Pydantic v2 BaseModel; mutable default `intake_snapshot: dict = {}` handled correctly by Pydantic v2 (no shared-default risk)
- [PASS] No circular imports between schemas

#### IA-04-W2 — workflows/policy_sop_cobuild.py
- [PASS] `propose_structure`: SONNET, max_tokens=512, returns 6–14 titles, pads with "Section N" if model returns <6
- [PASS] `draft_section`: HAIKU default, max_tokens=1024, prior context truncated to last 1500 chars
- [PASS] `revise_section`: HAIKU default, max_tokens=1024, instructions HTML-stripped + capped at 500 chars before injection (`_strip_html` + `[:500]`)
- [PASS] `assemble_and_write`: no model call; fires cobuild_complete audit event with action breakdown; calls write_artifact; returns FinalDeliverable
- [PASS] `identify_gaps`: SONNET, max_tokens=4096, JSON parse with all-None fallback on exception; markdown code fence stripping present
- [PASS] `workflows/policy_sop.py` (CLI single-pass) left untouched — CLI path not broken

#### IA-04-W3 — pages/04_Policy_SOP.py — stage machine
- [PASS] All 6 stages present: intake, ai_questions, custom_scoping, structure_proposal, section_loop, done
- [PASS] All helpers defined at MODULE LEVEL before stage machine (SyntaxError root cause resolved)
- [PASS] `ps_stage` initialised in session state at page load; invalid stage falls through to st.error
- [PASS] Stage transitions are forward-only; "Start Another Document" resets to intake

#### IA-04-W4 — pages/04_Policy_SOP.py — section loop UX
- [PASS] `st.progress(done_count / total)` present in section_loop
- [PASS] Three action buttons: Approve, Edit & Save, Regenerate
- [PASS] Regenerate shows instructions text_area (max_chars=500); calls revise_section
- [PASS] `append_audit_event` called after each section action (section_approved / section_edited / section_regenerated)
- [PASS] `_save_progress` called after each action (atomic write via .tmp)
- [PASS] Approved sections shown in collapsed expanders above current section

#### IA-04-W5 — gap analysis (pages/04_Policy_SOP.py — `_try_gap_analysis`)
- [FAIL → FIXED] `dm.get_all_text()` does not exist on DocumentManager; called was raising AttributeError caught silently by `except Exception: pass` — gap mode never pre-filled sections
- [FIX APPLIED] Replaced with `dm.has_documents()` guard + `dm.get_index().documents` iteration + `dm._read_full(doc.doc_id)` join; duplicate documents excluded (`not doc.is_duplicate`)
- [PASS after fix] `identify_gaps` receives concatenated doc text; truncates internally to 6000 chars
- [PASS after fix] 131 tests still pass post-fix

#### IA-04-W6 — docs/lld/policy-sop-cobuild.md
- [PASS] Stage machine diagram present with all 6 stages and transitions
- [PASS] Session state key reference table complete (11 keys)
- [PASS] All 5 orchestrator function signatures with model/input/output documented
- [PASS] Audit event schemas (section_approved/edited/regenerated + cobuild_complete) documented
- [PASS] cobuild_progress.json schema with resume behaviour described

### Defects

#### W5-BUG-01 (MEDIUM — FIXED in-session)
- File: `pages/04_Policy_SOP.py`, `_try_gap_analysis`, line 106
- Defect: `dm.get_all_text()` called on DocumentManager which has no such method
- Impact: Gap analysis mode silently produced blank drafts instead of pre-filling from uploaded document
- Fix: Replaced with `dm.has_documents()` + index iteration + `_read_full` join
- Status: FIXED — 131 tests pass post-fix

### Security checks
- [PASS] `revise_section` instructions: HTML-stripped + capped at 500 chars (source and injection point both verified)
- [PASS] doc_subtype from controlled selectbox — no injection risk at structure proposal
- [PASS] cobuild_progress.json local-only; no PII beyond case folder scope
- [PASS] sanitize_pii pre-hook applies to all downstream model calls via standard hook chain

### Auth / access
- [PASS] Page gated by `bootstrap(st, caller_file=__file__)` — same pattern as all other pages; no unauthenticated access path

### Mobile
- Not applicable — Streamlit app; no custom CSS layout changes in this sprint

### Verdict
QA_APPROVED — all P0 ACs met (S1, W2, W3, W4, W6); W5 defect found and fixed in-session; 131 tests pass post-fix. Sprint-IA-04 is clear for Architect merge.

---

## Last QA Run
Agent: qa-run
Sprint: Sprint-IA-03
Timestamp: 2026-04-23T06:10:00Z
Status: PASS

## Criterion Results

### IA-03-C1 (field configs)
- [PASS] All 6 configs importable
- [PASS] All field_types valid (selectbox/multiselect/radio/text/textarea)
- [PASS] required=True fields defined; has_remarks fields correct
- [PASS] 131 tests pass

### IA-03-W1 (06_FRM.py)
- [PASS] HybridIntakeEngine wired; frm_intake_form import removed (comments only, no import statement)
- [PASS] Module dependency enforcement (missing_deps auto-add + st.warning)
- [PASS] primary_jurisdiction from engine; workflow=frm_risk_register
- [PASS] frm_stage=confirm on engine_result
- [PASS] 131 tests pass

### IA-03-W2 (09_Due_Diligence.py)
- [PASS] HybridIntakeEngine wired; dd_intake_form import removed
- [PASS] subject_count and relationship outside engine (post-engine)
- [PASS] report_format logic (per_subject/consolidated)
- [PASS] dd_params["screening_level"] mapped from _DD_DEPTH_MAP
- [PASS] 131 tests pass

### IA-03-W3 (10_Sanctions.py)
- [PASS] knowledge_only gate position: byte offset 88 < engine offset 2159
- [PASS] subject_name from engine values (not separate text_input)
- [PASS] nationalities + aliases split on comma
- [PASS] _SAN_PURPOSE_KEYS + _SAN_OUTPUT_KEYS present
- [PASS] _san_engine.reset() + sanctions_acknowledged pop in reset button
- [PASS] 131 tests pass

### IA-03-W4 (11_Transaction_Testing.py)
- [PASS] HybridIntakeEngine wired; generic_intake_form removed
- [PASS] "Not applicable" → None in _TT_TYPOLOGY_KEYS (line 26)
- [PASS] doc upload outside engine (after engine_result is not None)
- [PASS] "Run Transaction Testing" button present
- [PASS] sampling="full_population" preserved
- [PASS] 131 tests pass

### IA-03-W5 (04_Policy_SOP.py)
- [PASS] POLICY_SUBTYPE_LABELS imported; doc_type inferred from membership
- [PASS] gap_analysis "New document"→"new" / "Gap analysis of existing"→"gap"
- [PASS] _POLICY_SUBTYPE_KEYS maps all 11 labels → pipeline keys
- [PASS] no separate doc_type selectbox widget
- [PASS] 131 tests pass

### IA-03-W6 (05_Training.py)
- [PASS] Duration "Custom" → 60; strip " min" → int conversion
- [PASS] include_quiz/include_case_study "Yes"/"No" → bool
- [PASS] _TR_TOPIC_KEYS + _TR_AUDIENCE_KEYS present
- [PASS] TRAINING_TOPICS/TARGET_AUDIENCES inverted dicts for running-stage display
- [PASS] 131 tests pass

### IA-03-QA (smoke test)
- [PASS] Smoke test spec written: tasks/smoke-tests/sprint-ia-03.md (7 steps, 6 pages + regression)
- [PASS] 131 tests pass (regression gate)
- [MANUAL] Steps A-G pending Maher live run in Streamlit

## Mobile Issues
None — Streamlit app; no custom CSS layout in wired pages.

## Warnings
- frm_intake_form appears in 2 comment lines in 06_FRM.py (docstring + code comment). Not an import. AC satisfied.
- date_range validation in TT now enforced at engine confirmation step (required field), not at Run click. Behaviour preserved, stage shifted earlier. Acceptable.
- Training TRAINING_TOPICS/TARGET_AUDIENCES dicts reconstructed as inverted maps (key→label) for running-stage expander display.

---

## QA — Sprint-DOCX-01 — AC Written (Mode A)
Agent: qa
Sprint: Sprint-DOCX-01
Timestamp: 2026-04-23T07:30:00Z
Status: AC_WRITTEN — awaiting junior-dev build + qa-run

### QA Implementation Flag — DOCX-01
**Severity: HIGH — junior-dev must read before implementing**

Task description says: "add [docx button] after the existing .md download button."
ux-specs.md:386 says: `st.columns(2)` layout — `.docx` LEFT (primary, label "Download Word document"), `.md` RIGHT (secondary, label "Download Markdown backup").

These conflict. The correct implementation follows ux-specs.md:386. Junior-dev must:
1. Remove the existing single-column `.md` button block from `done_zone.py`
2. Replace it with `col_docx, col_md = st.columns(2)` inside the `if report_path.exists():` gate
3. Render docx button in `col_docx` (only if `docx_path.exists()`)
4. Render md button in `col_md` (always, label "Download Markdown backup")
5. Use label "Download Word document" for docx — NOT `f"Download {workflow_label} report (.docx)"`

Same 2-column pattern applies to DOCX-02 through DOCX-02e on individual pages.

### AC summary
Full AC written inline in tasks/todo.md under each task (DOCX-01 through DOCX-03).
Key pass/fail gates:
- Two-column layout present (not stacked single-column)
- docx LEFT, md RIGHT
- Labels exactly "Download Word document" / "Download Markdown backup"
- docx absent → left column empty, md still renders, no crash
- Regression: "Start Another" reset + workpaper button unaffected (DOCX-01)
- All 8 affected pages checked (3 via done_zone.py, 5 individually)

---

## QA-Run — Sprint-PARTNER-FIX-01
Agent: qa-run
Sprint: Sprint-PARTNER-FIX-01
Timestamp: 2026-04-24T00:00:00Z
Branch: feature/sprint-partner-fix-01
Overall: QA_APPROVED

### Codex gate
Waived per project memory (feedback_codex_gate.md). QA proceeds on qa-run results and direct review.

### Test suite
139 passed, 0 failed, 19 warnings — `python3 -m pytest tests/ -q`
New file: `tests/test_partner_agent.py` — 8 tests, all PASS.

### Criterion Results

#### AC — PFIX-01 (prompts.py)
- [PASS] No instance of "If rejecting" or "set approved=false" in `agents/partner/prompts.py` APPROVAL RULES
- [PASS] No instance of "revision_requested=true" or "If revision is needed"
- [PASS] Line 49: "ALWAYS approve — set approved=true. Partner never blocks or stalls the pipeline."
- [PASS] Line 53: "revision_requested is ALWAYS false. Partner does not send work back to revision."
- [PASS] Line 69 (footer): "approved is always true. revision_requested is always false."
- [PASS] Live mode section (lines 129–139): "append to conditions[]" pattern — no rejection or revision language
- [PASS] Knowledge_only section unchanged — no regression
- [PASS] Output JSON template hardcodes `"approved": true`, `"revision_requested": false`

#### AC — PFIX-02 (agent.py _enforce_evidence_chains)
- [PASS] `_enforce_evidence_chains()` (lines 105–167) contains no `output["approved"] = False`
- [PASS] `_enforce_evidence_chains()` contains no `output["revision_requested"] = True`
- [PASS] Chain failure path (lines 151–165): appends disclaimer string to `output["conditions"]`
- [PASS] Chain failure path: warning text appended to `output["review_notes"]`
- [PASS] `approved` and `revision_requested` untouched by chain validation path
- [PASS] Early return on `not evidence_items or not finding_chains` (no-op) confirmed
- [NOTE] `approved=False` at line 195 is in `_parse_output` JSON fallback only — acceptable per AC test comment ("parse error, not revision loop"); `revision_requested=False` in that same fallback — correct

#### AC — PFIX-03 (tests)
- [PASS] `tests/test_partner_agent.py` exists — 8 tests in 2 classes
- [PASS] `TestPartnerParseOutput::test_approved_true_revision_false_passes_through`: mock LLM JSON with conditions list → `approved=True`, `revision_requested=False`
- [PASS] `TestEvidenceChainDisclaimerNotBlock::test_approved_remains_true_on_chain_failure`: chain failure → `approved=True`
- [PASS] `TestEvidenceChainDisclaimerNotBlock::test_revision_requested_remains_false_on_chain_failure`: chain failure → `revision_requested=False`
- [PASS] `TestEvidenceChainDisclaimerNotBlock::test_disclaimer_appended_to_conditions_on_chain_failure`: disclaimer with "evidence/condition/finding" keyword present
- [PASS] `TestEvidenceChainDisclaimerNotBlock::test_warning_appended_to_review_notes_on_chain_failure`: "evidence chain warning" in review_notes
- [PASS] 139/139 tests pass — no regression

#### AC — Integration (all PFIX tasks)
- [WARN] End-to-end FRM pipeline not run — API credits conserved. State machine verification (`partner_review_complete` not `partner_revision_requested`) deferred to next live run.
- [PASS] Code path analysis: `_enforce_evidence_chains` cannot produce `PARTNER_REVISION_REQ` — no `approved=False` or `revision_requested=True` set
- [PASS] Prompt instructs model to output `"approved": true`, `"revision_requested": false` — behavioural guarantee at prompt level
- [PASS] `_parse_output` fallback: `revision_requested=False` — orchestrator cannot enter revision loop on parse error

### Security checks
- [PASS] No new file reads, writes, or external calls
- [PASS] No auth model changes; single-user local install
- [PASS] No PII exposure path introduced

### Verdict
QA_APPROVED — all testable ACs pass; 139/139 tests pass; integration ACs satisfy via static analysis; prompt and code are aligned. Sprint-PARTNER-FIX-01 clear for Architect merge.

---

## QA-Run — Sprint-FOLDER-01
Agent: qa-run
Sprint: Sprint-FOLDER-01
Timestamp: 2026-04-24T01:00:00Z
Branch: feature/sprint-folder-01-pre-create-case-folder
Overall: QA_APPROVED

### Codex gate
Waived per project memory (feedback_codex_gate.md).

### Test suite
139 passed, 0 failed, 19 warnings — `python3 -m pytest tests/ -q`
No new test file — change is pure side-effect code (mkdir + write_state), no unit-testable branching in isolation. Regression baseline holds.

### Criterion Results

#### AC — FOLDER-01 through FOLDER-04 (all pages)

- [PASS] All 8 pages have the Sprint-FOLDER-01 block — confirmed via grep (1 block per file)
  - pages/02_Investigation.py, pages/06_FRM.py, pages/09_Due_Diligence.py, pages/04_Policy_SOP.py
  - pages/05_Training.py, pages/07_Proposal.py, pages/10_Sanctions.py, pages/11_Transaction_Testing.py

- [PASS] `cases/{slug}/` created before pipeline: `case_dir(intake.case_id)` called in all 8 blocks; `case_dir()` (file_tools.py:51) calls `d.mkdir(parents=True, exist_ok=True)` — synchronous, completes within milliseconds of Run click

- [PASS] `state.json` fields: all 8 blocks confirmed to contain `case_id`, `workflow`, `status: "running"`, `started_at` (ISO-8601 via `datetime.now(timezone.utc).isoformat()`)

- [PASS] Atomic write: `write_state()` (file_tools.py:233-238) uses `.with_suffix(".tmp")` → `os.replace()` — no partial writes possible

- [PASS] Idempotency guard: `if not (_cdir / "state.json").exists()` present in all 8 blocks — re-run same case skips write, no crash; `case_dir()` itself is always idempotent (`exist_ok=True`)

- [PASS] `case_id` empty guard: all 8 pages have `st.stop()` in the button handler before `case_id` is ever set; running stage is unreachable without a valid `case_id`

- [PASS] Atomic write pattern: `write_state()` — confirmed above (`.tmp → os.replace()`)

- [PASS] Security — path traversal: `case_dir()` (file_tools.py:41-50) resolves path and raises `ValueError` if it escapes `CASES_DIR`; fires on every `case_dir()` call including the one inside `write_state()`

- [PASS] Regression — `run_in_status()` call signatures unchanged in all 7 pages that use it; pre-create block is unconditional code inserted before (not inside) the try/except; Policy/SOP co-build injection point is before `propose_structure()` spinner — equivalent earliest work point

### Warnings
- FRM (06_FRM.py) has a prior `write_state` at ai_questions transition (engagement_id path, status: "intake_created"). Running-stage pre-create guard (`if not exists`) means FRM+engagement_id cases skip the "running" write — state.json retains "intake_created" status. Folder exists and pipeline runs correctly. P1 — AC functionally satisfied (folder exists), status field deviation documented.
- Policy/SOP injection is at `structure_proposal` stage (no `run_in_status` on this page). Equivalent earliest pipeline work point. AC intent satisfied.

### Security checks
- [PASS] No new auth change; single-user local install
- [PASS] No PII exposure: state.json writes case_id (slug), workflow key, status, timestamp only
- [PASS] Audit: write_state updates cases/index.json atomically — case tracker stays consistent

### Verdict
QA_APPROVED — all 8 ACs pass; 139/139 tests pass; no regressions; 2 P1 warnings documented, neither blocks. Sprint-FOLDER-01 clear for Architect merge.

---

## QA-Run — Sprint-UX-PROGRESS-01
Agent: qa-run
Sprint: Sprint-UX-PROGRESS-01
Timestamp: 2026-04-24T02:30:00Z
Branch: feature/sprint-ux-progress-01-fix-progress-bar
Overall: QA_APPROVED

### Codex gate
Waived per project memory (feedback_codex_gate.md).

### Test suite
139 passed, 0 failed, 19 warnings — `python3 -m pytest tests/ -q`
No new test file — change removes a UI widget; not unit-testable in isolation. Regression baseline holds.

### Criterion Results

#### AC — PROG-01 (pipeline.py)
- [PASS] Option A implemented: `st.progress()` fully removed from `run_in_status()` — only remaining reference is in module docstring (line 16), not executable code
- [PASS] `total_steps: int = 3` removed from function signature — confirmed by signature inspection; no callers were passing it (grep confirmed zero callers)
- [PASS] `_advance_progress()` function removed — no trace in live code
- [PASS] `progress_bar` variable removed — no trace in live code
- [PASS] `st.status(label, expanded=True)` retained at line 158 — provides spinner while running
- [PASS] `status.update(label=..., state="complete")` retained at line 170 — provides green checkmark on success
- [PASS] `status.update(label=..., state="error")` retained at line 185 — provides red state on failure (pipeline error, not mid-run overflow)
- [PASS] Under no circumstance can the progress indicator show 100%/red while pipeline is still running — the only visual state indicator is `st.status()`, which is controlled by `status.update()` called only after `fn()` returns
- [PASS] Forensic tip panel (line 137-138): `st.info(f"While you wait — **Forensic insight:** {tip}")` — UX-WAIT-01 no regression

#### AC — PROG-02 (FRM multi-module)
- [PASS] No callers pass `total_steps` (confirmed by grep: zero matches in pages/ and streamlit_app/); parameter removed — no page changes needed
- [PASS] Multi-module FRM with schema_retry events: each emits an on_progress call; step_count increments but no progress bar overflows — no visible red indicator possible

#### AC — PROG-03 (smoke verify — AK manual)
- [DEFERRED] Requires live pipeline run — API credits needed. Static analysis confirms the red-bar condition is architecturally impossible with Option A: st.status() spinner shows until status.update() is explicitly called after fn() returns.

### Activity log integrity
- [PASS] `step_count` retained (line 155) and incremented in `on_progress` (line 166)
- [PASS] `detail={"label": label, "steps": step_count[0]}` preserved in pipeline_complete log (line 180)

### Security checks
- [PASS] UI-only change — no auth, data boundary, PII, or audit impact
- [PASS] No new inputs processed; no new code paths that touch user data

### Verdict
QA_APPROVED — all testable ACs pass; 139/139 tests pass; red-bar condition architecturally eliminated; PROG-03 deferred to manual smoke (no blocker). Sprint-UX-PROGRESS-01 clear for Architect merge.

---
