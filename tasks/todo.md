# TODO

## SESSION STATE
Status:         CLOSED
Active task:    none
Active persona: architect
Blocking issue: none
Last updated:   2026-04-23T13:10:32Z — state transition by MCP server
---

## DEPENDENCY GRAPH (read before building)

```
P0-01 ──────────────────────────────────────────────────┐
P1-01 (config) ─────────────────────────────────────────┤
P1-02 (schemas/case) ──────────── P1-05 ────────────────┤
P1-02b (schemas/handoff) ──────────────────────────────┤
P1-03 (schemas/artifacts) ← P1-04                       │
P1-03b (schemas/presentation) ─────────────────────────┤
P1-04 (schemas/research) ──────── P1-03, P1-11..14 ────┤
P1-05 (state_machine) ← P1-02 ──── P1-09, P1-10 ───────┤
P1-06 (hook_engine) ─────────────── P1-07, P1-08 ───────┤
P1-07 (hooks) ← P1-06, P1-02..04 ─ P1-09 ──────────────┤
P1-08 (tool_registry) ← P1-06 ──── P1-09, P1-11..14 ───┤
P1-09 (agent_base) ← P1-01,05..08 ─ P2-01, P2-02..04 ──┤
P1-10 (orchestrator) ← P1-09,05 ── P2-02..04 ───────────┤
P1-11..14 (research tools) ← P1-04, P1-08 ─ P2-02 ─────┤
P1-15 (file_tools) ← P1-01 ─────── P1-07 ──────────────┘
P2-01 (plugins) ← P1-09 ─────────── P2-02..05
P2-02 (junior) ← P2-01,P1-10..14 ── P2-05
P2-03 (pm) ← P2-01, P1-10 ────────── P2-05
P2-04 (partner) ← P2-01, P1-10 ───── P2-05
P2-05 (run.py) ← P2-02..04 ──────── P3-01, P4-01..09
P3-01 (frm) ← P2-05 ──────────────── FRM-R-01..08
P4-01..09 (workflows) ← P2-05
Sprint-10A schemas ─── Sprint-10E,10F,10C
Sprint-10B knowledge ── Sprint-10E,10F
Sprint-10C (library) ← Sprint-10A
Sprint-10D (FRM redesign) ← ARCH-S-01 + P7-GATE baseline
Sprint-10E (workflows) ← Sprint-10A + Sprint-10B
Sprint-10F (scoping) ← KF-NEW + ARCH-S-04
Sprint-10I (Tavily resilience) ← config.py — blocks P7-GATE
Sprint-10G (chaining) ← Phase 8 (FE-01..06)
Phase 8 (Streamlit) ← FE-01..06
ARCH-INS-01 (severity events) ← P8-03-SHARED ──── P8-08-PAGES
ARCH-INS-02 (case index) ← write_state() ──────── P8-09-TRACKER
ARCH-INS-03 (circuit breaker) ← Phase 8 ─────── pre-production
Phase 9 (chaining UI) ← Sprint-10G
Phase 7 (blank framework) ← P7-GATE
Sprint-TPL-01 (TemplateManager) ─── TPL-02, TPL-03, TPL-04, TPL-05
Sprint-EMB-01 (EmbeddingEngine) ──── EMB-02, EMB-03
Sprint-EMB-02 (ingestion wire) ────── CONV-01
Sprint-P9-01a/b/c (schemas) ──────── P9-UI-01, P9-02..09
Sprint-WORK-01 (WorkpaperGenerator) ─ WORK-02, WORK-03
Sprint-CONV-01 (EvidenceChat) ─────── CONV-02
Sprint-CONV-02 ← EMB-02 + CONV-01
Sprint-UX-FIXES ─ parallel (no schema deps)
Sprint-ACT-00 (logs/ dir) ─────────── ACT-01
Sprint-ACT-01 (ActivityLogger) ─────── ACT-02, ACT-03
Sprint-ACT-02 ← ACT-01 + SETUP-03 + schemas stable (Phase C)
Sprint-KL-00 (manifest) ─────────────── KL-01
Sprint-KL-01 ← EMB-01 + KL-00 ────────── KL-02
```

Completed tasks archived in: releases/completed-tasks.md
Sprint-01, Sprint-02, QR-01..16, Sprint-03, Sprint-04 AKR, Sprint-06, Sprint-09, Sprint-10A..B, Sprint-10E/H/F/I/J/K, Sprint-10L-Phase-A, BUG-10, Phase 8 automated tasks (P8-01/03/04/07/08/09/10/11, ARCH-INS-01/02), Phase H (RD-02..06, P9-07A/B, P9-08), Sprint-IA-01..03 — all DONE, see releases/completed-tasks.md.

---

## PENDING TASKS

FIX-01, FIX-02, FIX-03, CR-01 — ARCHIVED to releases/completed-tasks.md (Sprint-IA-01, merged Session 038, QA_APPROVED 17/17 smoke steps). Removed from PENDING.

---

Sprint-IA-02 — ARCHIVED to releases/completed-tasks.md (QA_APPROVED Session 039, merged main). Removed from PENDING.

---

Sprint-IA-03 — ARCHIVED to releases/completed-tasks.md (QA_APPROVED Session 041, merged main). Removed from PENDING.

Sprint-IA-04 — ARCHIVED to releases/completed-tasks.md (QA_APPROVED Session 044, merged main). Removed from PENDING.

Sprint-QUAL-01 — ARCHIVED to releases/completed-tasks.md (QA_APPROVED Session 045, merged main). Removed from PENDING.

---

### Sprint-KB-01 — Firm Knowledge Base Embedding [READY_FOR_REVIEW]

**Status:** READY_FOR_REVIEW — Session 043. All tasks KB-01..04 complete. 131 tests pass.
**Context:** 14 knowledge/ markdown files (~10k+ lines) currently loaded as raw full text into every agent system prompt. No retrieval — agents get everything whether relevant or not. FirmKnowledgeEngine indexes all knowledge/ files once into a firm-level persistent ChromaDB at `firm_profile/knowledge/.chromadb`. Agents then retrieve only relevant sections per query.
**Separate from per-case EmbeddingEngine** (Sprint-EMB) which handles uploaded case documents.

**Knowledge-sharing design (AK decision 2026-04-23, revised):** Three deterministic fetches in `core/orchestrator.py` before any agent runs — no agent ever calls FirmKnowledgeEngine directly.

```
Fetch 1 — workflow-general (pre-pipeline):
  FirmKnowledgeEngine().search(workflow_generic_query, workflow_type=workflow_id)
  → context["firm_knowledge_context"]   (cap: 3000 chars)
  → passes to: Junior, PM, Partner

Fetch 2 — intake-derived supplemental (post-intake, pre-Junior):
  Extract jurisdiction / operating_jurisdictions / industry / regulators_implicated
  from resolved CaseIntake object (Maher's input, including remarks resolutions).
  Construct targeted query, e.g. "DFSA enforcement investigation UAE" from those fields.
  Skip if all intake fields are defaults (no supplemental needed).
  FirmKnowledgeEngine().search(intake_derived_query, workflow_type=workflow_id)
  → appended to context["firm_knowledge_context"]   (combined cap: 3000 chars)

Fetch 3 — review standards (pre-PM/Partner):
  FirmKnowledgeEngine().search("review standards quality criteria " + workflow_type)
  → context["firm_review_knowledge_context"]   (cap: 1500 chars)
  → passes to: PM and Partner only (not Junior)
```

PM prompt instruction: "Firm knowledge and review standards are provided above. Use them as-is — do not re-query. Identify gaps in Junior's coverage of these standards."
No `FirmKnowledgeEngine` calls inside any agent prompt builder.

- [x] KB-01 Create `tools/firm_knowledge_engine.py` — `FirmKnowledgeEngine` class. `__init__`: loads from `firm_profile/knowledge/.chromadb` (PersistentClient). `index_all()`: walks `knowledge/` recursively, chunks each .md file (chunk size 500 chars, 50 overlap), embeds with sentence-transformers, upserts to ChromaDB with metadata `{workflow_type, filename, chunk_idx}`. `search(query, workflow_type=None, top_k=5)`: retrieves relevant chunks, optionally filtered by workflow_type. `needs_reindex()`: returns True if any .md file mtime > last index timestamp. Auto-fallback: if unavailable, `search()` returns `""`.
- [x] KB-02 Wire into app.py bootstrap — call `FirmKnowledgeEngine().index_all()` on startup if `needs_reindex()`. Show `st.toast("Knowledge base indexed.")` on completion. Non-blocking — run in background thread.
- [x] KB-03 Wire all three fetches into orchestrator — in `core/orchestrator.py`: implement Fetch 1 (workflow-general), Fetch 2 (intake-derived, using `CaseIntake` fields: `primary_jurisdiction`, `operating_jurisdictions`, `industry`, any `regulators_implicated` field — skip fetch if all are defaults), Fetch 3 (review standards). Store results as `context["firm_knowledge_context"]` and `context["firm_review_knowledge_context"]`. In agent prompts: Junior reads `firm_knowledge_context` only; PM and Partner read both. No direct `open()` calls to `knowledge/` files in any agent prompt file.
- [x] KB-04 CLI path — grep confirmed zero raw `open(knowledge_file)` patterns in workflow files. No changes needed.

#### AC — Sprint-KB-01

- [x] KB-01: `FirmKnowledgeEngine` class exists in `tools/firm_knowledge_engine.py` with public methods `index_all()`, `search(query, workflow_type=None, top_k=5)`, and `needs_reindex()` — code inspection
- [x] KB-01: When `sentence-transformers` or `chromadb` is not importable, `FirmKnowledgeEngine().search("any query")` returns `""` without raising an `ImportError` — code inspection of fallback path
- [x] KB-01: `needs_reindex()` returns `True` when a `knowledge/` .md file has mtime newer than last index timestamp, or when no index exists — code inspection
- [x] KB-01: `search("AML risk", workflow_type="frm_risk_register", top_k=5)` returns a non-empty string when `knowledge/frm/frm_framework.md` is indexed — smoke-tested in Session 043, returned 1559 chars
- [x] KB-01: `firm_profile/knowledge/.chromadb/` directory is created by `index_all()` when it does not yet exist — confirmed in smoke test
- [x] KB-02: `app.py` bootstrap calls `FirmKnowledgeEngine().index_all()` in a background thread when `needs_reindex()` is True — code inspection
- [x] KB-02: `st.toast("Knowledge base indexed.")` is called on thread completion — code inspection
- [x] KB-02: If `FirmKnowledgeEngine` is unavailable (fallback), no exception is raised during bootstrap — code inspection of try/except guard
- [x] KB-03: `core/orchestrator.py` performs Fetch 1 (workflow-general) before Junior runs and stores result as `context["firm_knowledge_context"]` — code inspection
- [x] KB-03: `core/orchestrator.py` performs Fetch 2 (intake-derived) after intake resolves and appends to `context["firm_knowledge_context"]`; Fetch 2 is skipped when jurisdiction/industry are all defaults — smoke-tested: `_has_specific_intake_context(default_intake)` returns False
- [x] KB-03: `core/orchestrator.py` performs Fetch 3 (review-standards) and stores result as `context["firm_review_knowledge_context"]` — smoke-tested: key present at 1500 chars
- [x] KB-03: Junior agent `build_system_prompt()` injects `firm_knowledge_context` but NOT `firm_review_knowledge_context` — code inspection
- [x] KB-03: PM and Partner `build_system_prompt()` inject both `firm_knowledge_context` and `firm_review_knowledge_context` — code inspection
- [x] KB-03: No `FirmKnowledgeEngine` import or call in `agents/junior_analyst/prompts.py`, `agents/project_manager/prompts.py`, or `agents/partner/prompts.py` — grep confirms
- [x] KB-03: Combined `firm_knowledge_context` (Fetch 1 + Fetch 2) is ≤ 3000 chars; `firm_review_knowledge_context` is ≤ 1500 chars — smoke-tested: 3000 / 1500 exactly
- [x] KB-04: `workflows/investigation_report.py` has no raw `open(` calls referencing `knowledge/` files — grep check
- [x] KB-04: `workflows/frm_risk_register.py` same — grep check
- [ ] KB-04 (regression): `python run.py` Option 6 (FRM, `RESEARCH_MODE=knowledge_only`) completes without crash and writes `final_report.en.md` — manual smoke check by AK before QA_APPROVED

