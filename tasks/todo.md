# TODO

## SESSION STATE
Status:         OPEN
Active task:    none
Active persona: qa
Blocking issue: none
Last updated:   2026-04-18T05:55:30Z — state transition by MCP server

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
```

Completed tasks archived in: releases/completed-tasks.md
Sprint-01, Sprint-02, QR-01..16, Sprint-03 (completed), Sprint-04 AKR, Sprint-06, Sprint-09, Sprint-10A, Sprint-10B, Sprint-10B-KQ, Sprint-10E, Sprint-10H, Sprint-10F — all DONE, see releases/completed-tasks.md.

---

## PENDING TASKS

---

### Sprint-10I — P7-GATE Unblock: Research Mode Flag (PRIORITY: IMMEDIATE)

**Context:** Tavily API unreachable in current env. `timeout=_TIMEOUT` kwarg is silently ignored by the
Tavily SDK — each retry attempt waits the full 60s default. 3 attempts × 60s = 3+ min hang before graceful
fallback. User terminates terminal before fallback fires. Fix: add `RESEARCH_MODE` flag; when
`knowledge_only`, skip all Tavily calls immediately. No network, no hang. Pipeline runs on model knowledge.

**Constraint:** `RESEARCH_MODE=knowledge_only` is the DEFAULT. Set `RESEARCH_MODE=live` in .env to re-enable
Tavily. This ensures demo/dev never requires external connectivity.

**Security model:**
- Auth: N/A (local CLI, no auth layer)
- Data boundaries: no change — research results stay within local case folder
- PII: no change — same sanitisation hooks apply
- Audit: no new events required; research_mode is logged in existing agent context
- Abuse surface: stub returns fixed string — no injection surface

- [x] BUG-09a `config.py` — DONE
- [x] BUG-09b `tools/research/general_search.py` — DONE
- [x] BUG-09c `tools/research/regulatory_lookup.py` — DONE
- [x] BUG-09d `tools/research/sanctions_check.py` — DONE
- [x] BUG-09e `tools/research/company_lookup.py` — DONE

**After BUG-09:** Run P7-GATE → `python run.py` → Option 6 → complete FRM workflow → verify `final_report.en.md` written, `audit_log.jsonl` populated, `state.json = OWNER_APPROVED`.

---

### AKR-08b — docs/hld.md architect session [P2, human-input-required]

- [ ] AKR-08b Run /architect session: populate docs/hld.md gaps + draft docs/lld/ files per feature.
      PARTIAL: hld.md derived from CLAUDE.md; gaps marked [TO VERIFY VIA /architect SESSION]. Full session pending.

---

### Sprint-03 — Proposal + PPT QA Gate (NOT YET RUN)

Proposal workflow (Option 7) and PPT pack (Option 8) implemented in sprint-02 but never QA'd.

- [ ] PQA-01 Firm profile setup — confirm pricing_model.json, team.json, firm_profile.json written correctly; confirm loaded in _load_pricing()
- [ ] PQA-02 Proposal intake → _persist_intake() → intake.json + state.json written
- [ ] PQA-03 _select_team() — Haiku selects relevant members; fallback to team[:4] if API error
- [ ] PQA-04 _generate_proposal() — Sonnet returns 7-section markdown; check all sections present
- [ ] PQA-05 proposal.docx generated via OutputGenerator; graceful skip if python-docx missing
- [ ] PQA-06 PPT chain prompt — user offered deck after proposal; both paths (Y/N) work
- [ ] PQA-07 Standalone Option 8 — run_proposal_deck_workflow() with all 6 audience types
- [ ] PQA-08 DeckStoryboard validates against schema (case_id, slides[], open_questions)
- [ ] PQA-09 Per-slide files written: slide_01_prompt.md .. slide_NN_prompt.md
- [ ] PQA-10 deck_master_prompt.v1.md written with system prompt + step prompts
- [ ] PQA-11 Fallback storyboard returned if Sonnet JSON parse fails (open_questions flag set)
- [ ] PQA-12 case_tracker (Option 9) discovers PROP-XXXX cases via intake.json

---

### Sprint-03 — Pricing Model Gap

ISSUE: run_firm_profile_setup() is only triggered once. If user skips it, _load_pricing() returns
silent fallback {model:daily, currency:AED, rates:{}} — fee section generates blank.

- [ ] PGP-01 Add pricing completeness check in run_client_proposal_workflow(): if rates all empty, warn and offer to run firm profile setup inline
- [ ] PGP-02 Add pricing review step: show loaded rates before drafting; allow inline override without touching firm_profile/

---

### Sprint-03 — Open Codex Findings

#### C-01b — Upgrade client_proposal to orchestrated path (Medium)
Files: workflows/client_proposal.py

- [ ] C-01b Move client_proposal onto orchestrated path (Junior draft → PM review → Partner sign-off). Higher effort; closes quality gap for highest-value workflow.

#### C-04c / QR-17 — Document ingestion smoke test (Low, gated on API key)
Files: tools/document_manager.py, run.py

- [ ] QR-17 / C-04c Document ingestion path: _offer_document_ingestion() / _run_document_ingestion() → register_document() → document_index.json written → read_excerpt() returns ≤8k chars. GATED on live API key.

#### C-06 — Integration tests (Low)

- [ ] C-06a Integration test: investigation_report happy path (mocked API)
- [ ] C-06b Integration test: FRM multi-module run (modules 1, 2, 3 with dependency enforcement)
- [ ] C-06c Integration test: interrupted resume — write partial state.json, restart, verify orchestrator offers resume
- [ ] C-06d Integration test: document ingestion → read_excerpt → agent receives bounded content
- [ ] C-06e Integration test: persona review against a saved case folder

---

### Frontend Migration — Streamlit (Decision: Option A confirmed)

- [ ] FE-01 Replace ui/ terminal components with Streamlit pages
- [ ] FE-02 Conversational intake → Streamlit multi-step form per workflow
- [ ] FE-03 Pipeline progress → Streamlit spinner + status text (replaces CLI spinner that collides with input prompts — confirmed UX bug in P7-GATE test)
- [ ] FE-04 Output display → Streamlit markdown render + file download buttons
- [ ] FE-05 Firm profile setup → Streamlit settings page (replaces terminal wizard)
- [ ] FE-06 Case tracker → Streamlit table with case status + open/download links
- [ ] FE-07 Risk item review → Streamlit card per item with A/F/R buttons (replaces hidden CLI prompt — confirmed UX bug in P7-GATE test)
- [ ] FE-08 Case folder UX — final deliverables surfaced prominently; interim artifacts (*.v{N}.json, pm_review, junior_output) moved to cases/{id}/interim/ subfolder; only final_report.* and audit_log.jsonl in root
- [ ] FE-09 Word document design — apply firm branding template (logo, fonts, header/footer) to all .docx outputs; requires firm_profile/template.docx as base template loaded by file_tools.py
- [ ] FE-10 FRM Risk Register — Excel output (.xlsx) — **BLOCKED: MISSING_BA_SIGNOFF** — no BA entry for Excel as required output format; needs /ba session before build
- [ ] FE-11 FRM Risk Register — two-tier risk structure (Design-Level vs Operational-Level) — **BLOCKED: MISSING_BA_SIGNOFF** — no BA entry for tier taxonomy or schema change to RiskItem; needs /ba session before build

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

- [x] P7-GATE Run `python run.py` with live API keys — PASSED Session 015 (knowledge_only mode, 2 FRM modules, no crash, final_report.en.md written)
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

### Phase 8 — Streamlit Frontend Migration (Session 016 — Corrected Plan)

**Design authority:** Architect Session 016. Supersedes P8-01..06 from prior stub plan.
**CLI stays intact:** `run.py` unchanged. Streamlit is an additive layer only.
**Security model:** local localhost:8501 only; all data stays in cases/ and firm_profile/; same hooks/sanitisation chain applies; no new audit events required.

**Ultraplan corrections applied:**
- P8-00-EXTRACT is a hard prerequisite for all page tasks (missing from ultraplan)
- FE-09 fix is in `tools/file_tools.py:150`, not `tools/output_generator.py` (template support already exists in output_generator)
- FE-08: post-run migration preferred over `interim=True` flag (version counter gap in next_version())
- Review loop expanded to all modules in Streamlit (aligns with BA-002 Step 5 — Module 2-only was a CLI shortcut, not a requirement)
- FE-10, FE-11: BLOCKED pending BA sign-off

```
PHASE 8 DEPENDENCY GRAPH:
P8-00-EXTRACT ─────────────────────────────── P8-03-SHARED, P8-06-FRM, P8-08-PAGES
P8-01 (requirements.txt)  ── no deps, trivial
P8-02-SPLIT (FRM workflow) ─────────────────── P8-06-FRM
P8-03-SHARED ← P8-00-EXTRACT ───────────────── P8-04-APP, P8-06-FRM, P8-08-PAGES, P8-09-TRACKER, P8-10-SETTINGS
P8-04-APP ← P8-03-SHARED ───────────────────── P8-14-SMOKE
P8-05-FE08 (interim folder) ── no deps ──────── P8-14-SMOKE
P8-06-FRM ← P8-02-SPLIT + P8-03-SHARED ─────── P8-14-SMOKE
P8-07-FE09 (docx branding) ── no deps ──────── P8-14-SMOKE
ARCH-INS-01 ← P8-03-SHARED ─────────────────── P8-08-PAGES
ARCH-INS-02 ← write_state() ────────────────── P8-09-TRACKER
P8-08-PAGES ← P8-03-SHARED + ARCH-INS-01 ──── P8-11-DOCIN, P8-14-SMOKE
P8-09-TRACKER ← P8-03-SHARED + ARCH-INS-02 ── P8-14-SMOKE
P8-10-SETTINGS ← P8-03-SHARED ─────────────── P8-14-SMOKE
P8-11-DOCIN ← P8-08-PAGES ─────────────────── P8-14-SMOKE
P8-12-EXCEL — BLOCKED: MISSING_BA_SIGNOFF
P8-13-TIER  — BLOCKED: MISSING_BA_SIGNOFF
P8-14-SMOKE ← all above
```

---

#### P8-00-EXTRACT — Extract _mark_deliverable_written() from run.py [PREREQUISITE]
**Files:** `run.py`, `tools/file_tools.py`
**Why:** Defined at `run.py:423` — Streamlit pages cannot import from run.py. All page completions need this to advance state to DELIVERABLE_WRITTEN. Must be extracted to `tools/file_tools.py` first.
**Change:** Move function body to `file_tools.py`; `run.py` imports it from there. No behaviour change.

- [x] P8-00a Move `_mark_deliverable_written()` from `run.py:423` to `tools/file_tools.py` as `mark_deliverable_written(case_id, workflow)`
- [x] P8-00b Update `run.py` to import from `tools.file_tools` (shim kept for existing call sites)
- [ ] P8-00c Verify CLI smoke: `python run.py` Option 6 still advances state after completion — MANUAL, requires AK + API key

---

#### P8-01 — Add streamlit to requirements.txt
**File:** `requirements.txt`

- [x] P8-01a Add `streamlit>=1.32.0` to requirements.txt

---

#### P8-02-SPLIT — FRM workflow split: run_frm_pipeline + run_frm_finalize
**File:** `workflows/frm_risk_register.py`
**Gate for:** P8-06-FRM
**Constraint:** `run_frm_workflow()` signature and behaviour unchanged — CLI regression must be zero.
**Behavioral note:** Review loop currently fires for Module 2 only (line 153). `run_frm_pipeline()` returns all modules' risk items unreviewed. Streamlit page applies A/F/R to all items — aligns with BA-002 Step 5. CLI retains Module 2-only review loop inside `run_frm_workflow()`.

- [x] P8-02a Extract pipeline body into `run_frm_pipeline()` — returns (risk_items, citations, completed_modules, exec_summary)
- [x] P8-02b Create `run_frm_finalize()` — assembles deliverable, writes report, calls mark_deliverable_written
- [x] P8-02c Keep `run_frm_workflow()` intact — signature unchanged, verified by import test
- [ ] P8-02d Verify CLI: `python run.py` Option 6 produces identical output to pre-split — MANUAL, requires AK + API key

---

#### P8-03-SHARED — streamlit_app/shared/ utilities
**New files:** `streamlit_app/shared/session.py`, `streamlit_app/shared/intake.py`, `streamlit_app/shared/pipeline.py`
**Deps:** P8-00-EXTRACT

- [x] P8-03a `session.py` — `bootstrap(st)` written; idempotent session init
- [x] P8-03b `intake.py` — `generic_intake_form()` + `frm_intake_form()` with module dep validation and st.warning
- [x] P8-03c `pipeline.py` — `run_in_status()` with live log via st.empty().text()

---

#### P8-04-APP — app.py entry point
**New file:** `app.py`
**Deps:** P8-03-SHARED

- [x] P8-04a Create `app.py` — st.set_page_config, firm name header, RESEARCH_MODE banner, landing screen

---

#### P8-05-FE08 — Case folder interim restructure
**File:** `tools/file_tools.py` — `write_final_report()` only
**Approach:** Post-run migration (not `interim=True` flag — version counter in `next_version()` scans root only; adding interim/ routing would silently reset version counters)

- [x] P8-05a Post-run migration added to `write_final_report()` — shutil.move() for *.v*.json → interim/; FE-09 template_path fix included in same change
- [ ] P8-05b Verify interim folder structure after live run — MANUAL, requires AK + API key

---

#### P8-06-FRM — pages/6_FRM.py (highest priority — fixes FE-07)
**New file:** `pages/6_FRM.py`
**Deps:** P8-02-SPLIT, P8-03-SHARED, P8-00-EXTRACT
**Stage machine:** `st.session_state["frm_stage"]` ∈ {intake, running, reviewing, done}

- [x] P8-06a Intake stage: frm_intake_form() wired; module dep validation with st.warning
- [x] P8-06b Running stage: run_in_status() calling run_frm_pipeline(); result in session_state
- [x] P8-06c Reviewing stage: st.expander per RiskItem; A/F/R selectbox + note; all modules (not Module 2 only)
- [x] P8-06d Done stage: run_frm_finalize() with reviewed items; st.download_button; mark_deliverable_written called
- [ ] P8-06e Verify: FRM end-to-end in Streamlit — A/F/R visible and clickable — MANUAL, requires AK + streamlit run

---

#### P8-07-FE09 — Word doc branding fix
**File:** `tools/file_tools.py:150` (NOT output_generator.py — template support already exists there at lines 35-38)
**Note:** `generate_docx()` already accepts `template_path` and uses it. The bug is that `write_final_report()` calls it without passing the path.

- [x] P8-07a Completed as part of P8-05a — template_path check added to write_final_report() in same change

---

#### ARCH-INS-01 — Severity-tagged pipeline events (PREREQUISITE for P8-08)
**File:** `streamlit_app/shared/pipeline.py`
**Deps:** P8-03-SHARED
**Why:** Inspired by Transplant CRITICAL/WARNING/INFO severity model. `run_in_status()` currently emits flat text — consultant cannot distinguish a normal progress line from PM flagging empty findings. Severity tagging fixes this before all 10 workflow pages are built on top of it.
**Security model:** No auth/PII/audit changes. Severity is display-only. No injection surface — severity values are an enum, not user input.

- [x] INS-01a Define `PipelineEvent` dataclass in `streamlit_app/shared/pipeline.py` — fields: `severity: Literal["CRITICAL","WARNING","INFO"]`, `message: str`, `agent: str`
- [x] INS-01b Update `run_in_status()` to render `st.error()` for CRITICAL, `st.warning()` for WARNING, `st.info()` for INFO. Existing flat text log replaced by severity-aware rendering.
- [x] INS-01c Wire severity into `run_frm_pipeline()` call site in `pages/6_FRM.py` — empty findings list → CRITICAL; knowledge_only mode active → WARNING; normal agent progress → INFO.

**Status: QA_APPROVED**

#### AC — ARCH-INS-01

**INS-01a — PipelineEvent dataclass**
- [ ] `PipelineEvent` is importable from `streamlit_app/shared/pipeline.py` with no import errors
- [ ] Dataclass has exactly three fields: `severity: Literal["CRITICAL","WARNING","INFO"]`, `message: str`, `agent: str`
- [ ] `PipelineEvent(severity="INVALID", message="x", agent="junior")` raises `ValueError` or `TypeError` (Literal enforcement must be active — use Pydantic or explicit `__post_init__` guard)
- [ ] Constructing with `severity` omitted raises `TypeError` — no default value
- [ ] `PipelineEvent(severity="INFO", message="", agent="junior")` is accepted — empty message valid at dataclass level

**INS-01b — run_in_status() severity rendering**
- [ ] `run_in_status()` accepts `PipelineEvent` objects — flat-string path removed, not left as a parallel branch
- [ ] `severity="CRITICAL"` → rendered via `st.error()` (code inspection: call contains `st.error(...)`)
- [ ] `severity="WARNING"` → rendered via `st.warning()`
- [ ] `severity="INFO"` → rendered via `st.info()`
- [ ] No bare `st.text()` or `st.write()` calls remain in `run_in_status()` for log lines
- [ ] Any callers of `run_in_status()` outside `pages/6_FRM.py` either migrated or do not crash (no silent breakage of other pages)

**INS-01c — FRM page severity wiring**
- [ ] `pages/6_FRM.py` Stage 2 passes `PipelineEvent` objects to `run_in_status()` — not raw strings
- [ ] Zero risk items returned → at least one `CRITICAL` event emitted → `st.error()` visible in Stage 2 (per UX-002 Stage 2)
- [ ] `config.RESEARCH_MODE == "knowledge_only"` → at least one `WARNING` event emitted at pipeline start (per UX-002 Stage 2 knowledge_only banner requirement)
- [ ] Normal agent progress (Junior, PM, Partner steps) → `INFO` events → rendered as `st.info()`
- [ ] Severity values sourced from `PipelineEvent` Literal — no bare `"CRITICAL"` / `"WARNING"` string literals scattered in the page file

**Security**
- [ ] `PipelineEvent.message` populated only from agent status strings or fixed constants — not raw user input or unescaped model output (no injection surface)
- [ ] No new files written, no audit events added — severity is display-only (per task security model)

**Auth:** N/A — local CLI tool, no auth layer

---

#### P8-08-PAGES — Remaining workflow pages
**New files:** 10 pages (listed below)
**Deps:** P8-03-SHARED, P8-00-EXTRACT, ARCH-INS-01
**Pattern:** `bootstrap(st)` → `generic_intake_form()` → `run_in_status(workflow_fn)` → `st.download_button`

- [x] P8-08a `pages/2_Investigation.py` — `run_investigation_workflow`
- [x] P8-08b `pages/3_Persona_Review.py` — `run_persona_review_workflow`
- [x] P8-08c `pages/4_Policy_SOP.py` — `run_policy_sop_workflow`
- [x] P8-08d `pages/5_Training.py` — `run_training_material_workflow`
- [x] P8-08e `pages/7_Proposal.py` — `run_client_proposal_workflow`; post-run `st.checkbox` "Also generate PPT prompt pack?" chains to Option 8
- [x] P8-08f `pages/8_PPT_Pack.py` — `run_proposal_deck_workflow`
- [x] P8-08g `pages/0_Scope.py` — `run_engagement_scoping_workflow`
- [x] P8-08h `pages/11_Due_Diligence.py` — `run_due_diligence_workflow`
- [x] P8-08i `pages/12_Sanctions.py` — `run_sanctions_screening_workflow`; must render red warning panel when `RESEARCH_MODE=knowledge_only` before allowing workflow to run (mirrors CLI PPH-02 behaviour)
- [x] P8-08j `pages/13_Transaction_Testing.py` — `run_transaction_testing_workflow`

**Status: QA_APPROVED**

#### AC — P8-08-PAGES

All 10 pages follow UX-003 shell (Zone A → B → C). AC is written as a shared pattern + per-page overrides.

**Shell pattern (applies to all 10 pages)**
- [ ] All 10 page files importable with no errors (`python3 -c "import pages.2_Investigation"` etc.)
- [ ] Each page calls `bootstrap(st)` at module level — RESEARCH_MODE banner rendered on every page
- [ ] `generic_intake_form()` used in Zone A — no bespoke form fields built inline
- [ ] "Run [Workflow Name]" submit button uses `type="primary"` — renders in brand red (#D50032) per design system
- [ ] Submit button disabled (greyed) while pipeline is running — user cannot double-submit
- [ ] Zone A collapses to a closed `st.expander("Intake Summary")` when pipeline starts (UX-D-01 approved) — intake data visible but not editable during run
- [ ] `run_in_status()` used for pipeline execution — severity-tagged log (ARCH-INS-01 dependency satisfied)
- [ ] Pipeline error → `st.error("Pipeline failed: [message]")` + "Start Over" button that resets to Zone A
- [ ] Empty output (workflow returns None or empty) → `st.warning("No output was generated...")` in Zone C — not a blank page
- [ ] Success → `st.success()` banner + case ID chip + `st.download_button()` for the deliverable file
- [ ] "Start New Case" button resets page state: clears client/intake fields, keeps firm name pre-filled (UX-D-03 approved)
- [ ] No hardcoded workflow names, case IDs, or file paths as string literals — all derived from intake or pipeline return values

**Page-specific overrides**

- [ ] P8-08e (`pages/7_Proposal.py`): after success, `st.checkbox("Also generate PPT prompt pack for this engagement?")` renders — if checked, invokes PPT Pack workflow with same case_id (UX-003 Proposal-specific addition)
- [ ] P8-08i (`pages/12_Sanctions.py`): if `config.RESEARCH_MODE == "knowledge_only"`, `st.error()` warning panel renders BEFORE the intake form with message about live screening unavailability; `st.checkbox("I understand this is not a live screening — proceed anyway.")` required; Run button disabled until checkbox is ticked (UX-003 Sanctions-specific override)
- [ ] P8-08i: Run button remains disabled if knowledge_only checkbox is NOT ticked — verified by code inspection (`disabled=not st.session_state.get(...)` pattern or equivalent)

**Mobile (375px) — per UX-003**
- [ ] No multi-column layouts used in any page (`st.columns()` not called at page level) — Streamlit single-column on mobile is the default; verified by code inspection

**Security**
- [ ] No `st.text_input()` values passed directly into shell commands, file paths, or SQL — all intake data flows only into workflow function arguments
- [ ] No secrets, API keys, or firm_profile credentials rendered to the page via `st.write()` or `st.markdown()`
- [ ] `run_in_status()` `on_progress` messages sourced from pipeline constants only — not echoed user input (injection surface check, inherited from ARCH-INS-01)

**Auth:** N/A — local localhost:8501, no auth layer

---

#### ARCH-INS-02 — Materialized case index (PREREQUISITE for P8-09-TRACKER)
**Files:** `tools/file_tools.py`, `write_state()`
**Why:** Inspired by Transplant read-model / CQRS pattern. Case Tracker scanning `cases/*/state.json` at runtime is O(n) directory reads. With 50+ cases this is slow and fragile. A write-through index (`cases/index.json`) updated on every state transition makes tracker load instant.
**Security model:** No auth/PII changes. `cases/index.json` contains no PHI — only case_id, workflow, status, last_updated. Atomic write via existing `os.replace()` pattern in `file_tools.py`.

- [x] INS-02a Add `_update_case_index(case_id, workflow, status, last_updated)` to `tools/file_tools.py` — reads `cases/index.json` (creates if missing), upserts entry by case_id, writes atomically via `.tmp` → `os.replace()`.
- [x] INS-02b Call `_update_case_index()` at end of `write_state()` — fires on every state transition automatically.
- [x] INS-02c Backfill helper: on first load, if `cases/index.json` missing, scan `cases/*/state.json` once to build it. Subsequent loads use index only.

**Status: QA_APPROVED**

#### AC — ARCH-INS-02

**INS-02a — _update_case_index function**
- [ ] `_update_case_index` is importable from `tools/file_tools.py` with no import errors
- [ ] Calling `_update_case_index("CASE-001", "frm_risk_register", "OWNER_APPROVED", "2026-04-17T00:00:00Z")` when `cases/index.json` does not exist creates the file (no FileNotFoundError)
- [ ] Index entry has exactly 4 fields: `case_id`, `workflow`, `status`, `last_updated` — no PHI, no client name, no case content
- [ ] Calling twice with the same `case_id` upserts — resulting index has exactly one entry for that case_id, not two
- [ ] Write is atomic: a `.tmp` file is created and `os.replace()` is used — verifiable by code inspection (pattern matches `write_artifact()` in same file)
- [ ] Calling with a different `case_id` appends a second entry — index grows to 2 entries
- [ ] If `cases/index.json` is corrupt JSON, function raises a clear exception rather than silently overwriting with partial data

**INS-02b — write_state() integration**
- [ ] `write_state()` function signature is unchanged: `(case_id: str, state: dict) -> Path` — all existing callers unaffected
- [ ] After `write_state()` completes, `cases/index.json` is updated with the case's current `workflow`, `status`, and `last_updated` extracted from the state dict
- [ ] `_update_case_index()` failure (e.g., index file locked) does NOT silently swallow the error — either propagates or logs a warning; `state.json` write must already have succeeded before index update is attempted
- [ ] `write_state()` still writes `state.json` atomically regardless of whether `_update_case_index()` is called — primary write is never skipped

**INS-02c — Backfill helper**
- [ ] A public function `build_case_index()` (or equivalent) exists and is importable from `tools/file_tools.py`
- [ ] Calling `build_case_index()` when `cases/index.json` is absent but `cases/*/state.json` files exist → creates `cases/index.json` with one entry per scanned case
- [ ] Calling `build_case_index()` when `cases/` is empty (no case subdirs) → creates `cases/index.json` with an empty list `[]` (not a missing file, not an error)
- [ ] Calling `build_case_index()` twice produces identical output (idempotent)
- [ ] `state.json` files missing `workflow` or `status` keys are skipped without crashing — backfill continues with remaining cases

**Security**
- [ ] `cases/index.json` entries contain only `case_id`, `workflow`, `status`, `last_updated` — confirmed by code inspection (no `client_name`, `intake`, or document content written to index)
- [ ] Atomic write in `_update_case_index()` uses `.tmp` → `os.replace()` — a process kill mid-write leaves `.tmp` (recoverable), not a corrupt `index.json`

**Auth:** N/A — local CLI tool, no auth layer
**Mobile:** N/A — no UI components in this task

---

#### P8-09-TRACKER — pages/9_Case_Tracker.py
**New file:** `pages/9_Case_Tracker.py`
**Deps:** P8-03-SHARED, ARCH-INS-02

- [x] P8-09a Read `cases/index.json` (not directory scan) → build dataframe (case_id, workflow, status, date). `st.dataframe()` with click-to-expand: shows deliverables, audit_log link, download final_report button. **QA_APPROVED Session 020**

#### AC — P8-09a

**Data loading**
- [ ] Page shows `st.spinner("Loading cases...")` while reading `cases/index.json` — spinner visible before table renders (UX-004 loading state)
- [ ] Page reads `cases/index.json` — no `os.listdir()` / `glob("cases/*/")` directory scan at runtime (code inspection: only `_INDEX_PATH.read_text()` or `json.load(open(_INDEX_PATH))` pattern permitted)
- [ ] If `cases/index.json` exists → `st.dataframe()` renders with columns: Case ID | Workflow | Status | Last Updated — sorted by Last Updated descending (newest first)
- [ ] If `cases/index.json` is absent AND `cases/` directory is empty (or no `state.json` files exist) → `st.info("No cases yet. Run a workflow to create your first case.")` — no error, no blank page
- [ ] If `cases/index.json` is absent BUT `cases/*/state.json` files exist → `build_case_index()` called to backfill, then table renders; `st.warning("Case index rebuilt from folder scan.")` shown
- [ ] "Refresh" button re-reads `cases/index.json` without full page reload (`st.rerun()` or equivalent)

