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