---

### ARCH-SIM-01/02 — Simulation Directory Housekeeping [ATTACH TO NEXT SPRINT]

**Status:** READY — no design decisions needed. Attach as housekeeping tasks to Sprint-UX-ERR-01.
**Context:** Architect evaluation (Session 045) confirmed simulation/ is stale (calibrated to pre-Sprint-10L; doesn't model schema_retry, findings_floor, HybridIntakeEngine, FirmKnowledgeEngine). Harness family archived; empirical tests rescued to tests/.

- [ ] **[ARCH-SIM-01]** Fix empirical test imports and migrate to `tests/` — In `simulation/test_empirical_hooks.py`, `test_empirical_orchestrator.py`, `test_empirical_schemas.py`, `test_empirical_state_machine.py`: fix import paths so all 4 files are collected by `python3 -m pytest tests/ -q` without errors. Move files to `tests/`. Label with `# integration test — requires real codebase` comment at top. Verify: `python3 -m pytest tests/ -q` collects and runs all 4 + existing 131. ← no deps | P0 | Owner: junior-dev

- [ ] **[ARCH-SIM-02]** Archive harness family — Create `archive/simulation/`. Move these 10 files from `simulation/` to `archive/simulation/`: `harness.py`, `harness_future.py`, `game_theory.py`, `conflict_detector.py`, `conflict_detector_future.py`, `run_all.py`, `run_empirical.py`, `run_future.py`, `input_fuzzer.py`, `empirical_fixtures.py`. Write `archive/simulation/README.md`: "Monte Carlo failure harness — calibrated to pre-Sprint-10L (Sprint-IA-01 era). Archived Session 045. See git log for methodology. Do not maintain." Delete `simulation/` directory from active tree (it will be empty after moves). Verify: no import in `tests/` or any active module references `simulation/`. ← ARCH-SIM-01 | P0 | Owner: junior-dev

#### AC — ARCH-SIM-01/02
- [ ] SIM-01: `python3 -m pytest tests/ -q` collects all 4 empirical test files with no import errors
- [ ] SIM-01: Empirical tests either pass or fail with meaningful assertion errors (not ImportError/ModuleNotFoundError)
- [ ] SIM-02: `archive/simulation/` exists with 10 harness files + README.md
- [ ] SIM-02: `simulation/` directory no longer exists at repo root
- [ ] SIM-02: `grep -r "from simulation" tests/ agents/ core/ workflows/` returns nothing
- [ ] Regression: existing 131 tests still pass after moves

---

### Sprint-UX-ERR-01 — Crash Reporter + Structured Error Logs [UNBLOCKED]

**Status:** READY — no design decisions needed; extends existing FE-TRIAGE-04/05 error boundaries.
**Context:** Unhandled exceptions show raw Python tracebacks in Streamlit browser. No structured output, nothing shareable. When something breaks, Maher needs a single file he can drag into a Claude conversation for diagnosis — not a raw traceback.
**Security model:** crash report captures exception + sanitised session context only. No case content, no document text, no file paths from `cases/`. Session context is slug/type/status only.

- [ ] ERR-00 Create `logs/crash_reports/` directory — add `logs/crash_reports/.gitkeep`; add `logs/crash_reports/*.json` to `.gitignore`.
- [ ] ERR-01 Create `streamlit_app/shared/crash_reporter.py` — `write_crash_report(page_name: str, exception: Exception) -> str`. Captures and writes to `logs/crash_reports/crash_{YYYYMMDD_HHMMSS}.json`:
  - `timestamp_utc`: ISO-8601
  - `page`: basename of `page_name`
  - `exception_type`: `type(exception).__name__`
  - `exception_message`: `str(exception)`
  - `traceback`: `traceback.format_exc()`
  - `session_context`: read from `st.session_state` — extract only: `active_project` (slug string), `active_workflow_type`, current pipeline status from `cases/{slug}/state.json` if readable. If any key is missing or unreadable: `null`. Never read case content.
  - `recent_activity`: last 10 lines of `logs/activity.jsonl` if file exists, else `[]`
  - Returns the written file path as a string.
- [ ] ERR-02 Update error boundary on all pages — in the `except` block of every `bootstrap(st, caller_file=__file__)` try/except (FE-TRIAGE-05 pattern): call `write_crash_report(__file__, e)` before `st.error()`. Replace raw `st.error(f"Page failed to load: {e}")` with:
  - `st.error("Something went wrong loading this page.")` (no raw exception in primary message)
  - `st.code(crash_path, language=None)` — shows the file path, easy to copy
  - `st.caption("Share this file with Claude to diagnose the issue.")` 
  - `st.expander("Show error details")` → `st.text(exception_type + ": " + exception_message)` — tech details available but not in Maher's face
- [ ] ERR-03 Pipeline error boundary — in `streamlit_app/shared/pipeline.py`, wrap the pipeline run call in try/except. On exception: call `write_crash_report("pipeline:" + workflow_type, e)` and show the same styled error panel as ERR-02. Pipeline stage sets `inv_stage = "error"` as already done in BUG-042-07; crash report is in addition.

#### AC — Sprint-UX-ERR-01

- [ ] ERR-01: `write_crash_report()` produces valid JSON with all required keys: `timestamp_utc`, `page`, `exception_type`, `exception_message`, `traceback`, `session_context`, `recent_activity` — code inspection
- [ ] ERR-01: `session_context` contains only `active_project`, `active_workflow_type`, `pipeline_status` — no case content, no `cases/` file paths — code inspection
- [ ] ERR-01: if `logs/activity.jsonl` is absent, `recent_activity` is `[]` not an error — code inspection
- [ ] ERR-01: file is written to `logs/crash_reports/` — file existence check after simulated exception
- [ ] ERR-02: error boundary shows file path via `st.code()`, not a raw traceback — visual inspection
- [ ] ERR-02: `st.expander("Show error details")` is present but collapsed by default — visual inspection
- [ ] ERR-03: pipeline exception writes crash report and shows the styled error panel — code inspection of pipeline.py except block

---

### Sprint-UX-DS-01 — Design System Portability Shell [DEFERRED — white-label phase]

**Status:** DEFERRED. GoodWork colors and design stay as-is for now. Reusable design_system/ directory is a white-label deliverable — build when white-label packaging begins (likely alongside Phase 7). No tasks written yet.

---

### Sprint-UX-WIRE-01 — Interaction Sophistication [UNBLOCKED — after ERR-01]

**Status:** READY. AK decision 2026-04-23: sophistication problem is interaction wiring, not visual design. Colors/fonts stay GoodWork as-is. The root cause of "feels like it'll fall apart" is: (1) every button causes a full page rerun, (2) no inline feedback on saves, (3) forms dump all fields at once, (4) session state bleeds between pages, (5) stage transitions are abrupt jumps.
**Streamlit patterns used:** `@st.fragment` (partial reruns), `st.toast()` (non-blocking feedback), `st.dialog()` (modal confirms), `st.popover()` (contextual metadata), `st.progress()` step indicators, session state namespacing.
**No new libraries needed.** All patterns are native Streamlit ≥ 1.33.

- [ ] WIRE-01 `@st.fragment` on all Workspace save actions — in `pages/16_Workspace.py`: wrap each save handler (Save Note, Add Key Fact, Add Red Flag, Add Subject/Target/Population, file upload confirm) in `@st.fragment`. Each fragment reruns only its own section on submit; the rest of the page does not reload. After save: call `st.toast("Saved ✓")` inside the fragment. Pattern for every fragment:
  ```python
  @st.fragment
  def _save_note_fragment(case_id):
      note = st.text_area("Session note", key="note_input")
      if st.button("Save Note"):
          ProjectManager.add_session_note(case_id, note)
          st.toast("Note saved")
          st.rerun(scope="fragment")
  ```
- [ ] WIRE-02 `@st.fragment` on AIC questions stage — in `streamlit_app/shared/aic.py`: wrap the Q&A loop in a fragment so only the chat area reruns per answer, not the whole workflow page. Each question appears as `st.chat_message("assistant")`, answer via `st.chat_input()`. Fragment reruns on each answer submission; parent page does not reload until all questions answered or skipped.
- [ ] WIRE-03 Multi-step intake with step progress — in `streamlit_app/shared/intake_renderer.py` (or equivalent intake entry point): introduce `intake_step` counter in session state (namespaced: `f"{workflow_id}_intake_step"`). Render fields in logical groups: Step 1 = identification (client, type, jurisdiction), Step 2 = scope parameters (modules, depth, audience), Step 3 = remarks + confirmation. Show `st.progress(step / total_steps)` + `st.caption(f"Step {step} of {total_steps}")` above each group. "Next" button advances step without running the pipeline. "Back" button goes back. Final step has the "Confirm & Continue" button. Applies to Investigation, FRM, DD, Sanctions, TT intake pages — not to Mode B (Policy, Training, Proposal) which have simpler intakes.
- [ ] WIRE-04 Session state namespacing audit — in all 10 workflow pages: prefix every `st.session_state` key with `f"{workflow_id}_"` (e.g. `inv_stage` → `f"{workflow_id}_stage"`). Use a helper `ws(key)` → `f"{workflow_id}_{key}"` defined once in `streamlit_app/shared/state_helpers.py`. Fixes state bleed when Maher navigates between workflow pages without completing them (R-NEW-11 root cause).
- [ ] WIRE-05 `st.dialog()` for destructive confirms — replace any "Reset" / "Start over" / "Clear intake" actions that currently use `st.warning()` + second button with `@st.dialog`. Dialog shows: action description, consequence, Cancel + Confirm buttons. Apply to: intake reset on all workflow pages, engagement deletion if present.
- [ ] WIRE-06 `st.popover()` for contextual metadata — on Case Tracker and Engagements page: replace static status text with a status chip that opens a `st.popover()` on click showing: current status, last state transition timestamp, last agent that ran, revision count. Read from `state.json`. No new data — just surfaces what's already stored.
- [ ] WIRE-07 Stage transition feedback — on all workflow pages, when `stage` changes (intake → ai_questions → running → done): call `st.toast(f"{stage_label}...")` at the transition point so Maher gets an immediate signal the page is advancing, before the spinner appears. E.g. `st.toast("Starting pipeline — this takes 1–3 minutes")` when stage flips to `running`.

#### AC — Sprint-UX-WIRE-01

- [ ] WIRE-01: Clicking "Save Note" in Workspace does not reload the engagement header, sidebar, or context budget bar — visual inspection confirms only the note section updates
- [ ] WIRE-01: `st.toast("Note saved")` appears and fades after save — visual inspection
- [ ] WIRE-01: Same fragment pattern applied to Key Facts, Red Flags, and DD/Sanctions/TT population panels — code inspection of each handler
- [ ] WIRE-02: Answering one AIC question does not reload the workflow page intake form — visual inspection
- [ ] WIRE-02: Skip button inside the fragment still advances the parent page stage to `running` — code inspection of skip handler (uses `st.session_state` write + parent rerun)
- [ ] WIRE-03: Investigation intake shows exactly 3 steps with `st.progress()` indicator — visual inspection
- [ ] WIRE-03: "Back" button on Step 2 returns to Step 1 with previously entered values preserved in session state — visual inspection
- [ ] WIRE-03: FRM, DD, Sanctions, TT intake pages also use step progression — code inspection confirms `intake_step` counter present in each
- [ ] WIRE-04: `state_helpers.py` exists with `ws(workflow_id, key) -> str` helper — code inspection
- [ ] WIRE-04: No bare `st.session_state["inv_stage"]` or similar un-namespaced workflow keys remain in any workflow page — grep confirms all workflow state keys use `ws()` helper
- [ ] WIRE-05: Intake reset action on at least Investigation and FRM pages uses `@st.dialog` confirm — visual inspection
- [ ] WIRE-06: Clicking status chip in Case Tracker opens popover with status, timestamp, last agent, revision count — visual inspection on a case with state.json present
- [ ] WIRE-07: `st.toast()` fires when stage transitions intake → running on any workflow page — visual inspection
- [ ] (regression) All 17 pages still render without crash; existing workflow end-to-end (FRM knowledge_only) completes — manual smoke check by AK before QA_APPROVED

---

---

### Sprint-UX-STREAM-01 — Pipeline Streaming Progress [UNBLOCKED]

**Status:** READY.
**Context:** Pipeline takes 1–3 min with no visible progress. `on_progress` callbacks fire but Streamlit shows only a spinner. Replace with `st.status()` live step labels so Maher sees "Junior drafting... → PM reviewing... → Partner signing off..." as it runs.

- [ ] STREAM-01 Update `streamlit_app/shared/pipeline.py:run_in_status()` — replace `st.spinner` with `st.status(expanded=True)`. Each `on_progress` call appends a `st.write()` line inside the status block with agent name + message. Status label updates to "complete" or "failed" on exit.
- [ ] STREAM-02 Calibrate `total_steps` per workflow — investigation (6), FRM per-module (4 per module), others (3). Pass from each workflow page to `run_in_status(total_steps=N)`.

---

### Sprint-SMOKE-01 — Multi-Level Smoke Test Suite [UNBLOCKED]

**Status:** READY — spec designed Session 042.
**Context:** No formal smoke test suite exists. FE-TRIAGE-01 (manual triage pass) has been pending. This sprint builds the structured suite.

- [ ] SMOKE-BOOT-01 App cold start — `streamlit run app.py`, all pages load, no traceback, sidebar 5 sections
- [ ] SMOKE-BOOT-02 Firm profile present — Settings loads without setup redirect
- [ ] SMOKE-BOOT-03 Page walk 00→16 — every page renders, no P0 crash
- [ ] SMOKE-WF-01 Investigation (standalone) — intake fields, type selectbox, output to F_Final
- [ ] SMOKE-WF-02 FRM (standalone) — 8-module radio, dependency enforcement, xlsx download
- [ ] SMOKE-WF-03 DD (standalone) — subject_count, relationship routing
- [ ] SMOKE-WF-04 Sanctions (standalone) — knowledge_only gate, per_hit_review, disposition
- [ ] SMOKE-WF-05 TT (standalone) — doc upload, label→key maps
- [ ] SMOKE-WF-06 Policy/SOP (standalone) — 11-subtype selectbox, output written
- [ ] SMOKE-WF-07 Training (standalone) — duration selectbox, bool conversion
- [ ] SMOKE-WF-08 Proposal (standalone) — Scope → Proposal, deck output
- [ ] SMOKE-ENG-01 Engagement → Investigation — A-F folders, engagement_id in state.json, Workspace shows section
- [ ] SMOKE-ENG-02 Engagement → FRM — is_af_project() = True
- [ ] SMOKE-ENG-03 Context pre-fill — "Continuing engagement" banner, client_name locked
- [ ] SMOKE-MWF-01 Investigation + FRM — both case_ids in ProjectState.cases, no state contamination
- [ ] SMOKE-MWF-02 DD + Sanctions — independent state.json per workflow
- [ ] SMOKE-EDGE-01 Navigate away mid-intake — state reset cleanly on return
- [ ] SMOKE-EDGE-02 Zero-info path — baseline draft produced, no crash
- [ ] SMOKE-EDGE-03 Legacy UUID case in Tracker — renders, no A-F features shown

---

---

### AKR-08b — docs/hld.md architect session [P2, human-input-required]

- [ ] AKR-08b Run /architect session: populate docs/hld.md gaps + draft docs/lld/ files per feature.
      PARTIAL: hld.md derived from CLAUDE.md; gaps marked [TO VERIFY VIA /architect SESSION]. Full session pending.

---

### Phase 7 — Blank Framework Packaging (GATED on P7-GATE smoke test)

```
P7-GATE ──────────────────── blocks ALL P7 tasks
P7-01 ← P7-GATE ──── P7-02, P7-03
P7-02 ← P7-01 ─────── P7-03, P7-04, P7-05
P7-03 ← P7-01 ─────── P7-05
P7-04 ← P7-02 ─────── P7-05, P7-06
P7-05 ← P7-02,03,04 ─ P7-07
P7-06 ← P7-04 ─────── P7-07
P7-07 ← P7-05, P7-06
```

- ~~[x] P7-GATE~~ PASSED Session 015 — gate cleared
- [ ] P7-01a Grep for "GoodWork", "Maher", "forensic" as string literals. Confirm only 4 locations: run.py:331, partner/prompts.py:8, setup_wizard.py:161, run.py:2.
- [ ] P7-02a Create `instance_config/` directory
- [ ] P7-02b Create `instance_config/firm.json` — {firm_name, firm_type, primary_industry, primary_jurisdiction, enabled_workflows[], persona_set[], language_default, billing_currency}
- [ ] P7-02c Update `config.py` to load instance_config/firm.json; expose FIRM_NAME, FIRM_TYPE, PRIMARY_INDUSTRY
- [ ] P7-02d Update `run.py` to read firm_name from config
- [ ] P7-03a `run.py:331` — replace hardcoded "GoodWork Forensic Consulting" with `config.FIRM_NAME`
- [ ] P7-03b `agents/partner/prompts.py:8` — replace default `firm_name="GoodWork Forensic Consulting"` with `config.FIRM_NAME`
- [ ] P7-03c `core/setup_wizard.py:161` — wrap "GoodWork LLC" prompt default in `config.FIRM_NAME`
- [ ] P7-04a Create `knowledge/README.md` — explains knowledge/ is instance-specific
- [ ] P7-04b Create `knowledge/_template/` with stub framework.md + sources.md
- [ ] P7-05a Create `scripts/create_blank_instance.py` — copies repo, removes GoodWork knowledge content, resets firm_profile/, resets instance_config/firm.json, outputs zip
- [ ] P7-06a Create `INSTANCE_GUIDE.md` — 6-step onboarding for new firms
- [ ] P7-07a Run create_blank_instance.py → new instance directory created
- [ ] P7-07b Run setup wizard on blank instance — firm profile collected for test firm
- [ ] P7-07c Run Option 6 (FRM) on blank instance — confirm works without GoodWork knowledge
- [ ] P7-07d Verify no GoodWork data bleeds into blank instance output

---


### Phase 8 — Manual Verification (requires live API key + streamlit run)

These [ ] tasks were not automated — require AK to run manually. Low priority.

- [ ] P8-00c Verify CLI smoke: `python run.py` Option 6 still advances state after completion
- [ ] P8-02d Verify CLI: `python run.py` Option 6 produces identical output to pre-split
- [ ] P8-05b Verify interim folder structure after live run
- [ ] P8-06e Verify: FRM end-to-end in Streamlit — A/F/R visible and clickable

---

### ARCH-INS-03 — Circuit Breaker for External API Calls (GATED on Phase 8 — pre-production)

**Context:** Inspired by Transplant Insight & Compliance circuit breaker pattern that isolates Anthropic latency from audit writes. Sprint-10I exposed the root problem: Tavily hangs 60s × 3 retries = 3min before graceful fallback. Current mitigation is `RESEARCH_MODE=knowledge_only` default. That is a workaround. The circuit breaker makes `RESEARCH_MODE=live` safe to use even on flaky networks — OPEN state returns fallback immediately without attempting the call.

**State machine:** CLOSED (normal) → OPEN (after failure threshold) → HALF_OPEN (probe) → CLOSED (if probe succeeds).

**Security model:**
- Auth: N/A
- Data boundaries: no change — fallback returns same `ResearchResult` shape with `disclaimer="circuit_open_fallback"`
- PII: no change — sanitisation hooks still fire on returned result
- Audit: no new events; existing research_mode logging unchanged
- Abuse surface: OPEN state returns fixed string — no injection surface

**Config:**
- `CIRCUIT_BREAKER_FAILURE_THRESHOLD=2` — failures within window before OPEN
- `CIRCUIT_BREAKER_WINDOW_SECONDS=30` — rolling window
- `CIRCUIT_BREAKER_RESET_SECONDS=60` — OPEN → HALF_OPEN after this delay

- [ ] INS-03a Create `tools/research/circuit_breaker.py` — `CircuitBreaker` class. State: CLOSED/OPEN/HALF_OPEN. Tracks failure timestamps in a deque. `call(fn, fallback_fn)` — if CLOSED, calls fn; on failure increments counter; if threshold reached within window → OPEN. If OPEN and reset elapsed → HALF_OPEN; probe fn once; success → CLOSED, failure → OPEN. Thread-safe (threading.Lock).
- [ ] INS-03b Wrap `TavilyClient.search()` in `tools/research/general_search.py` with circuit breaker. On OPEN state: return `ResearchResult(query=query, results=[], authoritative_citations=[], disclaimer="circuit_open_fallback — Tavily unreachable")` immediately.
- [ ] INS-03c Apply same breaker instance to `regulatory_lookup.py`, `sanctions_check.py`, `company_lookup.py`. One shared breaker per provider (not per call).
- [ ] INS-03d Add `CIRCUIT_BREAKER_FAILURE_THRESHOLD`, `CIRCUIT_BREAKER_WINDOW_SECONDS`, `CIRCUIT_BREAKER_RESET_SECONDS` to `config.py` with defaults above.
- [ ] INS-03e Smoke test: set `RESEARCH_MODE=live`, disable network, run FRM workflow — confirm no 3min hang; confirm `disclaimer="circuit_open_fallback"` appears in citations index.

---

### Phase 10 — New Service Lines (planning gate: DONE — Session 010)

- [ ] SL-01 Transaction Testing — knowledge/transaction_testing/ ✓ KF done; workflow in Sprint-10E
- [ ] SL-02 Due Diligence — knowledge/due_diligence/ ✓ KF done; workflow in Sprint-10E
- [ ] SL-03 Fraud Audit — knowledge/fraud_audit/ (KF-03 pending)
- [ ] SL-04 Sanctions Screening — knowledge/sanctions_screening/ ✓ KF done; workflow in Sprint-10E
- [ ] SL-05 ESI Review — knowledge/esi_review/ (KF-05 pending)
- [ ] SL-06 Expert Witness Support — knowledge/expert_witness/ (KF-06 pending)
- [ ] SL-07 HUMINT — knowledge/humint/ (KF-07 pending)

---

### Phase 11 — Precision Intake Questionnaires (GATED on Phase 10 planning)

- [ ] PQ-01 Transaction Testing intake: 8–12 questions (transaction types, date range, population size, red flag criteria, regulatory context)
- [ ] PQ-02 Due Diligence intake: 8–12 questions (target type, purpose, depth, jurisdictions, timeline)
- [ ] PQ-03 Fraud Audit intake: 8–12 questions (allegation type, population, data access, preliminary evidence)
- [ ] PQ-04 Sanctions intake: 8–12 questions (entity type, jurisdictions, screening lists, existing relationships)
- [ ] PQ-05 ESI Review intake: 8–12 questions (data volume, custodians, date range, relevance criteria)
- [ ] PQ-06 Expert Witness intake: 8–12 questions (matter type, jurisdiction, opposing expert, issue framing)
- [ ] PQ-07 HUMINT intake: 8–12 questions (subject type, jurisdictions, engagement limits, client authorization)

---

### Phase 12 — Remaining Knowledge Files

KF-00, KF-01, KF-02, KF-04 complete — see releases/completed-tasks.md.

- [ ] KF-03 knowledge/fraud_audit/ (framework + sources)
- [ ] KF-05 knowledge/esi_review/ (EDRM framework + sources)
- [ ] KF-06 knowledge/expert_witness/ (framework + sources)
- [ ] KF-07 knowledge/humint/ (framework + methodology)

---

### Phase 13 — FRM Guided Exercise Design

Planning gate (FRM-R-00) and zero-info planning gate (ZID-00) CONFIRMED Session 010 — see releases/completed-tasks.md.
Implementation tasks: see Sprint-10D (FRM-R-01..08) below.

FRM flow design (confirmed):
- STEP 1: Show scope plan → confirm
- STEP 2: Per module — present sub-areas, consultant confirms which apply
- STEP 3: Per sub-area — 4 questions (incidents? controls? probability? impact?)
- STEP 4: Model generates one RiskItem from answers + regulatory baseline
- STEP 5: Approve / Edit / Skip per item → register assembled from approved only
- Zero-info: model pre-fills with BASELINE answers, consultant reviews each

---

### Phase 13 — Zero-Information Draft Design

- [ ] ZID-01 FRM: if findings=[] after junior run → inject industry-baseline risks from knowledge file before PM review
- [ ] ZID-02 Investigation: if no documents → system prompt instructs junior to draft from typologies + generate open_questions
- [ ] ZID-03 Policy/SOP: if minimal intake → draft from regulatory defaults + flag gaps
- [ ] ZID-04 All agent system prompts: add "never return empty findings/risks — use BASELINE if no client evidence"
- [ ] ZID-05 Session context hygiene: session-open warns if context approaching limit; close before 80%

---

---

### Sprint-10L Phase B — Behavioral Matrix
**BLOCKED: MISSING_BA_SIGNOFF** — moved to tasks/blocked-backlog.md

---

### Sprint-10C — Historical Knowledge Library (depends on Sprint-10A — UNBLOCKED)

- [ ] HRL-00 tools/knowledge_library.py: KnowledgeLibrary class — ingest(file_path, service_type) → intake conversation → sanitise() → index_entry(). sanitise() strips names, passport/ID numbers, company reg numbers, case IDs, identifying dates. Retrieval: match_similar(engagement_params) → list[HistoricalMatch]. Hard gate: SanitisationError blocks index write if PII in stripped output.
- [ ] HRL-01 Historical import wizard — extend setup_wizard.py or add guided_import.py; calls KnowledgeLibrary.ingest() per file; shows index summary. CE Creates DD reports (3) are seed entries. GATED on HRL-00.
- [ ] HRL-02 firm_profile/historical_registers/ dir + index.json schema — GATED on HRL-00
- [ ] HRL-03 firm_profile/historical_reports/due_diligence/ dir + index.json schema — GATED on HRL-00
- [ ] HRL-04 firm_profile/historical_reports/sanctions_screening/ dir + index.json schema — GATED on HRL-00
- [ ] HRL-05 firm_profile/historical_reports/transaction_testing/ dir + index.json schema — GATED on HRL-00
- [ ] HRL-06 firm_profile/historical_scopes/ dir + index.json schema — GATED on HRL-00

#### AC — Sprint-10C
- [ ] HRL-00: `KnowledgeLibrary` class exists in `tools/knowledge_library.py` with `ingest(file_path, service_type)`, `sanitise(raw_text)`, and `match_similar(engagement_params)` methods — code inspection
- [ ] HRL-00: `SanitisationError` is importable from `tools.knowledge_library`; raising it with a message constructs without error — code inspection
- [ ] HRL-00: `sanitise()` called with text containing a string matching a passport number pattern (e.g. `"AB1234567"`) raises `SanitisationError` — behavioural assertion (no API call; regex-based detection)
- [ ] HRL-00: `match_similar({})` on a `KnowledgeLibrary` instance where `firm_profile/historical_registers/index.json` does not exist returns an empty list rather than raising `FileNotFoundError` — negative/fallback case
- [ ] HRL-02 through HRL-06: each of the five directories (`historical_registers/`, `historical_reports/due_diligence/`, `historical_reports/sanctions_screening/`, `historical_reports/transaction_testing/`, `historical_scopes/`) is created under `firm_profile/`; each contains an `index.json` file that is valid JSON with a top-level list structure — file existence and schema check
- [ ] HRL-01: The historical import wizard calls `KnowledgeLibrary.ingest()` for each submitted file; if `SanitisationError` is raised, the wizard surfaces the error message to the user and does NOT write a partial entry to the index — negative case (verify by code inspection of the wizard's except block)

---

### Sprint-10D — FRM Guided Exercise Redesign (depends on ARCH-S-01 — UNBLOCKED after merge)

WARNING: FRM-R-01..08 must be built behind a new workflow path until P7-GATE (FRM smoke test) has a baseline passing run. See R-010.

- [ ] FRM-R-00 Custom risk areas — Maher can add unlimited custom risk areas after the 8 standard modules. Three input modes per area:
      (a) Name only → model generates BASELINE indicative risks (3–5 items)
      (b) Maher's notes → free-text narration of observations/findings; model structures into risk items
      (c) Document upload (interview transcripts, meeting notes, emails) → DocumentManager ingests; model reads and extracts risk signals; asks structured follow-up questions where gaps exist; then structures into formal risk items
      All three modes feed the same 4-question guided flow and approve/flag/rewrite loop.
      Custom areas tagged as CUSTOM in state.json; source mode (BASELINE/CONSULTANT_NOTES/FROM_DOCUMENT) recorded per item in audit_log. Final register treats custom items identically to standard module items.
      BA sign-off required (extends BA-002) before build.
- [ ] FRM-R-01 workflows/frm_risk_register.py: after module selection, present plan summary → "We will assess X sub-areas across Y modules. Proceed?"
- [ ] FRM-R-02 Per-module loop: present sub-areas list → consultant confirms which apply (Y/N/Partial)
- [ ] FRM-R-03 Per-risk-area: 4-question sequence (incidents? controls? probability? impact?). Store in RiskContextItem; pass to model for item generation.
- [ ] FRM-R-04 One-item-at-a-time generation: model generates one RiskItem from RiskContextItem + regulatory baseline. Never generate full register in one call.
- [ ] FRM-R-05 Review loop: show each RiskItem → Approve / Edit / Skip. Edit = structured model conversation, one revision cycle. Override recorded in audit_log.
- [ ] FRM-R-06 Register assembly: only approved items enter final register. Skipped items in state.json as excluded. Empty register warning before assembly.
- [ ] FRM-R-07 Zero-info mode: if all Step 3 answers skipped, model pre-fills RiskContextItem with BASELINE. Consultant still reviews each item — no auto-approval.
- [ ] FRM-R-08 Apply same guided-exercise pattern to Investigation Report scoping phase.

---


### Sprint-10G — Workflow Chaining (GATED on Phase 8 Streamlit)

- [ ] CHAIN-00 core/chain_router.py — CHAIN_MAP: dict[str, list[str]] — 11 valid chains per BA-011; get_compatible_chains(workflow_id) → list[str]; blocked chains enforced by omission. GATED on FE-01..06.
- [ ] CHAIN-01 Post-workflow "Add another deliverable?" prompt — calls chain_router.get_compatible_chains(); threads case_id; updates state.json with all workflow runs. GATED on CHAIN-00.
- [ ] CHAIN-02 case_tracker (Option 9): show all deliverables per case_id when chaining used. GATED on CHAIN-01.

---

### Phase 9 — Engagement Management Framework (GATE CLEARED — P8 merged 97626d9, P8-14 superseded Session 022)

**Design authority:** Architect Session 021. All decisions confirmed by AK in session.
**BA sign-off:** BA-P9-01 through BA-P9-06 in tasks/ba-logic.md.
**Scope:** Replace one-shot UUID case model with a named Project model. Add A-F folder structure, multi-session input, language standards, AI Review Mode, and context accumulation.
**CLI stays intact:** run.py unchanged. Phase 9 is Streamlit-layer only.

**Security model (applies to all P9 tasks):**
- Auth: N/A — localhost:8501, single user
- Data boundaries: all data stays in `cases/{project_slug}/` — no external transmission
- PII: same sanitization hooks (pre_hooks.py) apply; `interim_context.md` is a condensed summary — no PII beyond what's already in case folder
- Audit: project creation, each input session start, final run trigger — all appended to `audit_log.jsonl`
- Abuse surface: project_name → slug conversion MUST strip `..`, `/`, `\`, null bytes, and non-alphanumeric/hyphen chars before any filesystem write (R-019)

```
PHASE 9 DEPENDENCY GRAPH:
P9-01 (schemas/project.py) ─────────────────────────────────── P9-02
P9-02 (ProjectManager class) ─── P9-03A, P9-03B, P9-04, P9-06
P9-03A (Active Engagements page) ──── P9-05, P9-09
P9-03B (New Engagement wizard) ────── P9-05
P9-04 (A-F folder structure) ──────── P9-05, P9-09
P9-05 (Input session UI) ──────────── P9-09
P9-06 (Context accumulation) ─────── P9-09
P9-07A (Language standard settings UI) ─── P9-07B
P9-07B (Apply standard to agent prompts) ── P9-09
P9-08 (AI Review Mode) ─────────────────── P9-09
P9-09 (Wire all workflow pages to project context) ← all above
```

---

#### P9-01, P9-02, P9-03A, P9-03B — DONE
Schemas (schemas/project.py), ProjectManager (tools/project_manager.py),
and Engagements page (pages/01_Engagements.py) built in Phase A + Phase D.
Full specs archived in releases/completed-tasks.md.

---

#### P9-04 — A-F Folder Structure in tools/file_tools.py
**File:** `tools/file_tools.py`
**Deps:** P9-01
**BA:** BA-P9-02
**Note:** `ProjectManager.create_af_structure()` handles creation. This task ensures `file_tools.py` route functions (case_dir, write_artifact, etc.) respect A-F layout for NEW projects.

- [x] P9-04a Add `AF_FOLDERS` constant to `tools/file_tools.py` — DONE Phase F (4315d2a)
- [x] P9-04b Add `is_af_project(case_id: str) -> bool` — DONE Phase F (4315d2a)
- [x] P9-04c — DONE Phase G (9f83126)
- [ ] P9-04d Post-run migration (existing P8-05a) updated: migrates root `*.v*.json` → `E_Drafts/` (not `interim/`) for AF projects; `interim/` used only for legacy projects.

#### AC — P9-04
- [ ] `is_af_project("project-alpha-frm")` returns True when `cases/project-alpha-frm/E_Drafts/` exists
- [ ] `is_af_project("20260418-0C0A8D")` returns False (legacy case has no E_Drafts/)
- [ ] `write_artifact()` for AF project writes to `cases/{slug}/E_Drafts/` — verified by code inspection
- [ ] `write_final_report()` for AF project writes to `cases/{slug}/F_Final/` — verified by code inspection
- [ ] Legacy cases: `write_artifact()` and `write_final_report()` paths unchanged

---

#### P9-05 — Input Session UI (Project Workspace page)
**New file:** `pages/1_Engagements.py` (workspace stage within same page, or separate `pages/workspace.py`)
**Deps:** P9-03A, P9-03B, P9-04
**BA:** BA-P9-02, BA-P9-03

- [ ] P9-05a Project header: project name, client name, service type, language standard chip, last session date
- [ ] P9-05b A-F folder tree: collapsible `st.expander` per section (A through F); inside each expander, list files in that folder with size + date; "Upload to this section" button per folder
- [ ] P9-05c Session mode selector: "Input Session" | "Final Run" radio — prominent, cannot be missed
- [ ] P9-05d Input session panel (shown when mode=Input):
  - `st.file_uploader` (goes to C_Evidence/{timestamp}/)
  - Session Notes text area → "Save Note" button → `add_session_note()`
  - Key Facts form (fact text + source + date) → "Add Fact" → `add_key_fact()`
  - Red Flag form (description + severity selectbox) → "Flag" → `add_red_flag()`
  - Context budget bar: `st.progress()` showing % of budget used; warning at 75%
- [ ] P9-05e Final Run panel (shown when mode=Final Run): shows accumulated materials summary (document count, note count, fact count, flag count); "Run [Service Type] Pipeline" primary button → routes to existing workflow page with `active_project` context passed

#### AC — P9-05
- [ ] Input / Final Run mode selector is prominent (radio buttons at top of workspace, not hidden in sidebar)
- [ ] Context budget bar shows correct percentage (from `get_context_summary()`)
- [ ] At 75%+, budget bar turns red and `st.warning("Context limit approaching — a summary will be written to Working Papers.")` shown
- [ ] "Save Note" appends to session_notes file — does NOT overwrite; repeated saves accumulate
- [ ] Final Run panel shows materials summary BEFORE the Run button — Maher knows what context the pipeline will receive

---

#### P9-06 — Context Accumulation + 75% Threshold → interim_context.md
**Files:** `tools/document_manager.py`, `tools/project_manager.py`
**Deps:** P9-02
**BA:** BA-P9-04
**Security model:** `interim_context.md` written to `D_Working_Papers/` inside case folder only; Haiku model call for summarization; no external transmission.

- [ ] P9-06a Add `CONTEXT_BUDGET_CHARS` to `config.py` — default: `400_000` (≈ 100k tokens, conservative for sonnet-4 200k window minus overhead)
- [ ] P9-06b `DocumentManager.get_total_chars()` — sum char lengths of all registered documents
- [ ] P9-06c `DocumentManager.context_usage_pct()` — returns `get_total_chars() / CONTEXT_BUDGET_CHARS * 100`
- [ ] P9-06d After each `register_document()` call: check `context_usage_pct()`. If ≥ 75%: call `_trigger_interim_context_write(case_id)`.
- [ ] P9-06e `_trigger_interim_context_write(case_id)`: calls Haiku with system prompt "Summarize the following documents into a concise briefing — key facts, red flags, open questions, critical excerpts. Be comprehensive — this summary replaces the source documents in future sessions." → response written via `ProjectManager.write_interim_context()`.
- [ ] P9-06f `DocumentManager.get_context_for_agents()` — if `interim_context.md` exists: return its content + content of any documents registered AFTER its creation date. Otherwise: return all document content.

#### AC — P9-06
- [ ] `context_usage_pct()` returns `> 0` when at least one document is registered
- [ ] `context_usage_pct()` returns `0.0` when no documents registered
- [ ] At 75%+ usage: `D_Working_Papers/interim_context.md` created (code inspection: `_trigger_interim_context_write` called)
- [ ] `get_context_for_agents()` returns `interim_context.md` content when file exists — not all raw document content
- [ ] `get_context_for_agents()` returns all raw document content when `interim_context.md` absent
- [ ] `interim_context.md` is NOT included in `get_total_chars()` calculation — only source documents counted

---

#### P9-07A — Language Standard Settings (in pages/settings.py)
**File:** `pages/settings.py`
**Deps:** P9-01
**BA:** BA-P9-05
**Note:** Language standard is set per-project at intake. Settings page shows the FIRM DEFAULT only. Per-project override is in New Engagement wizard (P9-03B).

- [x] P9-07Aa Add "Default Language Standard" selectbox to Settings page — DONE (already in pages/14_Settings.py)
- [x] P9-07Ab Save writes `firm_profile/firm.json["default_language_standard"]` — DONE
- [x] P9-07Ac Load at bootstrap: `st.session_state.default_language_standard` — DONE Phase H

#### AC — P9-07A
- [x] Settings page has "Default Language Standard" selectbox with exactly 4 options (matching BA-P9-05 labels)
- [x] Saving updates `firm.json["default_language_standard"]`; existing firm.json fields unchanged
- [x] Bootstrap loads default and exposes it in `st.session_state`

---

#### P9-07B — Apply Language Standard to All Agent System Prompts
**Files:** `agents/junior_analyst/prompts.py`, `agents/project_manager/prompts.py`, `agents/partner/prompts.py`
**Deps:** P9-01, P9-07A
**BA:** BA-P9-05

- [x] P9-07Ba `agents/shared/language_standards.py` — DONE Phase H
- [x] P9-07Bb All three agents' `build_system_prompt()` accept `language_standard` param — DONE Phase H
- [x] P9-07Bc All three agents' `__call__()` pass `context.get("language_standard", "acfe")` — DONE Phase H

#### AC — P9-07B
- [x] `build_system_prompt(language_standard="expert_witness")` includes "court-ready" and "Past tense only" in the returned string — code inspection
- [x] `build_system_prompt(language_standard="acfe")` includes "qualified language" — code inspection
- [x] `context.get("language_standard", "acfe")` pattern used in all three agent `__call__()` methods
- [x] Missing `language_standard` in context → defaults to "acfe" (no KeyError)

---

#### P9-08 — AI Review Mode
**New file:** `agents/reviewer/review_agent.py` (or inline in orchestrator)
**Deps:** P9-07B, Phase 8 complete
**BA:** BA-P9-06
**Note:** Runs as a post-pipeline pass before Maher's review screen. Uses Haiku (speed/cost). Results stored in D_Working_Papers/.

- [x] P9-08a `agents/reviewer/review_agent.py` — DONE Phase H
- [x] P9-08b `ReviewAnnotation` in `schemas/artifacts.py` — DONE Phase H
- [x] P9-08c `ReviewAgent.__call__()` — DONE Phase H (citations=[] auto-unsupported, Haiku for rest)
- [x] P9-08d Wired into investigation_report.py + frm_risk_register.py run_frm_finalize() — DONE Phase H
- [x] P9-08e FRM done stage badges (green/amber/red with evidence_cited + logic_gaps popover) — DONE Phase H

#### AC — P9-08
- [x] `ReviewAnnotation` importable from `schemas.artifacts`; `support_level="invalid"` raises ValidationError
- [x] ReviewAgent produces exactly one annotation per finding — same count as `draft["findings"]`
- [x] Finding with `citations=[]` → automatically classified as `"unsupported"` (no model call needed; code inspection)
- [x] `ai_review_{date}.json` written to `D_Working_Papers/` inside case folder — not to root
- [x] Review badges visible in FRM review stage (P8-06c): green/amber/red per risk item
- [x] AI Review Mode can be disabled: `context.get("ai_review_enabled", True)` — when False, ReviewAgent not called; badges absent

---

~~P9-09 archived → releases/completed-tasks.md (commit c8ee66f)~~

---

### Sprint-EMB — Semantic Embeddings Layer (Session 022 — GATE CLEARED — P8 merged 97626d9)

**BA:** BA-R-11
**Security:** All paths via case_dir(); ChromaDB runs in-process; no shell execution; no external data transmission beyond Haiku extraction API call.

```
EMB-01 (EmbeddingEngine) ─── EMB-02, EMB-03
EMB-02 (ingestion pipeline) ─ EMB-04
EMB-03 (retrieval UI) ──────── independent
EMB-04 (pipeline context) ──── P9-09 wire-up
```

- ~~[x] EMB-00~~ DONE (requirements.txt updated)
- [x] EMB-01 `tools/embedding_engine.py` — DONE Session 033 (feature/sprint-emb)
- [x] EMB-02 Wire into `DocumentManager.register_document()` — DONE Session 033 (feature/sprint-emb)
- [x] EMB-03 Semantic search UI in Input Session workspace — DONE Session 033 (feature/sprint-emb)
- [x] EMB-04 Pipeline context prep in `core/orchestrator.py` — DONE Session 033 (feature/sprint-emb)

**Status: READY_FOR_REVIEW**

#### AC — Sprint-EMB
- [x] EMB-01: `EmbeddingEngine` class exists in `tools/embedding_engine.py` with `chunk_document()`, `embed_and_index()`, `search(query, n=5)`, and `get_context_for_query(query, max_chars=8000)` methods — PASS (spec names added as public methods; `embed_document()` and `retrieve()` retained for DocumentManager compatibility)
- [x] EMB-01: When `sentence-transformers` is not installed, `EmbeddingEngine(case_id).available` is `False` and calling `get_context_for_query()` returns an empty string rather than raising an `ImportError` — PASS (verified by code inspection + python3 -c test)
- [ ] EMB-02: After `DocumentManager.register_document()` completes, `EmbeddingEngine(case_id).chunk_count(doc_id)` returns a value greater than 0 for a document with at least 800 characters of content — behavioural assertion requires sentence-transformers installed in test env; call path verified by code inspection
- [x] EMB-02: `D_Working_Papers/case_intake.md` exists after the first `register_document()` call on a new case — PASS (_append_case_intake() added; atomic write via .tmp/os.replace)
- [x] EMB-03: Semantic search UI component calls `EmbeddingEngine.search()` when query is submitted; when engine unavailable shows fallback message — PASS (code inspection)
- [x] EMB-04: In `core/orchestrator.py`, when `EmbeddingEngine(case_id).available` is `True`, context dict contains `embedded_context` key; when `False`, key is absent — PASS (code inspection + python3 -c test)

---

### Sprint-AIC — Smart Intake Completion (Session 022 — GATE CLEARED — P8 merged 97626d9)

**BA:** BA-R-10
**Security:** No new data paths; Haiku/Sonnet API calls gated on RESEARCH_MODE; results stored only in D_Working_Papers/; no client data transmitted beyond existing API call pattern.

```
AIC-01 (post-intake pass) ─── AIC-03
AIC-02 (pre-final-run pass) ── AIC-03
AIC-03 (inject into pipeline) ← AIC-01 + AIC-02
```

- [x] AIC-01 Post-intake Haiku pass — DONE Phase F (4315d2a)
- [x] AIC-02 Pre-final-run Sonnet pass — DONE Phase F (4315d2a)
- [x] AIC-03 `ProjectManager.get_intake_qa_context()` + `get_prefinalrun_context()` — DONE Phase F (4315d2a)

---

### Sprint-RD — Report Design Layer (Session 022 — runs parallel to Phase 9)

**BA:** BA-R-01, BA-R-02, BA-R-03
**Security:** No shell execution; all paths via case_dir() or firm_profile/ constants; template .docx write is atomic (.tmp → os.replace()).

```
RD-01 ──── RD-03, RD-05, RD-06
RD-02 ──── RD-03
RD-04 ──── independent (called by RD-03)
```

- [x] RD-00 Add `openpyxl>=3.1.0` to `requirements.txt` — DONE (already present before Phase F)
- [x] RD-01 `tools/report_builder.py` — DONE Phase G (9f83126)
- [x] RD-02 `streamlit_app/shared/template_selector.py` — DONE Phase H
- [x] RD-03 `tools/file_tools.py:write_final_report()` — DONE Phase H (uses BaseReportBuilder, section_overrides, _version_existing_report)
- [x] RD-04 `tools/file_tools.py:_version_existing_report()` — DONE Phase H
- [x] RD-05 Investigation section overrides in `workflows/investigation_report.py` — DONE Phase H (13-section)
- [x] RD-06 FRM section overrides in `workflows/frm_risk_register.py` — DONE Phase H (7-section)

---

~~Sprint-WF + Sprint-FR archived — see releases/completed-tasks.md (commit 3b498cc)~~

---

### Sprint-FE — Frontend Impact Tasks (Session 022 — GATED on P9-05 design)

**BA:** BA-FE-01, BA-FE-02 — CONFIRMED 2026-04-20
**Scope:** Frontend changes required by Sprint-EMB, Sprint-AIC, Sprint-RD, Sprint-WF, Sprint-FR, Phase 9
**Security:** Same as Phase 8 — localhost:8501, no auth, no new data paths

- [x] FE-GATE-BA: CLEARED — BA-FE-01 (AI questions stage) + BA-FE-02 (workspace panels all workflows) confirmed 2026-04-20

- [x] FE-01 All 10 workflow pages: add `ai_questions` stage between intake and running — DONE Session 033
- [x] FE-02 `pages/14_Settings.py` — Template Selector section using `render_template_selector()` — DONE Session 033
- [x] FE-03 `pages/06_FRM.py` — Done stage xlsx download button via `FRMExcelBuilder` — DONE Session 033
- [x] FE-04 `pages/10_Sanctions.py` — `per_hit_review` stage with dispositions + policy default — DONE Session 033
- [x] FE-05 `pages/09_Due_Diligence.py` — subject_count, relationship_type, template_upload fields + routing — DONE Session 033
- [x] FE-06 `pages/16_Workspace.py` — DD/Sanctions/TT workflow-specific panels gated on service_type — DONE Session 033
- [x] FE-07 `pages/12_Case_Tracker.py` — Previous Versions section with download buttons — DONE Session 033

#### AC — Sprint-FE
- [x] FE-01: On all 10 workflow pages (02, 04, 05, 06, 07, 08, 01_Scope, 11, 10, 09), an `ai_questions` stage exists between intake confirmation and `running`; the stage calls `render_intake_questions()` from `streamlit_app/shared/aic.py` — code inspection of each page
- [x] FE-01: When `render_intake_questions()` returns `True` (questions answered or skipped), the page transitions to `running` stage — code inspection of stage transition logic
- [x] FE-01: When AIC-01 returns 0 questions, `render_intake_questions()` returns `True` immediately and the `ai_questions` stage is bypassed — code inspection of `aic.py` (already implemented); page must not block on empty question list
- [x] FE-01: Answered questions are written to `D_Working_Papers/case_intake.md` as `Q: <text>\nA: <answer>`; skipped questions written as `Q: <text>\nA: [SKIPPED]` — code inspection of `_save_intake_qa()` in `aic.py`
- [x] FE-01: A Skip button is visible during the `ai_questions` stage on every page; clicking it calls `_save_intake_qa()` with all remaining questions marked `[SKIPPED]` and transitions to `running` — code inspection
- [x] FE-02: `pages/14_Settings.py` renders a Template Selector section with one `render_template_selector(workflow_type)` call for each of: `frm_risk_register`, `investigation_report`, `due_diligence`, `transaction_testing`, `sanctions_screening`, `client_proposal` — code inspection
- [x] FE-02: Selecting a template saves `firm_profile/firm.json["templates"][workflow_type]` with the chosen filename; if `firm.json` does not exist, it is created — code inspection of save handler
- [x] FE-03: `pages/06_FRM.py` Done stage renders a `st.download_button` labelled "Download Risk Register (.xlsx)" alongside the existing DOCX button — code inspection
- [x] FE-03: The `.xlsx` download button is only rendered if the Excel file exists under `F_Final/`; if the file is absent the button is not shown and no error is raised — code inspection of the conditional
- [x] FE-04: `pages/10_Sanctions.py` has a `per_hit_review` stage between `running` and `done`; one `st.expander` per entity hit is rendered — code inspection
- [x] FE-04: Each hit expander contains a disposition `st.selectbox` with options: True Match / False Positive / Requires Investigation / Escalate; firm default pre-loaded from `sanctions_disposition_policy.json` when file exists — code inspection
- [x] FE-04: "Confirm all dispositions" button writes dispositions to `D_Working_Papers/` and transitions to `done` stage — code inspection of the confirm handler
- [x] FE-05: `pages/09_Due_Diligence.py` intake form includes `st.number_input` for subject count (min=1), `st.radio` for relationship type (Unrelated / Related), and `st.file_uploader` for DD template (.docx) — code inspection
- [x] FE-05: When `subject_count == 1` AND `relationship == "Unrelated"`, the pipeline is routed to per-subject format; when `subject_count > 1` OR `relationship == "Related"`, routed to consolidated format — code inspection of routing condition
- [x] FE-06: `pages/16_Workspace.py` renders a "DD Subjects" expander only when `state.service_type == "Due Diligence"`; adding a subject with a non-empty name appends to `dd_subjects.json` atomically; empty name shows inline error and does not write — code inspection
- [x] FE-06: `pages/16_Workspace.py` renders a "Screening Targets" expander only when `state.service_type == "Sanctions Screening"`; adds to `sanctions_targets.json` atomically; empty name blocked — code inspection
- [x] FE-06: `pages/16_Workspace.py` renders a "Transaction Populations" expander only when `state.service_type == "Transaction Testing"`; adds to `tt_populations.json` atomically; empty name or count ≤ 0 blocked — code inspection
- [x] FE-06: When `state.service_type` is unrecognised (e.g. legacy type), no workflow-specific panel is rendered and no exception is raised — code inspection of the service_type dispatch block
- [x] FE-07: `pages/12_Case_Tracker.py` project detail expander shows a "Previous Versions" section listing files in `Previous_Versions/` with `st.download_button` per file — code inspection
- [x] FE-07: "Previous Versions" section is not rendered when `Previous_Versions/` folder does not exist for the project — code inspection of the conditional check

**Status: READY_FOR_REVIEW**

---

~~Sprint-TPL — DONE. TPL-01..05 all merged. Archived to releases/completed-tasks.md (Session 035).~~

---

### Sprint-IA-01 — Product IA Redesign Phase 1: Navigation + Multi-Workflow (Session 036)

**BA sign-off:** BA-IA-01, BA-IA-02, BA-IA-03 — confirmed AK 2026-04-21
**Branch:** `feature/sprint-fe-triage` (continuing on same branch — no new branch needed)
**Context:** AK identified fundamental IA issue during FE-TRIAGE-01 pass. Engagement must be root entity. Two arcs: Proposal (Arc 1) and Engagement (Arc 2). Workflow pages demoted from primary nav to secondary. Full design in ba-logic.md Session 036 section.
**LLD:** `docs/lld/product-ia-design.md` — authority for all navigation and arc decisions.

#### Phase 0 — Doc updates (all BLOCK MERGE TO MAIN — do not block individual build tasks)

- [x] **[ARCH-DOC-01]** HLD refresh — update `docs/hld.md` to reflect post-Phase 8/9 state: (a) System Overview: add Streamlit as primary entry point, (b) Major Components: add streamlit_app/, ProjectManager, EmbeddingEngine, TemplateManager, ActivityLogger, schemas/project.py, (c) Architecture/Data Flow: add Phase 9 engagement flow + Proposal arc + two-arc model, (d) Deployment Model: Streamlit replaces run.py as primary UI (run.py remains for CLI mode), (e) Phase 10-13 section: add Phase 9 decisions. LLD `docs/lld/product-ia-design.md` already written (Session 036). ← no deps | P0 | **BLOCKS MERGE TO MAIN** | AC: hld.md Status = `active`; Major Components includes all Phase 8/9 additions; Architecture/Data Flow shows two arcs; Deployment Model reflects Streamlit as primary.
  - **Auth:** none (doc-only) | **Data:** none | **PII:** none | **Audit:** none | **Abuse:** none

- [x] **[ARCH-DOC-02]** README.md full rewrite — current README describes the old `python run.py` CLI with a 10-item terminal menu. Must be completely rewritten to reflect: (a) Streamlit as primary entry point (`streamlit run app.py`), (b) project/engagement model (Projects with 1–N workstreams), (c) two-arc flow (Proposal arc → Engagement arc), (d) full service line list including DD, Sanctions, TT, AUP, and new investigation types (8 types including AUP + Custom), (e) updated output folder structure (A–F per engagement), (f) updated cost guide, (g) updated troubleshooting for Streamlit. Audience: white-label customer reading for the first time. ← no deps | P0 | **BLOCKS MERGE TO MAIN** | AC: README describes Streamlit entry point; lists all current service lines; project/engagement model explained; no mention of `python run.py` as primary path.
  - **Auth:** none (doc-only) | **Data:** none | **PII:** none | **Audit:** none | **Abuse:** none

- [x] **[ARCH-DOC-03]** Framework brief + scope brief update — (a) `docs/GoodWork_AI_Framework_Brief.md`: update to reflect Streamlit UI, full service line list, two-arc model, project/engagement structure — this is the white-label pitch/executive doc; (b) `docs/scope-brief.md`: move Streamlit from should-have to done; add AUP and Expert Witness to must-have; update Cut-for-Now list to reflect Session 036 decisions. ← no deps | P1 | **BLOCKS MERGE TO MAIN** | AC: Framework Brief mentions Streamlit and all service lines; scope-brief.md reflects current product state accurately.
  - **Auth:** none (doc-only) | **Data:** none | **PII:** none | **Audit:** none | **Abuse:** none

#### Phase A — App-level fixes (no deps on ARCH-DOC-01 — coding can start immediately)

- [x] **[IA-00]** Seed test data script — create `scripts/seed_test_engagement.py`. Writes a mock `ProjectState` with `project_name="ABC Corp Test Engagement"`, `client="ABC Corp"`, and 3 entries in `cases`: `{"investigation_report": "case_test_001", "frm_risk_register": "case_test_002", "due_diligence": "case_test_003"}`. For each case_id: create `cases/{case_id}/state.json` (status=DELIVERABLE_WRITTEN), `cases/{case_id}/F_Final/final_report.en.md` (3-line placeholder), `cases/{case_id}/F_Final/final_report.en.docx` (empty docx via python-docx). No API calls. Run once before testing IA-04. ← no deps | P0 | AC: script runs without error; `streamlit run app.py` → Workspace shows 3 workflow sections under the test engagement; each section shows a download link.
  - **Auth:** local only | **Data:** writes to cases/ (test data only — gitignored) | **PII:** none | **Audit:** none | **Abuse:** none

- [x] **[IA-01]** Fix `app.py` bootstrap — add `try/except` + `caller_file=__file__` to `session = bootstrap(st)` call on line 25. Same pattern applied to all pages in FE-TRIAGE-05. ← no deps | P0 | AC: app.py bootstrap failure renders error panel, not blank crash; `bootstrap(st, caller_file=__file__)` called in app.py.
  - **Auth:** local only | **Data:** no change | **PII:** none | **Audit:** none | **Abuse:** none

- [x] **[IA-02]** Navigation restructure — replace pages/ directory convention with `st.navigation()` in `app.py`. Group pages into sections per `docs/lld/product-ia-design.md` (MAIN: Engagements, Workspace; PROPOSALS: Scope, Proposals; MONITOR: Case Tracker, Activity Log; SETTINGS: Team, Settings; WORKFLOWS: all workflow pages). 00_Setup not in nav (redirect-only). Use `st.Page(title=...)` to set display names — fixes "b Scope" → "Scope" without file rename. ← deps: IA-01 | P0 | AC: sidebar shows exactly 5 sections (MAIN, PROPOSALS, MONITOR, SETTINGS, WORKFLOWS); "b Scope" gone, replaced by "Scope" in PROPOSALS; 00_Setup not visible in sidebar; all workflow pages still reachable; existing `st.switch_page()` calls still work.
  - **Auth:** local only | **Data:** no change | **PII:** none | **Audit:** none | **Abuse:** none

#### Phase B — Engagement multi-workflow

- [x] **[IA-03]** Verify multi-workflow in `01_Engagements.py` — confirm "Run Workflow" selectbox (line ~199) allows ALL workflow types regardless of engagement's primary `service_type`. If any restriction exists, remove it. ← no deps | P1 | AC: an engagement created with service_type "Investigation Report" can also launch FRM, DD, or any other workflow from the Engagements detail panel without error.
  - **Auth:** local only | **Data:** reads ProjectState; writes active_project to session_state | **PII:** none | **Audit:** none | **Abuse:** service_type is read from state.json, not user input at this point

- [x] **[IA-04]** Workspace multi-workflow outputs — update `16_Workspace.py` to show all workflow runs under the active engagement, not just the primary. Read `ProjectState.cases` dict (all workflow_type → case_id entries) and render a section per workflow with links to its outputs in E_Drafts/ and F_Final/. ← no deps | P1 | AC: an engagement with 2+ workflow runs shows a section per workflow in Workspace; each section shows latest draft/final report download link; engagement with 0 runs shows "No workflows run yet."
  - **Auth:** local only | **Data:** reads cases/{slug}/; no writes | **PII:** report content is Maher's work product, stored locally | **Audit:** none | **Abuse:** slug validated by ProjectManager._safe_slug()

#### Phase C — Proposal arc v1 (navigation only — no new functionality)

- [x] **[IA-05]** Reposition Proposal arc in navigation — in the `st.navigation()` config, move `07_Proposal.py` into a "Proposals" section with title "Proposals". Move `01b_Scope.py` (display title: "Scope") into same section as step 1 of Arc 1. Add a static info panel at top of 07_Proposal.py: "Arc 1 — Proposal: Step 2 of 3 (Proposal Deck). Complete Scope first, then upload signed letter to create an Engagement." ← deps: IA-02 | P2 | AC: sidebar shows "Proposals" section with "Scope" and "Proposals" entries; 07_Proposal.py renders info banner at top; no other page content changes.
  - **Auth:** local only | **Data:** no change | **PII:** none | **Audit:** none | **Abuse:** none

#### Phase D — Verification

- [ ] **[IA-VERIFY]** Full page walk — run `streamlit run app.py`, confirm new sidebar structure, confirm all pages still load, confirm multi-workflow launch from Engagements, confirm Workspace shows workflow outputs. ← deps: IA-01..05 | AC: sidebar matches 4-section design; all 17 pages render; no new crashes introduced.

**Note:** IA-06 (full Proposal arc with scoping conversation + engagement letter generation) is Sprint-IA-02 — separate session. This sprint is navigation and multi-workflow only.

---

### Sprint-FE-TRIAGE — Frontend Smoke Test + Bug Fix (target: ~2026-05-05)

**Context:** AK ran manual frontend testing (2026-04-21). Pages 00 (Setup), 01 (Engagements/Scope), and 16 (Workspace) showed crashes or errors. Workflow execution was broken. Exact errors not captured — triage session required.
**Pre-condition:** Run `streamlit run app.py` with `RESEARCH_MODE=knowledge_only` and go through each page in order, capturing exact error messages. No API calls needed for triage.
**Scope:** All 17 pages (00–16). Triage first, fix second.
**Branch:** `feature/sprint-fe-triage`
**Root causes (Session 036, diagnosed before triage pass):** RC1 QA gate gap, RC2 naming collision, RC3 private Streamlit API, RC4 bootstrap crash, RC5 no integration test.

#### Phase A — Discovery

- [ ] **[FE-TRIAGE-01]** Triage pass (junior-dev) — run `streamlit run app.py` with `RESEARCH_MODE=knowledge_only`. Open pages 00→16 in order from a clean browser session. For each page capture: exact traceback or visible error text, crash-on-load vs crash-on-action, severity P0/P1/P2. Record in triage table in `tasks/fe-triage-table.md`. No fixes in this task. ← no deps | AC: triage table exists with one row per page (17 rows); every P0 has a full traceback; table committed to branch before FE-TRIAGE-02 starts.
  - **Auth:** local only, no external access
  - **Data boundaries:** reads pages/ and streamlit_app/ only; no case data written
  - **PII:** none
  - **Audit:** append `fe_triage_pass_complete` event to audit_log.jsonl on completion
  - **Abuse surface:** read-only pass; no mutations

#### Phase B — Pre-defined structural fixes (parallel with Phase A)

- [x] **[FE-TRIAGE-03]** Fix naming collision — rename `pages/01_Scope.py` to `pages/01b_Scope.py`. Verify sidebar renders both pages without duplication or shadowing. ← no deps | P0 | AC: `streamlit run app.py` sidebar shows both Scope and Engagements pages; no 404 on either; no duplicate entries.
  - **Auth:** local only
  - **Data boundaries:** pages/ rename only; no schema or state change
  - **PII:** none
  - **Audit:** none required (structural rename)
  - **Abuse surface:** none

- [x] **[FE-TRIAGE-04]** Replace private Streamlit API in `_maybe_redirect_to_setup` — `streamlit_app/shared/session.py:156-179`. Remove `get_script_run_ctx`, `ctx.page_script_hash`, `ctx.script_path`. Replace with caller-filename detection: add optional `caller_file: str = ""` param to `bootstrap(st, caller_file=__file__)` and check `"00_Setup" in caller_file` instead. Update all 17 `bootstrap(st)` call sites to pass `__file__`. ← no deps | P0 | AC: `bootstrap(st, caller_file=__file__)` called on all pages; `_maybe_redirect_to_setup` contains no Streamlit runtime imports; 00_Setup.py does not redirect to itself; any other page redirects to setup when readiness check fails.
  - **Auth:** local only
  - **Data boundaries:** session.py only; no state change
  - **PII:** none
  - **Audit:** none required
  - **Abuse surface:** caller_file is a string passed from `__file__` — not user-controlled

- [x] **[FE-TRIAGE-05]** Harden bootstrap call sites — wrap `session = bootstrap(st, caller_file=__file__)` in try/except at all 17 page call sites. On exception: render `st.error(f"Page failed to load: {e}")` + `st.stop()`. Prevents blank crash; gives Maher a readable error and a path to report it. ← deps: FE-TRIAGE-04 | P1 | AC: artificially break one import in bootstrap, confirm the page renders an error panel instead of a blank crash; restore import; confirm normal page renders correctly.
  - **Auth:** local only
  - **Data boundaries:** pages/ only; no state mutation on failure path
  - **PII:** exception message must not include file contents or case data — verify error string is safe before rendering
  - **Audit:** none required
  - **Abuse surface:** error message rendered via st.error() — no HTML injection risk in Streamlit's safe renderer

#### Phase C — Unknown fixes (blocked on FE-TRIAGE-01)

- [ ] **[FE-TRIAGE-02]** Root cause grouping (architect) — read `tasks/fe-triage-table.md`. Group errors by root cause category (import failure, missing session key, broken API call, version mismatch, layout bug). Write FE-TRIAGE-06..N fix tasks below, one task per root cause group. ← deps: FE-TRIAGE-01 | AC: every P0 and P1 from triage table is covered by a fix task; fix tasks written to this sprint block before any fix code is written.

- [ ] **[FE-TRIAGE-06..N]** Fix tasks — written by architect after FE-TRIAGE-02. Placeholder; expanded in next session.

#### Phase D — Verification

- [ ] **[FE-TRIAGE-VERIFY]** Full page walk from clean state — run `streamlit run app.py`, open pages 00→16 in order, confirm all P0s and P1s resolved. This is the QA_APPROVED gate for the entire sprint. ← deps: FE-TRIAGE-03, 04, 05, 06..N | AC: all 17 pages render without exception; no P0 remains; P2s documented but do not block merge; triage table updated with PASS/FAIL per fix.

**Process fix (permanent — applies after this sprint):** Every sprint touching `pages/` must include AC: "run `streamlit run app.py`, open all affected pages, confirm render before QA_APPROVED." Architect enforces this at task decomposition time.

**Note:** FE-TRIAGE-02 and FE-TRIAGE-06..N are blocked on FE-TRIAGE-01. FE-TRIAGE-03/04 can start immediately. FE-TRIAGE-05 blocked on FE-TRIAGE-04 (needs updated bootstrap signature).

---

### Sprint-WORK — Interim Workpaper Generation (Session 024)

**BA:** BA-WORK-01 — CONFIRMED 2026-04-19
**Note:** WORK-01 DONE (merged Phase D). WORK-02 and WORK-03 are next.

- ~~[x] WORK-01~~ DONE — workflows/workpaper.py built Phase D
- [x] **[WORK-02]** Trigger in Case Tracker — "Generate Workpaper" button in detail expander per UX-015: visible for cases with status `JUNIOR_DRAFT_COMPLETE` or `PM_REVIEW_COMPLETE`. Button calls `WorkpaperGenerator.generate(case_id, source_artifacts)` where source_artifacts are loaded from case folder E_Drafts (junior_output.v*.json, pm_review.v*.json). Shows download button in Case Tracker detail expander after generation: `st.download_button("Download Workpaper (.md)", ...)` with filename pattern `workpaper_{case_id}_{YYYYMMDD}.md`. Greyed out (disabled, tooltip "No draft material yet") for cases with status `INTAKE_CREATED`. Not shown for terminal states (`OWNER_APPROVED`, `DELIVERABLE_WRITTEN`). ← deps: WORK-01 | AC: button visible for `JUNIOR_DRAFT_COMPLETE` case; button absent for `INTAKE_CREATED` case; generated file downloadable from tracker without navigating to case folder.
- [x] **[WORK-03]** Secondary trigger in pipeline done stage — secondary `st.button("Generate Interim Workpaper")` below primary download button on Investigation and FRM done stages per UX-015. Calls same `WorkpaperGenerator.generate()`. Shows inline `st.spinner("Generating workpaper...")` during generation. Renders a second download button for the workpaper after generation. Does not re-trigger the pipeline. ← deps: WORK-01 | AC: button present on FRM done stage and Investigation done stage; clicking generates workpaper without any agent pipeline re-run (verify by checking audit_log — no new Junior/PM/Partner events); workpaper download available immediately after generation.

---

### Sprint-CONV — Conversational Evidence Mode (Session 024)

**BA:** BA-CONV-01 — CONFIRMED 2026-04-19
**Security:** Context window cap (16,000 chars per turn) prevents prompt injection via large document uploads. Per-turn source attribution is an audit integrity requirement. CEM conversations are stored as working materials — NOT part of formal audit_log. Audit event written only when Lead/Fact/Red Flag is explicitly saved. Model strictly scoped to registered documents only.
**AK decisions locked:** Placement = persistent collapsible chat panel on ALL engagement pages (not standalone page, not tab). Single shared component injected via bootstrap(). Right-edge slide-out panel. Replace CONV-02 standalone page design with shared panel component.
**Gate:** UNBLOCKED — ready to build. Note: CONV-02 design updated — build as `streamlit_app/shared/evidence_chat_panel.py` injected on all pages, not as `14_Evidence_Chat.py`.

```
CONV-01 (EvidenceChat backend) ─── CONV-02
CONV-02 ← CONV-01 + EMB-02-REF
```

- [x] **[CONV-01]** Create `workflows/evidence_chat.py` — DONE Phase F (4315d2a) — `EvidenceChat` class: `chat(case_id: str, message: str, selected_doc_ids: list[str], conversation_history: list[dict]) -> str`. Single Sonnet turn. System prompt: "You are reviewing the documents registered for this forensic engagement. You can only present findings and observations directly supported by the registered documents. For each observation, state the source document and quote the relevant passage. You may explain forensic concepts and fraud patterns as background context. You must not present inferences as conclusions. All observations are preliminary." Context injection per turn (capped at `config.CEM_CONTEXT_CHARS` = 16,000 chars): (1) DocumentIndex summary of all registered docs; (2) key_facts.json and red_flags.json content; (3) `EmbeddingEngine.retrieve(message, case_id, top_k=5)` chunks if embedding available, else `DocumentManager.find_relevant_docs()` excerpt; (4) conversation history (oldest turns dropped first when cap approached). Document-scoped mode: if `selected_doc_ids` is non-empty, retrieval filtered to those doc_ids only. Saves full conversation turn to `D_Working_Papers/evidence_chat_{YYYYMMDD_HHMMSS}.md` on each session_end call (append-only; new CEM session = new file). Auto-save to `evidence_chat_{timestamp}_recovered.md` on mid-session app close. ← deps: EMB-02-REF | AC: `chat(case_id, "What does the bank statement show?", [], [])` returns a non-empty string; system prompt injection confirmed via code inspection; context cap of 16000 chars enforced (verify by unit test with large doc); conversation save creates file in D_Working_Papers/.

- [x] **[CONV-02]** Built as `streamlit_app/shared/evidence_chat_panel.py` per AK locked design decision — DONE Phase F (4315d2a) (or tab within Investigation per UX-D-07 decision — build as standalone page, refactor to tab if AK decides option B post-build). Two-panel layout per UX-014: Left panel (1/3 width) — document selector loaded from `DocumentManager` index for active case (`st.session_state.active_project` or case_id picker if no active project); each document has a checkbox "Include in context"; shows embedding status badge per EMB-03-REF. Right panel (2/3 width) — chat interface: `st.chat_input("Ask about the evidence...")` + `st.chat_message()` rendering (user and assistant). Per assistant response: three action buttons below the message — "Save as Lead" (appends to leads_register.json + audit event), "Save as Key Fact" (appends to key_facts.json), "Save as Red Flag" (severity selectbox appears before saving). "Flag Response" button appends `FLAGGED` annotation to conversation transcript. Persistent banner at top of right panel: `st.warning("Evidence Exploration Mode — outputs are not reviewed deliverables. Use the Investigation pipeline for reviewed reports.")`. Conversation persists across sessions via `cases/{id}/evidence_chat.jsonl` (new file per session). History trimming banner shown when >50 turns: `st.info("Older turns have been trimmed from context. Full transcript saved to Working Papers.")`. "End Conversation" button closes session and triggers conversation save. ← deps: CONV-01, EMB-02-REF | AC: page loads without error when no active case; chat input sends message and renders response; "Save as Lead" button appends to leads_register.json (verify file exists and has entry); "NOT FOR CLIENT REVIEW" equivalent warning banner present; conversation saved to evidence_chat_{timestamp}.md on "End Conversation" click.

---

### Sprint-UX-FIXES — DONE
UX-F-01 through UX-F-07 all completed and merged. See releases/completed-tasks.md.

---

### REFACTOR-01 — Consolidate firm_profile.json + pricing_model.json → firm.json (DO NOT IMPLEMENT NOW)

Roadmap: merge `firm_profile/firm_profile.json` and `firm_profile/pricing_model.json` into
`firm.json` for a single unified config used by both CLI and Streamlit paths.
Priority: LOW. Gate: after P9-07A (Language Standard Settings) lands.

- [ ] REFACTOR-01a Merge pricing fields from pricing_model.json into firm.json
- [ ] REFACTOR-01b Merge firm profile fields from firm_profile.json into firm.json
- [ ] REFACTOR-01c Update CLI setup_wizard.py to read/write firm.json only

---

### Sprint-P9-UI — Phase 9 Engagements UI (Session 024)

**Note:** P9-UI-01 DONE (merged Phase D). P9-UI-02 is next.

- ~~[x] P9-UI-01~~ DONE — pages/01_Engagements.py built Phase D
- [x] **[P9-UI-02]** Wire `engagement_id` / `active_project` into all workflow intake pages — add "Continue Engagement" option at top of intake form on all workflow pages: if `st.session_state.active_project` is set, show `st.info("Continuing engagement: {project_name} — client: {client_name}")` banner and pre-fill `client_name`, `language_standard` from project context; lock those fields (render as `st.text()` not `st.text_input()`). If no `active_project`: existing behavior unchanged (standalone case with UUID, backward compat). Add `engagement_id` to `state.json` at case creation if `active_project` is set. ← deps: P9-UI-01, P9-01-STATE | AC: workflow page with `active_project` set shows pre-filled client name and "Continuing engagement" banner; field is read-only (not editable); without `active_project`, page behaves identically to Phase 8 behavior; `state.json` contains `engagement_id` matching project slug when created via engagement context.

---

### Sprint-SETUP — DONE
SETUP-00 through SETUP-03 all completed and merged. See releases/completed-tasks.md.

---

### Sprint-TEST — Minimum Test Surface (Session 024)

**Note:** TEST-01..04, TEST-05, TEST-06, TEST-07, TEST-07b all DONE.

- [x] **[TEST-05]** `tests/test_project_schema.py` (P9-01-AC) — ProjectIntake slug validation (7-step algorithm), path traversal attempts, empty slug rejection, InputSession lifecycle states, ProjectState health enum. ← deps: TEST-01 | AC: `../../etc/passwd` as project_name raises ValueError; empty string raises ValueError; valid name produces correct slug.

---

### Sprint-KL — Three-Layer Knowledge Architecture (Session 024)

**BA:** BA-KL-01 — CONFIRMED 2026-04-19
**Note:** KL-00 and KL-01 DONE (merged Phase D). KL-02 is next.

- [x] **[KL-02]** Engagement harvest pipeline — `tools/knowledge_harvester.py`: `harvest_case(case_id)` runs after OWNER_APPROVED. Extracts approved patterns to `cases/{id}/knowledge_export/approved_patterns.json`. Promotes to `firm_profile/knowledge/engagement/index.jsonl`. Never extracts client identifiers or raw evidence text. ← deps: KL-01 | AC: harvest_case() on approved case produces approved_patterns.json; file contains no client name, no case_id reference in content fields; audit event written.

- [ ] **[KL-02b]** Expand harvest trigger to DELIVERABLE_WRITTEN (AK decision 2026-04-23) — currently `harvest_case()` only fires at `OWNER_APPROVED`. Update the post-hook in `core/hooks/post_hooks.py` (or wherever the OWNER_APPROVED trigger lives) to also call `KnowledgeHarvester.harvest_case(case_id)` when `new_status == CaseStatus.DELIVERABLE_WRITTEN`. Applies to both Streamlit pipeline and CLI pipeline paths. Guard: only harvest if `approved_patterns.json` does not already exist for this case_id (idempotent — do not harvest twice). ← deps: KL-02 | AC: (1) pipeline that ends at DELIVERABLE_WRITTEN (Mode B workflows: Policy/SOP, Proposal, Training) produces `approved_patterns.json` — verify by running a policy workflow and checking `cases/{id}/knowledge_export/`; (2) running the same case twice does not produce duplicate entries in `firm_profile/knowledge/engagement/index.jsonl` — idempotency check; (3) OWNER_APPROVED path still works unchanged — regression check on existing KL-02 AC.

---

### Sprint-ACT — Activity Ledger (Session 024)

**BA:** BA-ACT-01 — CONFIRMED 2026-04-19
**Note:** ACT-00 and ACT-01 DONE (merged Phase D). ACT-02 and ACT-03 are next.

- [x] **[ACT-02]** Wire ActivityLogger into bootstrap() and all pipeline on_progress callbacks — SESSION/PIPELINE events. Wire into 00_Setup.py — SETUP events. Wire into file_tools.py write_artifact() — DOCUMENT/DELIVERABLE events. Wire into settings pages — SETTINGS events. ← deps: ACT-01, SETUP-03 | AC: running a pipeline end-to-end produces ≥5 activity events in logs/activity.jsonl covering SESSION, PIPELINE, DELIVERABLE categories; settings change produces SETTINGS event with old_value + new_value fields.
- [x] **[ACT-03]** Create `pages/07_Activity_Log.py` — per UX-020. (Built as 15_Activity_Log.py — 07 conflicts with existing 07_Proposal.py) Date range picker + category multiselect + free-text search. Paginated 50 events per page. Export as CSV button. Sidebar warning if `st.session_state.get("act_log_warn")` is True. ← deps: ACT-01 | AC: page renders with empty log (shows "No activity recorded yet"); date filter correctly narrows events; category filter works independently and in combination with date; CSV export produces valid file with all visible events; corrupt log file shows error message, does not crash.

---


## Sprint-SIM (Simulation Findings — auto-generated)

| ID | Severity | Source | Description | Effort | Status |
|----|----------|--------|-------------|--------|--------|
| SIM-01 [CONFIRMED_EMPIRICAL] | HIGH | Monte Carlo | investigation_report: success_rate=54.4%, top failure=NO_CITATIONS | M | OPEN |
| SIM-02 [CONFIRMED_EMPIRICAL] | HIGH | Monte Carlo | frm_risk_register: success_rate=57.2%, top failure=MAX_TURNS | M | OPEN |
| SIM-03 | MEDIUM | Monte Carlo | persona_review: success_rate=74.4%, top failure=SCHEMA_VALIDATION | M | OPEN |
| SIM-04 [CONFIRMED_EMPIRICAL] | HIGH | Game Theory | B: Information Asymmetry (PM over-approves): Partner rejection rate 46.4% — no recovery path (Pipeli | L | OPEN |
| SIM-05 [CONFIRMED_EMPIRICAL] | HIGH | Fuzz | description/text_pii: PII value passed through sanitize_pii unchanged | S | OPEN |
| SIM-06 [CONFIRMED_EMPIRICAL] | HIGH | Fuzz | description/text_pii: PII value passed through sanitize_pii unchanged | S | OPEN |
| SIM-07 [CONFIRMED_EMPIRICAL] | HIGH | Fuzz | description/text_pii: PII value passed through sanitize_pii unchanged | S | OPEN |
| SIM-08 [CONFIRMED_EMPIRICAL] | HIGH | Fuzz | description/text_pii: PII value passed through sanitize_pii unchanged | S | OPEN |
| SIM-09 [CONFIRMED_EMPIRICAL] | HIGH | Fuzz | description/text_pii: PII value passed through sanitize_pii unchanged | S | OPEN |
| SIM-10 [CONFIRMED_EMPIRICAL] | HIGH | Fuzz | description/text_pii: PII value passed through sanitize_pii unchanged | S | OPEN |
| SIM-11 [CONFIRMED_EMPIRICAL] | HIGH | Fuzz | description/text_pii: PII value passed through sanitize_pii unchanged | S | OPEN |
| SIM-12 [CONFIRMED_EMPIRICAL] | HIGH | Fuzz | description/text_pii: PII value passed through sanitize_pii unchanged | S | OPEN |
| SIM-13 [CONFIRMED_EMPIRICAL] | HIGH | Fuzz | description/text_pii: PII value passed through sanitize_pii unchanged | S | OPEN |
| SIM-14 [CONFIRMED_EMPIRICAL] | HIGH | Fuzz | description/text_pii: PII value passed through sanitize_pii unchanged | S | OPEN |
| SIM-15 | MEDIUM | Conflict/session_state_collision | Key 'active_project' referenced in 4 pages: 01_Engagements.py, 06_FRM.py, 12_Case_Tracker.py, 16_Wor | S | OPEN |
| SIM-16 | MEDIUM | Conflict/hook_ordering | persist_artifact (hook N) fires BEFORE extract_citations (hook N+1). If citation extraction fails (e | S | OPEN |
| SIM-17 | MEDIUM | Conflict/state_machine_reachability | States unreachable from INTAKE_CREATED: pipeline_error. These states can never be entered via valid  | S | OPEN |


## Sprint-FUT (Future-Direction Simulation Findings — auto-generated)

| ID | Priority | Area | Description | Effort | Sprint | Status |
|----|----------|------|-------------|--------|--------|--------|
| FUT-01 | P1 | pii | Add UAE IBAN regex to sanitize_pii (AE07... pattern confirmed bypassed) | S | Sprint-SIM | DONE |
| FUT-02 | P1 | pii | Strip null bytes (\x00..\x02) from free-text fields in sanitize_pii | S | Sprint-SIM | DONE |
| FUT-03 | P1 | schema | Add ge=1, le=5 validators to RiskItem.likelihood and RiskItem.impact — 0 and 6 both accepted by Pyda | S | Sprint-SIM | DONE |
| FUT-04 | P1 | orchestrator | Thread pm_feedback into Junior context on revision runs — confirmed missing: feedback_in_context=Non | M | Sprint-SIM | DONE |
| FUT-05 | P2 | schema | Add min_length=1 to JuniorDraft.findings list — empty findings accepted today | S | Sprint-SIM | DONE |
| FUT-06 | P2 | orchestrator | Add Partner→PM feedback recovery path — human decision gate with in-app review | L | Sprint-SIM | DONE |
| FUT-07 | P2 | hook | enforce_evidence_chain root cause resolved — reads evidence_items from output fallback | M | Sprint-SIM | DONE |
| FUT-09 | P1 | future_workflow | multi_tenant_workstream: CRITICAL — success_rate=14.2%, top failure=MAX_TURNS | L | Sprint-IA-01/02 | OPEN |
| FUT-10 | P1 | future_workflow | expert_witness_report: CRITICAL — success_rate=24.8%, top failure=PIPELINE_ERROR | L | Sprint-IA-01/02 | OPEN |
| FUT-11 | P1 | future_workflow | custom_investigation: CRITICAL — success_rate=27.6%, top failure=PIPELINE_ERROR | L | Sprint-IA-01/02 | OPEN |
| FUT-12 | P1 | future_workflow | frm_guided_exercise: CRITICAL — success_rate=28.6%, top failure=PIPELINE_ERROR | L | Sprint-IA-01/02 | OPEN |
| FUT-13 | P1 | future_workflow | aup_investigation: CRITICAL — success_rate=31.6%, top failure=PIPELINE_ERROR | L | Sprint-IA-01/02 | OPEN |
| FUT-14 | P2 | future_workflow | co_work_session: HIGH — success_rate=58.0%, top failure=PIPELINE_ERROR | M | Sprint-IA-01/02 | OPEN |
| FUT-15 | P2 | future_workflow | evidence_chat_session: HIGH — success_rate=58.0%, top failure=PIPELINE_ERROR | M | Sprint-IA-01/02 | OPEN |
| FUT-16 | P2 | future_workflow | knowledge_harvester: HIGH — success_rate=61.8%, top failure=HOOK_VETO_POST | M | Sprint-IA-01/02 | OPEN |
| FUT-17 | P2 | future_workflow | workpaper_promotion: HIGH — success_rate=66.8%, top failure=PIPELINE_ERROR | M | Sprint-IA-01/02 | OPEN |
| FUT-18 | P2 | future_workflow | app_bootstrap: HIGH — success_rate=67.0%, top failure=PIPELINE_ERROR | M | Sprint-IA-01/02 | OPEN |
| FUT-19 | P2 | slug | Artifact filenames appear to be named by agent + version only (e.g. junior_output.v1.json). When two | M | Sprint-IA-01 IA-03 | OPEN |
| FUT-20 | P1 | bootstrap | app.py calls bootstrap() without a try/except wrapper. If bootstrap() raises (missing firm_profile/, | M | Sprint-IA-01 IA-01 | DONE |
| FUT-21 | P1 | bootstrap | 00_Setup.py calls bootstrap() AND app.py calls bootstrap(). CLOSED — 00_Setup.py does NOT call bootstrap; no circular redirect risk. | M | Sprint-IA-01 IA-01 | CLOSED |
| FUT-22 | P2 | template | templates/ directory exists but contains no .docx files. Any workflow that calls python-docx with a  | M | Sprint-IA-02 | OPEN |
| FUT-23 | P1 | locking | No file locking primitives found in orchestrator.py or tools/file_tools.py. Current atomic write use | M | Sprint-IA-02 (co-work / shipping models 3+) | OPEN |
| FUT-25 | P2 | future_design | evidence_chat_session: cap CEM context at 50 turns with explicit truncation warning (CEM_CONTEXT_CHA | S | Sprint-IA-02 (CEM) | OPEN |
| FUT-26 | P2 | future_design | workpaper_promotion: require audit_log.jsonl to exist before promotion — surface friendly error on m | S | Sprint-IA-01 | OPEN |
| FUT-27 | P2 | future_design | knowledge_harvester: implement PII filter (client names, case IDs, financial amounts) as a mandatory | M | Sprint-IA-02 (future) | OPEN |