**Table display**
- [ ] `st.dataframe()` used (not `st.table()` or raw HTML) — importable via code inspection
- [ ] Workflow column displays human-readable label (e.g. "FRM Risk Register" not "frm_risk_register") — either via format_func or rename dict applied before render
- [ ] `DELIVERABLE_WRITTEN` and `OWNER_APPROVED` status values map to a green visual indicator in the table (column value, emoji prefix, or highlight — any consistent approach)
- [ ] `PIPELINE_ERROR` status maps to a red visual indicator
- [ ] `PM_REVISION_REQUESTED` and `PARTNER_REVISION_REQ` status values map to an amber/yellow visual indicator — distinct from both green and red (UX-004 amber pill)
- [ ] In-progress states (`INTAKE_CREATED`, `JUNIOR_DRAFT_COMPLETE`, `PM_REVIEW_COMPLETE`, etc.) map to a neutral/blue indicator

**Row detail (case expander)**
- [ ] After selecting a case (via `st.selectbox`, `st.dataframe` row selection, or equivalent), an expander or detail section renders below the table — not a separate page navigation
- [ ] Only one case expander is open at a time — opening a second case collapses the previous one (UX-004 D-02: expander below row, one at a time)
- [ ] Detail section shows all `final_report.*.md` files present in `cases/{case_id}/` as `st.download_button()` entries — one button per file
- [ ] Detail section notes whether `audit_log.jsonl` exists in the case folder (present/absent label) — does not read or render its contents inline
- [ ] If no deliverable files exist for a case, detail section shows `st.caption("No deliverables yet for this case.")` — not a blank expander
- [ ] If case status is `PIPELINE_ERROR` and an `error.json` or equivalent error artifact exists in the case folder, expander shows a "What to do" guidance message — no raw Python stack trace rendered to the user (UX-004 PIPELINE_ERROR guidance)

**Error and edge states**
- [ ] `cases/index.json` exists but is corrupt JSON → `st.error("Case index is corrupt. Delete cases/index.json and refresh to rebuild.")` — no unhandled exception
- [ ] Case in index references a `case_id` whose folder does not exist on disk → row still renders (index entry shown), download buttons absent with `st.caption("Case folder not found on disk.")` — no crash
- [ ] Empty index (valid JSON, empty list `[]`) → renders as empty state with `st.info(...)` — not a blank table

**Mobile (375px)**
- [ ] `st.dataframe()` renders without multi-column layout wrapper — table itself scrolls natively on mobile (no `st.columns()` wrapping the table)
- [ ] Case ID column does not overflow on 375px viewport — value truncated or ellipsed at ≤16 chars (UX-004: Case ID truncated to 12 chars with tooltip)

**Security**
- [ ] Index data displayed is only `case_id`, `workflow`, `status`, `last_updated` — no `client_name`, intake fields, or document content rendered in the table (index.json contains no PHI per ARCH-INS-02 design)
- [ ] `st.download_button()` reads file via `Path.read_text()` or `Path.read_bytes()` on the resolved `cases/{case_id}/final_report.*.md` path — no shell command or `subprocess` call
- [ ] `case_id` values from index are used only as path components via `tools.file_tools.case_dir()` — not interpolated into shell commands or SQL

**Auth:** N/A — localhost:8501, no auth layer

---

#### P8-10-SETTINGS — pages/settings.py
**New file:** `pages/settings.py`
**Deps:** P8-03-SHARED

- [x] P8-10a Read/write `firm_profile/firm.json` via existing setup_wizard functions. `st.text_input` per field + Save button. Load at startup; write on save. **QA_APPROVED** Session 020

#### AC — P8-10a

**File and data contract**
- [ ] Page reads `firm_profile/firm.json` on load — this is the file `session.py:_load_firm_name()` reads; writing here keeps the Streamlit header firm name in sync
- [ ] If `firm_profile/firm.json` is absent → fields render empty (not an error), `st.warning("Firm profile not yet set up. Fill in the fields below to create it.")` shown (UX-005 missing-file state)
- [ ] Save writes `firm_profile/firm.json` atomically (`.tmp` → `os.replace()`) — partial write on process kill must not corrupt the file
- [ ] `firm_profile/firm.json` written by this page must contain at least `firm_name` key — `session.py:_load_firm_name()` reads this key and will return the updated value after save

**Form fields**
- [ ] Firm Name field: `st.text_input` — pre-populated from `firm.json["firm_name"]` if file exists
- [ ] Logo Path field: `st.text_input` with helper text ("Enter path relative to repo root, e.g. assets/logo.png") — pre-populated from `firm.json["logo_path"]` if set
- [ ] Default Currency field: `st.selectbox` with options AED / USD / SAR — pre-selected from saved value (UX-005)
- [ ] Pricing Model field: `st.selectbox` with options T&M / Lump Sum / Retainer — pre-selected from saved value (UX-005)
- [ ] T&M Day Rate field: `st.text_input` — visible ONLY when Pricing Model = T&M; hidden for Lump Sum and Retainer (UX-005 conditional visibility)
- [ ] T&M Hour Rate field: `st.text_input` — visible ONLY when Pricing Model = T&M; hidden for Lump Sum and Retainer (UX-005 conditional visibility)
- [ ] All 6 fields render with pre-loaded values on page open (not blank on first load if file exists)

**Save button**
- [ ] Save button uses `type="primary"` (#D50032) — per design system
- [ ] Save button is disabled (greyed) when Firm Name field is empty — user cannot save without a firm name (UX-005)
- [ ] Save button re-enables when Firm Name is non-empty

**States**
- [ ] Loading: `st.spinner("Loading firm profile...")` renders while reading `firm.json` (UX-005 loading state)
- [ ] Success: `st.success("Firm profile saved.")` shown after save; page returns to default state showing saved values (UX-005 — note: 3s delay via st.empty + time.sleep acceptable but not required for AC pass)
- [ ] Error on save: `st.error("Save failed: [error message]")` + "Try Again" button that does NOT reload the form fields (user input preserved) — file not written on error (UX-005)
- [ ] Error on read: if `firm.json` exists but is corrupt JSON → `st.warning("Firm profile could not be loaded. Editing will overwrite the existing file.")` — fields render empty, save still permitted

**Mobile (375px)**
- [ ] No `st.columns()` used for form layout — OR if `st.columns()` is used, it is only for desktop layout and fields stack vertically (labels above inputs) at narrow viewport (UX-005 mobile: two-col → single col)
- [ ] Save button renders full-width at bottom of form (UX-005 mobile)

**Security**
- [ ] No API keys, ANTHROPIC_API_KEY, TAVILY_API_KEY, or any credential field rendered to `st.text_input()` or `st.write()` — settings page manages firm profile only
- [ ] Logo Path field accepts text string only — no `subprocess` call, no file execution, no shell interpolation of the entered path
- [ ] `firm.json` written via atomic `.tmp` → `os.replace()` — confirmed by code inspection

**Auth:** N/A — localhost:8501, local tool, no auth layer

---

#### P8-10b-TEAM — pages/10_Team.py (UX-D-04 approved 2026-04-16)
**New file:** `pages/10_Team.py`
**Deps:** P8-03-SHARED

- [x] P8-10b Read/write `firm_profile/team.json`. One `st.expander` per team member — name, title, credentials, bio. "Add Member" button appends new entry. "Remove" per member. Save writes atomically. **QA_APPROVED** Session 020

#### AC — P8-10b

**File config (FC)**
- [ ] FC-1: `_TEAM_JSON` constant points to `FIRM_PROFILE_DIR / "team.json"` — not a hardcoded string path
- [ ] FC-2: `bootstrap(st)` called at module level via `streamlit_app.shared.session`

**Load (LD)**
- [ ] LD-1: Loading spinner shown while reading team.json ("Loading team..." or equivalent)
- [ ] LD-2: When `team.json` absent: no error banner; page renders empty state with "Add Member" prompt — file absence is normal (first run)
- [ ] LD-3: When `team.json` exists but is corrupt JSON: `st.warning` shown; page still renders with zero members so user can build a new list and overwrite

**Display (DI)**
- [ ] DI-1: One `st.expander` rendered per team member; expander label uses the member's name (or "New Member" when name is blank)
- [ ] DI-2: Inside each expander: four `st.text_input` fields — Name, Title, Credentials, Bio — pre-populated from loaded data
- [ ] DI-3: Empty state (zero members): `st.info` shown prompting user to add their first team member; expander section absent
- [ ] DI-4: Member count shown above the expander list (e.g. "3 team members")

**Add Member (AM)**
- [ ] AM-1: "Add Member" button appends a blank entry to `st.session_state` member list; triggers rerun so new expander appears
- [ ] AM-2: New member expander is expanded by default; all four fields are blank

**Remove Member (RM)**
- [ ] RM-1: Each expander contains a "Remove" button; clicking it removes that entry from `st.session_state` and triggers rerun — member disappears immediately
- [ ] RM-2: Remove does NOT auto-save to disk — user must click "Save" to persist the removal

**Save (SV)**
- [ ] SV-1: "Save" button is `type="primary"`; it is always enabled (saving zero members is valid — clears the team)
- [ ] SV-2: Blank-name members are either filtered out before save or a `st.warning` is shown before proceeding — no silent empty entries written to team.json
- [ ] SV-3: Atomic write: `.tmp` file written first, then `os.replace()` — never direct write to `team.json`
- [ ] SV-4: On success: auto-clearing success banner shown for 3 s then cleared (consistent with Settings page pattern — `placeholder = st.empty()`)
- [ ] SV-5: On write failure: `st.error` shown with a "Try Again" button; session state preserves current edits (no data loss)

**Mobile (MOB)**
- [ ] MOB-1: No `st.columns()` call in page-level executable code — single-column layout at 375px

**Security (SEC)**
- [ ] SEC-1: No shell execution from text inputs — all four fields used as data values only
- [ ] SEC-2: `team.json` written only into `firm_profile/` via the `_TEAM_JSON` constant — no user-controlled file path

---

#### P8-11-DOCIN — Document ingestion UI
**Files:** pages/2_Investigation.py, pages/6_FRM.py, pages/11_Due_Diligence.py, pages/13_Transaction_Testing.py
**Deps:** P8-08-PAGES
**BA:** ba-logic.md:72-73 — documents uploaded after intake, before pipeline
**UX:** UX-006 APPROVED

- [x] P8-11a Add `st.file_uploader("Upload case documents (optional)", accept_multiple_files=True, type=["pdf","docx","txt","xlsx"])` to Investigation, FRM, DD, TT pages. Feed into `DocumentManager.register_document()`. Registration happens before pipeline runs. **QA_APPROVED Session 020**

#### AC — P8-11a

**Widget config (WG) — applies to all 4 pages**
- [ ] WG-1: `st.file_uploader` present in intake stage on pages 2_Investigation, 6_FRM, 11_Due_Diligence, 13_Transaction_Testing
- [ ] WG-2: `accept_multiple_files=True` and `type=["pdf","docx","txt","xlsx"]` set on the uploader
- [ ] WG-3: Static `st.warning("Maximum file size is 10MB per document.")` shown below uploader (always visible, not conditional)
- [ ] WG-4: Uploader appears below the intake fields and above the Run button (Zone A)

**Registration timing (RT)**
- [ ] RT-1: Document registration happens inside the Run button click handler — NOT on file selection/change event
- [ ] RT-2: `case_dir(intake.case_id)` called before `DocumentManager` initialization to ensure case folder exists

**File write (FW)**
- [ ] FW-1: File bytes written using `UploadedFile.getbuffer()` — not `read()` or shell copy
- [ ] FW-2: Write destination is `case_dir(intake.case_id) / file.name` — path constructed from constant + filename only, no user-controlled directory component

**Registration calls (RG)**
- [ ] RG-1: `DocumentManager(intake.case_id)` initialized after `case_dir()` call; stored in `st.session_state`
- [ ] RG-2: `register_document()` called with `folder="uploaded"` and `doc_type` from `_infer_doc_type(file.name)`
- [ ] RG-3: `_infer_doc_type` helper maps: `.pdf`→`"pdf"`, `.docx`→`"word"`, `.txt`→`"text"`, `.xlsx`→`"excel"`
- [ ] RG-4: Each `register_document()` call wrapped in try/except — failure shows `st.error("Failed to register [name]: [err]")` and continues to next file (per-file isolation)

**File status display (FS)**
- [ ] FS-1: Successful registration shows `st.caption` with `✓ [name]` and file size in MB for each registered file
- [ ] FS-2: Zero files uploaded → no registration attempt; no error shown; Run button remains enabled; pipeline runs without document context

**Edge cases (EC)**
- [ ] EC-1: >10 files uploaded → `st.warning("Maximum 10 documents per case.")` shown; registration still proceeds for all files (warning only, not a hard block per UX-006)
- [ ] EC-2: Note — "removed from uploader" caption (UX-006) is N/A: registration-on-Run-click is an approved ARCH-P8-11a deviation; user cannot remove a file after Run is clicked (stage transitions immediately)

**Workflow integration (WI)**
- [ ] WI-1: Investigation page passes `document_manager=dm` to `run_investigation_workflow` when files were uploaded (or `document_manager=None` when none)
- [ ] WI-2: FRM page passes `document_manager=dm` to `run_frm_pipeline` when files were uploaded (or `None` when none)
- [ ] WI-3: DD page does NOT pass `document_manager` to `run_due_diligence_workflow` — registration only (files available in case folder)
- [ ] WI-4: TT page does NOT pass `document_manager` to `run_transaction_testing_workflow` — registration only

**Mobile (MOB)**
- [ ] MOB-1: No `st.columns()` wrapper added around the file uploader on any of the 4 pages

**Security (SEC)**
- [ ] SEC-1: No `subprocess`, `os.system`, `shell=True`, or `exec`/`eval` in any of the 4 pages
- [ ] SEC-2: Write path uses `case_dir(intake.case_id)` constant — no string concatenation from user-supplied directory input

**Architecture constraints (ARCH-P8-11a — Architect sign-off):**
- Placement: below intake fields, above Run button (Zone A per UX-006)
- Registration timing: on Run click, not on upload event — `intake.case_id` is required to initialize DocumentManager, and it is available after `generic_intake_form` / `frm_intake_form` returns
- File write: `UploadedFile.getbuffer()` → write to `case_dir(intake.case_id) / file.name` — never to user-controlled path
- DocumentManager: initialize as `DocumentManager(intake.case_id)` AFTER calling `case_dir(intake.case_id)` (which creates the folder). Store in `st.session_state`.
- `register_document(filepath, folder="uploaded", doc_type=_infer_doc_type(file.name), provenance=DocumentProvenance(...))` — wrap each call in try/except; show `st.error("Failed to register [name]: [err]")` per file; other files unaffected
- Helper: `_infer_doc_type(name) -> str`: pdf→"pdf", docx→"word", txt→"text", xlsx→"excel"
- For Investigation and FRM: pass pre-created `document_manager=dm` to `run_investigation_workflow` / `run_frm_pipeline` (existing params)
- For DD and TT: register docs to case folder; do NOT pass dm to workflow (those workflows don't use it internally yet — files are available in case folder for future use)
- UX-006 limits: show `st.warning("Maximum file size is 10MB per document.")` as static helper; if uploaded file count >10 show `st.warning("Maximum 10 documents per case.")`; if user removes file from uploader show `st.caption("Removed from uploader — already registered in case index.")`
- Uploaded file list: show `st.caption("✓ [name] — [size]MB — registered")` after each successful registration
- Mobile: file_uploader is full-width natively; no st.columns() needed
- Security: UploadedFile.getbuffer() only; no shell execution; no arbitrary paths

---

#### P8-12-EXCEL — BLOCKED: MISSING_BA_SIGNOFF
FE-10 Excel output. No BA entry exists for Excel as a required output format.
Do not build until /ba session produces entry in tasks/ba-logic.md.

#### P8-13-TIER — BLOCKED: MISSING_BA_SIGNOFF
FE-11 Two-tier risk structure (Design-Level vs Operational-Level). No BA entry for tier taxonomy or schema change to RiskItem.
Do not build until /ba session produces entry in tasks/ba-logic.md.

---

#### P8-14-SMOKE — End-to-end smoke test
**Deps:** P8-04-APP, P8-05-FE08, P8-06-FRM, P8-07-FE09, P8-08-PAGES, P8-09-TRACKER, P8-10-SETTINGS, P8-11-DOCIN

- [ ] P8-14a `streamlit run app.py` — browser opens, sidebar shows all pages
- [ ] P8-14b FRM page: intake → pipeline → review 3+ risk items (A/F/R visible, not hidden) → finalize → verify `cases/{id}/final_report.en.md` written
- [ ] P8-14c Case Tracker: new FRM case appears with DELIVERABLE_WRITTEN status
- [ ] P8-14d Investigation page: intake → pipeline → download output
- [ ] P8-14e Interim folder check: `ls cases/{id}/` root has only `final_report.*`, `state.json`, `audit_log.jsonl`, `citations_index.json`; `ls cases/{id}/interim/` has `*.v*.json`
- [ ] P8-14f CLI regression: `python run.py` → Rich menu renders → Option 6 completes → no crash

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

### Phase 9 — Workflow Chaining (GATED on Phase 8)

- [ ] CH-01 Post-workflow "Add another deliverable to this case?" prompt (Y/N)
- [ ] CH-02 If Y → present only compatible follow-on workflows based on existing case type
- [ ] CH-03 Chain state: state.json updated with all workflow runs; case_tracker shows all deliverables per case_id
- [ ] CH-04 Integration test: investigation_report → persona_review on same case_id

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

### Sprint-10L Phase A — Prompt-Only Fix (PRIORITY 1 — unblocks P7-GATE)

**Scope decision (Session 014 Architect):** Full behavioral matrix (REVIEW_MODE, verdict spectrum,
DocLevel, Phase, Authority axes) split into Phase B — gated on P7-GATE passing + BA sign-off.
Phase A is the minimal targeted fix: 4 files, no schema changes, no orchestrator changes.
Design rationale in: docs/lld/sprint-10L-review-chain-design.md

**Root cause of G-13/G-14 (63% of crashes):** PM/Partner don't know RESEARCH_MODE=knowledge_only,
so they reject for citation absence → revision loop exhausts → crash.

**Phase A fix:** Pass RESEARCH_MODE into PM/Partner prompts. In knowledge_only mode:
- NEVER reject for missing citations or generic output
- Flag gaps as open_questions[], not revision_requested=true
- STILL reject: empty findings list, wrong regulator, structural schema violation

**Security model:** No auth/PII changes. Audit: research_mode logged in agent context.

**Branch:** feature/sprint-10L-mode-aware-review-chain (partially built — see notes per task)

- [x] SRL-01 `agents/project_manager/prompts.py` — DONE by junior-dev (Session 014).
      build_system_prompt() accepts research_mode param; _build_mode_section() generates
      mode-specific criteria block. Awaiting SRL-03a before QA.

- [x] SRL-02 `agents/partner/prompts.py` — DONE. build_task_message() now accepts research_mode
      param; appends "Use regulatory_lookup..." only when research_mode == "live".

- [x] SRL-03a `agents/project_manager/agent.py` — DONE. import config; passes
      research_mode=config.RESEARCH_MODE to prompts.build_system_prompt().

- [x] SRL-03b `agents/partner/agent.py` — DONE. import config; passes
      research_mode=config.RESEARCH_MODE to both build_system_prompt() and build_task_message().

- [x] SRL-04 Smoke test (AK manual): PASSED 2026-04-08. FRM 2 modules (AML + Regulatory),
      knowledge_only mode. PM approved without citation revision requests. Final report written.
      G-13/G-14 confirmed fixed. P7-GATE PASSED.

---

### Sprint-10L Phase B — Behavioral Matrix (GATED on P7-GATE + BA sign-off)

**Scope:** Full 10-component design from docs/lld/sprint-10L-review-chain-design.md.
MISSING_BA_SIGNOFF: REVIEW_MODE enum, verdict spectrum, DocLevel axis, Phase axis, Authority Level
have no BA entry in ba-logic.md. Do not start until BA session completes for this feature.

**Files touched:** config.py, schemas/artifacts.py, core/orchestrator.py,
agents/project_manager/prompts.py + agent.py, agents/partner/prompts.py + agent.py,
workflows/sanctions_screening.py, workflows/due_diligence.py,
workflows/transaction_testing.py, workflows/investigation_report.py

- [ ] SRL-B-BA Write BA entries for behavioral matrix to ba-logic.md (AK input required)
- [ ] SRL-B-01 config.py — REVIEW_MODE flag with validation (DEMO/DEV/CLIENT_DRAFT/CLIENT_FINAL)
- [ ] SRL-B-02 schemas/artifacts.py — ReviewVerdict enum; update ApprovalDecision + RevisionRequest
- [ ] SRL-B-03 core/orchestrator.py — behavioral_matrix(), universal_blocker_checks(),
      D0/D1 equivalence enforcement, FINAL-phase multiplier lock
- [ ] SRL-B-04 agents/project_manager/prompts.py — rewrite to consume full matrix context
- [ ] SRL-B-05 agents/partner/prompts.py — same
- [ ] SRL-B-06 agents/project_manager/agent.py + agents/partner/agent.py — pass matrix context
- [ ] SRL-B-07 workflows/sanctions_screening.py, due_diligence.py — BLOCK not loop for G-A
- [ ] SRL-B-08 workflows/transaction_testing.py, investigation_report.py — intake completeness gates

---

### Sprint-10K — Pre-Production Hardening (GATED on P7-GATE — do not start until gate passes)

**Context:** Session 013 smoke test exposed three production risks in the BUG-09/10 fixes. These must
be resolved before any client-facing use of the system.

**Security model (applies to all 10K tasks):**
- Auth: N/A (local CLI, single user)
- Data boundaries: no change
- PII: no change — sanitisation hooks unchanged
- Audit: PPH-01 adds a new audit event for research mode at session start
- Abuse surface: PPH-03 disclaimer is fixed string — no injection surface

#### PPH-01 — RESEARCH_MODE smart default (P1 — must fix before production)

**Risk:** Current default is `knowledge_only` regardless of whether TAVILY_API_KEY is present.
A consultant with a valid key who doesn't set `RESEARCH_MODE=live` gets silently degraded output
with no live regulatory/sanctions data. The degradation is not visible at session start.

- [x] PPH-01a `config.py` — DONE. RESEARCH_MODE defaults to "live" if TAVILY_API_KEY present, "knowledge_only" if not. Explicit env var always wins.

- [x] PPH-01b `run.py` — DONE. display_research_mode_banner() called at startup after validate_config().

- [x] PPH-02a `workflows/sanctions_screening.py` — DONE. Red warning panel + explicit confirm before workflow runs in knowledge_only mode.

- [x] PPH-03a `ui/display.py` — DONE. display_research_mode_banner() added.

- [x] PPH-03b `core/agent_base.py` — DONE. stderr warn line after knowledge-only disclaimer append.

- [x] PPH-04a `docs/lld/guardrails.md` — DONE. Mode-awareness rule documented with rationale and required pattern.

---

### BUG-10 — Citation guard blocks knowledge_only mode (IMMEDIATE — P7-GATE blocker)

**File:** `core/agent_base.py` — single line fix.

**Root cause:** Citation guard at line 160 raises `NoCitationsError` when no authoritative tool was
called. In `knowledge_only` mode, research tools return stubs — model may not call them, so the guard
fires even though there is no real citation requirement. Guard was designed for `live` mode only.

**Security model:** N/A — no auth, no PII, no new data paths. Guardrail relaxation is scoped to
knowledge_only mode only. Live mode guard is unchanged.

- [x] BUG-10a `core/agent_base.py` — DONE. Committed to feature/BUG-10-citation-guard-knowledge-only.

**Acceptance:** `python run.py` → Option 6 → FRM run completes without NoCitationsError.

---

### Sprint-10J — Taxonomy + True Modularity Foundation (GATED on P7-GATE)

**BA sign-off:** BA-014, BA-015 confirmed 2026-04-07.

**Design principle:** Every axis of variation (industry, module, jurisdiction, knowledge routing) becomes
a data/config file. Zero core-code changes to add a new industry, service line, or jurisdiction.

**Dependency note:** Sprint-10J is foundational — all later intake and UI improvements build on it.
Complete before BA-013 (FRM Suite) and FRM-R-01..08, as both will read from taxonomy data.

```
SPRINT-10J INTERNAL DEPS:
TAX-01 (industries.json) ──── TAX-02 (frm_modules.json) ──── TAX-04 (routing_table.json)
TAX-01 ──────────────────────────────────────────────── TAX-03 (jurisdiction registry → JSON)
TAX-01 + TAX-02 + TAX-03 + TAX-04 ──── TAX-05 (prompt_with_options UI helper)
TAX-05 ──── TAX-06 (wire into all intake flows)
```

- [x] TAX-01 Create `knowledge/taxonomy/industries.json` — Level 1 industries + Level 2 sub-sectors.
      Minimum: Manufacturing, Financial Services, Real Estate, Healthcare, Retail, Government, Technology, Construction.
      Each entry: `{id, label, sub_sectors[], suggested_frm_modules[], rationale}`.

- [x] TAX-02 Create `knowledge/taxonomy/frm_modules.json` — extract FRM module definitions from
      frm_risk_register.py. Each entry: `{id, label, description, dependencies[], default_enabled}`.
      frm_risk_register.py reads from this file — no module definitions in code.

- [x] TAX-03 Move `JURISDICTION_REGISTRY` from `config.py` to `knowledge/taxonomy/jurisdictions.json`.
      config.py loads the file at startup and exposes the same API (get_jurisdiction_domains etc).
      No behaviour change — pure data extraction.

- [x] TAX-04 Create `knowledge/taxonomy/routing_table.json` — maps `{industry_id, workflow_id}` →
      `knowledge_file_path`. Agents read this to load the right knowledge baseline. Start with FRM + DD.

- [x] TAX-05 Add `prompt_with_options(question, options, allow_free_text=True)` to `ui/guided_intake.py`.
      Displays numbered list + "0. Other (type your own)" option. Returns structured value with
      `{selected_id, label, is_custom}` so downstream code knows if it was a taxonomy pick or free text.

- [x] TAX-06 Wire `prompt_with_options` into all workflow intake flows that currently ask free-text for
      industry, sub-sector, jurisdiction, and engagement type:
      `workflows/frm_risk_register.py`, `workflows/engagement_scoping.py`,
      `workflows/due_diligence.py`, `workflows/investigation_report.py`.

**UX note:** TAX-05/06 also drives the Streamlit frontend redesign (Phase 8) — intake components will
map directly to Streamlit select boxes + text_input fallback. Design TAX-05 interface with that in mind.

---

### Sprint-10C — Historical Knowledge Library (depends on Sprint-10A — UNBLOCKED)

- [ ] HRL-00 tools/knowledge_library.py: KnowledgeLibrary class — ingest(file_path, service_type) → intake conversation → sanitise() → index_entry(). sanitise() strips names, passport/ID numbers, company reg numbers, case IDs, identifying dates. Retrieval: match_similar(engagement_params) → list[HistoricalMatch]. Hard gate: SanitisationError blocks index write if PII in stripped output.
- [ ] HRL-01 Historical import wizard — extend setup_wizard.py or add guided_import.py; calls KnowledgeLibrary.ingest() per file; shows index summary. CE Creates DD reports (3) are seed entries. GATED on HRL-00.
- [ ] HRL-02 firm_profile/historical_registers/ dir + index.json schema — GATED on HRL-00
- [ ] HRL-03 firm_profile/historical_reports/due_diligence/ dir + index.json schema — GATED on HRL-00
- [ ] HRL-04 firm_profile/historical_reports/sanctions_screening/ dir + index.json schema — GATED on HRL-00
- [ ] HRL-05 firm_profile/historical_reports/transaction_testing/ dir + index.json schema — GATED on HRL-00
- [ ] HRL-06 firm_profile/historical_scopes/ dir + index.json schema — GATED on HRL-00

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

