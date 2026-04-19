# TODO

## SESSION STATE
Status:         OPEN
Active task:    none
Active persona: junior-dev
Blocking issue: none
Last updated:   2026-04-19T07:42:03Z — state transition by MCP server

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
Sprint-01, Sprint-02, QR-01..16, Sprint-03, Sprint-04 AKR, Sprint-06, Sprint-09, Sprint-10A..B, Sprint-10E/H/F/I/J/K, Sprint-10L-Phase-A, BUG-10, Phase 8 automated tasks (P8-01/03/04/07/08/09/10/11, ARCH-INS-01/02) — all DONE, see releases/completed-tasks.md.
**Merge pending:** feature/P8-phase8-streamlit → main (P8-14 superseded; merge now).

---

## PENDING TASKS

---

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


#### P8-12-EXCEL — BLOCKED: MISSING_BA_SIGNOFF
FE-10 Excel output. No BA entry exists for Excel as a required output format.
Do not build until /ba session produces entry in tasks/ba-logic.md.

#### P8-13-TIER — BLOCKED: MISSING_BA_SIGNOFF
FE-11 Two-tier risk structure (Design-Level vs Operational-Level). No BA entry for tier taxonomy or schema change to RiskItem.
Do not build until /ba session produces entry in tasks/ba-logic.md.

---

#### P8-14-SMOKE — ~~SUPERSEDED~~ (Session 022)
**Status:** Superseded by design change. Phase 9 + Sprint-RD replaces the report-writing path entirely (F_Final/, BaseReportBuilder, versioning). Testing the old flat-folder, UUID-case flow against the new design is meaningless.
**Branch:** feature/P8-phase8-streamlit → merged to main (pages load, 4 bugs fixed in commit 36f0cc5, pipeline runs). Report-writing rebuilt in Sprint-RD.
- [x] P8-14a browser opens, sidebar shows 14 pages — CONFIRMED (AK session 022)
- [x] P8-14f CLI `python run.py` — no crash — CONFIRMED (AK session 022)
- [~] P8-14b FRM finalize → report write — report-writing path rebuilt in Sprint-RD; not tested against old design
- [~] P8-14c/d/e — superseded by Phase 9 folder structure

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

---


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

#### P9-01 — schemas/project.py (PREREQUISITE)
**New file:** `schemas/project.py`
**BA:** BA-P9-01, BA-P9-03, BA-P9-05
**Security model:** as above. Slug field enforces sanitized pattern via Pydantic validator.

**Schemas to define:**
- `ProjectIntake` — project_name: str, project_slug: str (derived, validated), client_name: str, service_type: str, language_standard: Literal["acfe","expert_witness","regulatory","board_pack"] = "acfe", created_at: datetime, naming_convention: str
- `InputSession` — session_id: str, project_slug: str, mode: Literal["input","final_run"], timestamp: datetime, documents_registered: list[str], notes_path: Optional[str], key_facts_count: int, red_flags_count: int
- `ProjectState` — project_slug: str, status: CaseStatus, sessions: list[InputSession], language_standard: str, context_budget_used_pct: float, interim_context_written: bool, last_updated: datetime

- [ ] P9-01a Define `ProjectIntake` schema with Pydantic validator on `project_slug`: strip non-alphanumeric/hyphen chars; block `..`, `/`, `\`, null bytes; raise ValueError on empty result
- [ ] P9-01b Define `InputSession` schema
- [ ] P9-01c Define `ProjectState` schema

#### AC — P9-01
- [ ] `from schemas.project import ProjectIntake, InputSession, ProjectState` imports with no errors
- [ ] `ProjectIntake(project_name="Project Alpha / FRM", ...)` → `project_slug` = `"project-alpha-frm"` (slash stripped, spaces → hyphens)
- [ ] `ProjectIntake(project_name="../etc/passwd", ...)` raises `ValueError` — path traversal blocked
- [ ] `ProjectIntake(project_name="   ", ...)` raises `ValueError` — empty slug blocked
- [ ] `ProjectIntake(language_standard="invalid")` raises `ValidationError`

---

#### P9-02 — tools/project_manager.py (PREREQUISITE)
**New file:** `tools/project_manager.py`
**Deps:** P9-01
**BA:** BA-P9-01, BA-P9-02, BA-P9-03, BA-P9-04
**Security model:** all filesystem writes via `case_dir()` helper only; no user-controlled path component after slug sanitization.

**Class:** `ProjectManager`
- `create_project(intake: ProjectIntake) -> Path` — creates `cases/{slug}/` + A-F subfolder structure; writes `state.json` with ProjectState; logs to `audit_log.jsonl`
- `list_projects() -> list[dict]` — reads `cases/index.json`; returns entries where source is "P9" (named projects) + legacy UUID entries with a `legacy=True` flag
- `get_project(slug: str) -> ProjectState` — reads `cases/{slug}/state.json`
- `create_af_structure(slug: str)` — creates the 6 standard subfolders under `cases/{slug}/`
- `start_input_session(slug: str) -> InputSession` — creates timestamped subfolder in `C_Evidence/`; initializes `InputSession`; appends to session_log
- `add_session_note(slug: str, note: str)` — appends to `D_Working_Papers/session_notes_{YYYYMMDD}.md` (atomic write)
- `add_key_fact(slug: str, fact: dict)` — appends to `D_Working_Papers/key_facts.json`
- `add_red_flag(slug: str, flag: dict)` — appends to `D_Working_Papers/red_flags.json`
- `get_context_summary(slug: str) -> dict` — returns document count, estimated token usage pct, interim_context exists
- `write_interim_context(slug: str, content: str)` — atomic write to `D_Working_Papers/interim_context.md`; updates state.json `interim_context_written = True`
- `detect_slug_collision(slug: str) -> bool` — returns True if `cases/{slug}/` already exists

- [ ] P9-02a `create_project()` + `create_af_structure()` — creates all 6 folders atomically (all-or-nothing: if any mkdir fails, rollback all created dirs)
- [ ] P9-02b `list_projects()` — reads cases/index.json; flags legacy entries
- [ ] P9-02c `get_project()` + `get_context_summary()`
- [ ] P9-02d `start_input_session()` + `add_session_note()` + `add_key_fact()` + `add_red_flag()`
- [ ] P9-02e `write_interim_context()` — atomic write; updates state.json

#### AC — P9-02
- [ ] `create_project()` creates exactly 6 subfolders: A_Engagement_Management, B_Planning, C_Evidence, D_Working_Papers, E_Drafts, F_Final
- [ ] `create_project()` with a project_name whose slug collides with an existing folder raises `ValueError("Project slug already exists: ...")`
- [ ] `add_session_note()` appends (not overwrites) — calling twice in one day produces one file with two entries
- [ ] `write_interim_context()` uses `.tmp` → `os.replace()` pattern — atomic
- [ ] `get_context_summary()` returns `interim_context_written = True` after `write_interim_context()` called

---

#### P9-03A — pages/1_Engagements.py — Active Engagements list
**New file:** `pages/1_Engagements.py`
**Deps:** P9-02
**BA:** BA-P9-01, BA-P9-03
**Security model:** same as P8-09 tracker; no PII in list view; slug used only via case_dir()

- [ ] P9-03Aa Read `cases/index.json` via `ProjectManager.list_projects()`; render table: Project Name | Service Type | Status | Last Session
- [ ] P9-03Ab Each row: "Open" button → sets `st.session_state.active_project = slug`; routes to Project Workspace (P9-05)
- [ ] P9-03Ac "New Engagement" button → navigates to New Engagement wizard (P9-03B)
- [ ] P9-03Ad Empty state: `st.info("No projects yet. Start a new engagement.")` with prominent "New Engagement" button
- [ ] P9-03Ae Legacy cases (UUID format, `legacy=True`) shown in a separate "Legacy Cases" expander below the main table

#### AC — P9-03A
- [ ] Table renders with columns: Project Name, Service Type, Status, Last Session — sorted by Last Session descending
- [ ] Legacy cases shown in collapsed expander, not in main table
- [ ] "Open" button sets `st.session_state.active_project` and does NOT trigger a pipeline run
- [ ] Empty index → `st.info()` shown, no error

---

#### P9-03B — New Engagement wizard (within pages/1_Engagements.py)
**File:** `pages/1_Engagements.py` (same page, different st.session_state stage)
**Deps:** P9-01, P9-02
**BA:** BA-P9-01, BA-P9-05

- [ ] P9-03Ba Multi-field wizard form: Project Name, Client Name, Service Type (selectbox), Language Standard (selectbox — ACFE / Expert Witness / Regulatory Submission / Board Pack), Naming Convention (text_input with suggestion like "ClientName_ServiceType")
- [ ] P9-03Bb On submit: validate project_name → derive slug → detect collision → call `ProjectManager.create_project()` → show success with folder structure created confirmation
- [ ] P9-03Bc Slug preview: as Maher types the Project Name, show "Folder name: cases/project-alpha-frm/" live (via `st.caption()` updated on each keystroke — use `on_change` or just display below input)
- [ ] P9-03Bd Collision warning: if slug already exists, show `st.warning("A project with this name already exists. Open it instead?")` with "Open Existing" button

#### AC — P9-03B
- [ ] Language Standard selectbox has exactly 4 options matching BA-P9-05 labels
- [ ] Slug preview updates as project name is typed — shown as `st.caption()` below the name field
- [ ] Collision detected before `create_project()` called — no duplicate folder created
- [ ] On success: `st.success("Project created: cases/{slug}/")` + list of 6 created subfolders shown

---

#### P9-04 — A-F Folder Structure in tools/file_tools.py
**File:** `tools/file_tools.py`
**Deps:** P9-01
**BA:** BA-P9-02
**Note:** `ProjectManager.create_af_structure()` handles creation. This task ensures `file_tools.py` route functions (case_dir, write_artifact, etc.) respect A-F layout for NEW projects.

- [ ] P9-04a Add `AF_FOLDERS = ("A_Engagement_Management", "B_Planning", "C_Evidence", "D_Working_Papers", "E_Drafts", "F_Final")` constant to `tools/file_tools.py`
- [ ] P9-04b Add `is_af_project(case_id: str) -> bool` — returns True if `cases/{case_id}/E_Drafts/` exists (distinguishes P9 named projects from legacy UUID cases)
- [ ] P9-04c For P9 projects: `write_artifact()` writes to `E_Drafts/` instead of root; `write_final_report()` writes to `F_Final/` instead of root. Legacy projects: unchanged behavior.
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

- [ ] P9-07Aa Add "Default Language Standard" selectbox to Settings page: ACFE Internal Review / Expert Witness / Regulatory Submission / Board Pack
- [ ] P9-07Ab Save writes `firm_profile/firm.json["default_language_standard"]` alongside existing fields
- [ ] P9-07Ac Load at bootstrap: `st.session_state.default_language_standard` from firm.json or default "acfe"

#### AC — P9-07A
- [ ] Settings page has "Default Language Standard" selectbox with exactly 4 options (matching BA-P9-05 labels)
- [ ] Saving updates `firm.json["default_language_standard"]`; existing firm.json fields unchanged
- [ ] Bootstrap loads default and exposes it in `st.session_state`

---

#### P9-07B — Apply Language Standard to All Agent System Prompts
**Files:** `agents/junior_analyst/prompts.py`, `agents/project_manager/prompts.py`, `agents/partner/prompts.py`
**Deps:** P9-01, P9-07A
**BA:** BA-P9-05

- [ ] P9-07Ba Create `LANGUAGE_STANDARD_BLOCKS: dict[str, str]` in a shared module (`agents/shared/language_standards.py` or inline in each prompts.py) with one instruction block per standard
  - `"acfe"`: "Write in narrative style. Use qualified language for inferences ('evidence suggests', 'it appears'). Cite every source. Past tense. Third person. No pronouns."
  - `"expert_witness"`: "Write in court-ready format. Past tense only. Third person only. No pronouns. State only what is directly evidenced. No opinions or inferences — if inference is required, label it explicitly as a reasonable professional conclusion."
  - `"regulatory"`: "Write in formal regulatory submission style. Cite regulations by full name and section number. Use prescribed structure for the relevant regulatory body. Past tense. Third person."
  - `"board_pack"`: "Write for a C-suite / board audience. Lead with business risk and impact. Minimize technical jargon. Past tense. Third person. Executive summary first, detail follows."
- [ ] P9-07Bb All three agents' `build_system_prompt()` functions accept `language_standard: str = "acfe"` param; append the relevant block from `LANGUAGE_STANDARD_BLOCKS`
- [ ] P9-07Bc All three agents' `__call__()` methods pass `language_standard` from context dict → to prompt builder

#### AC — P9-07B
- [ ] `build_system_prompt(language_standard="expert_witness")` includes "court-ready" and "Past tense only" in the returned string — code inspection
- [ ] `build_system_prompt(language_standard="acfe")` includes "qualified language" — code inspection
- [ ] `context.get("language_standard", "acfe")` pattern used in all three agent `__call__()` methods
- [ ] Missing `language_standard` in context → defaults to "acfe" (no KeyError)

---

#### P9-08 — AI Review Mode
**New file:** `agents/reviewer/review_agent.py` (or inline in orchestrator)
**Deps:** P9-07B, Phase 8 complete
**BA:** BA-P9-06
**Note:** Runs as a post-pipeline pass before Maher's review screen. Uses Haiku (speed/cost). Results stored in D_Working_Papers/.

- [ ] P9-08a `agents/reviewer/` directory + manifest: role="reviewer", model_preference="haiku", max_turns=3, output_schema="ReviewAnnotation"
- [ ] P9-08b `ReviewAnnotation` schema in `schemas/artifacts.py`: finding_id: str, support_level: Literal["supported","partially_supported","unsupported"], evidence_cited: list[str], logic_gaps: list[str], rewritten_text: Optional[str]
- [ ] P9-08c `ReviewAgent.__call__(draft: dict, context: dict) -> list[ReviewAnnotation]` — iterates over `draft["findings"]`; for each finding: classifies support level, identifies logic gaps, rewrites text per language_standard; returns list of annotations
- [ ] P9-08d Wire into pipeline: orchestrator calls ReviewAgent after Partner approval, before final report write. Annotations stored to `D_Working_Papers/ai_review_{YYYYMMDD}.json`.
- [ ] P9-08e Streamlit review UI: in existing A/F/R review screen (FRM, Investigation), add a small badge per finding: green "SUPPORTED" / amber "PARTIAL" / red "UNSUPPORTED". Maher can click badge to see evidence_cited and logic_gaps.

#### AC — P9-08
- [ ] `ReviewAnnotation` importable from `schemas.artifacts`; `support_level="invalid"` raises ValidationError
- [ ] ReviewAgent produces exactly one annotation per finding — same count as `draft["findings"]`
- [ ] Finding with `citations=[]` → automatically classified as `"unsupported"` (no model call needed; code inspection)
- [ ] `ai_review_{date}.json` written to `D_Working_Papers/` inside case folder — not to root
- [ ] Review badges visible in FRM review stage (P8-06c): green/amber/red per risk item
- [ ] AI Review Mode can be disabled: `context.get("ai_review_enabled", True)` — when False, ReviewAgent not called; badges absent

---

#### P9-09 — Wire All Workflow Pages to Project Context
**Files:** pages/2_Investigation.py, pages/6_FRM.py, pages/7_Proposal.py, pages/4_Policy_SOP.py, pages/5_Training.py, pages/8_PPT_Pack.py, pages/0_Scope.py, pages/11_Due_Diligence.py, pages/12_Sanctions.py, pages/13_Transaction_Testing.py
**Deps:** P9-03A, P9-04, P9-05, P9-06, P9-07B, P9-08
**BA:** BA-P9-01, BA-P9-03
**Note:** Large task — must be decomposed into sub-tasks per page at build time.

- [ ] P9-09a When `st.session_state.active_project` is set: pre-fill intake form fields from project context (client_name, service_type, language_standard); lock fields that were set at project creation
- [ ] P9-09b When active_project set: `DocumentManager` initialized from `ProjectManager.get_context_for_agents()` instead of fresh intake; accumulated context passed to pipeline
- [ ] P9-09c Post-pipeline: artifacts written to project's E_Drafts/ (via P9-04); final report written to F_Final/; Case Tracker reads from project's F_Final/
- [ ] P9-09d Case Tracker (pages/9_Case_Tracker.py): for P9 projects, "View Project" link routes to Engagements page with active_project set
- [ ] P9-09e If no active_project set (user navigates directly to a workflow page): existing behavior unchanged — standalone case with UUID, root-level folder, no A-F structure (backward compat)

#### AC — P9-09
- [ ] With `active_project` set: intake form shows pre-filled client_name from project; field is read-only
- [ ] With `active_project` set: pipeline receives `interim_context.md` content (if exists) via DocumentManager
- [ ] With no `active_project`: all pages function identically to Phase 8 behavior — no regression
- [ ] Final report for AF project lands in `cases/{slug}/F_Final/final_report.en.md` — not root
- [ ] Case Tracker "View Project" button present for P9 projects; absent for legacy UUID cases

---


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

- [x] EMB-00 Add `sentence-transformers>=2.7.0` and `chromadb>=0.4.0` to `requirements.txt`
- [ ] EMB-01 `tools/embedding_engine.py` — `EmbeddingEngine(case_id)`: chunk_document(), embed_and_index(), search(query, n=5), get_context_for_query(query, max_chars=8000). Graceful fallback if sentence-transformers unavailable (R-NEW-07).
- [ ] EMB-02 Wire into `DocumentManager.register_document()`: chunk+embed on upload; Haiku extraction → append to `D_Working_Papers/case_intake.md`
- [ ] EMB-03 Semantic search UI in Input Session workspace: `st.text_input` + Search → ranked chunks with source citation
- [ ] EMB-04 Pipeline context prep in `core/orchestrator.py`: if vector index exists, use `get_context_for_query()` per finding area; inject as `embedded_context`; fallback to existing DocumentManager if no index

---

### Sprint-AIC — Smart Intake Completion (Session 022 — GATE CLEARED — P8 merged 97626d9)

**BA:** BA-R-10
**Security:** No new data paths; Haiku/Sonnet API calls gated on RESEARCH_MODE; results stored only in D_Working_Papers/; no client data transmitted beyond existing API call pattern.

```
AIC-01 (post-intake pass) ─── AIC-03
AIC-02 (pre-final-run pass) ── AIC-03
AIC-03 (inject into pipeline) ← AIC-01 + AIC-02
```

- [ ] AIC-01 Post-intake Haiku pass: after intake form submit, ask up to 3 follow-up questions conversationally (st.chat_message style); answers to `D_Working_Papers/intake_qa.json`; "Skip for now" button available
- [ ] AIC-02 Pre-final-run Sonnet pass: reviews all accumulated materials; renders 3–5 warning cards; each card: "Resolve" or "Proceed anyway"; results to `D_Working_Papers/prefinalrun_review.json`; pipeline Run button locked until all cards acknowledged
- [ ] AIC-03 `ProjectManager.get_intake_qa_context()` + `get_prefinalrun_context()` — inject into agent context dict

---

### Sprint-RD — Report Design Layer (Session 022 — runs parallel to Phase 9)

**BA:** BA-R-01, BA-R-02, BA-R-03
**Security:** No shell execution; all paths via case_dir() or firm_profile/ constants; template .docx write is atomic (.tmp → os.replace()).

```
RD-01 ──── RD-03, RD-05, RD-06
RD-02 ──── RD-03
RD-04 ──── independent (called by RD-03)
```

- [ ] RD-00 Add `openpyxl>=3.1.0` to `requirements.txt` (also needed for Sprint-FR and Sprint-WF)
- [ ] RD-01 `tools/report_builder.py` — `BaseReportBuilder(template_path=None)`: add_cover_page(), add_toc(), add_section(), add_subsection(), set_header(), set_footer(), save(). Style fallback if template styles incompatible.
- [ ] RD-02 `streamlit_app/shared/template_selector.py` — `render_template_selector(workflow_type)`: check firm.json; if no template → offer "Use my template" / "Build one"; save to `firm_profile/templates/{wf}.docx`; update firm.json
- [ ] RD-03 Update `tools/file_tools.py:write_final_report()` — use BaseReportBuilder; load template via firm.json; apply section_overrides; call _version_existing_report() first
- [ ] RD-04 `tools/file_tools.py` — `_version_existing_report(case_id)`: move existing final_report.* to Previous_Versions/final_report.v{N}.*; create Previous_Versions/ if missing
- [ ] RD-05 Investigation section overrides in `workflows/investigation_report.py` — full 13-section structure per BA-R-05
- [ ] RD-06 FRM section overrides in `workflows/frm_risk_register.py` — Risk Register Table + Heat Map sections via BaseReportBuilder

---

### Sprint-WF — Workflow-Specific Report Sections (Session 022 — GATED on RD-01)

**BA:** BA-R-05, BA-R-06, BA-R-07, BA-R-08

- [ ] WF-01a `tools/project_manager.py` helpers: add_exhibit(), add_lead(), update_lead(), get_open_leads(), get_confirmed_leads()
- [ ] WF-01b Investigation Input Session UI additions: Exhibit Register expander + Leads Register expander with Status selectbox; confirmed lead → Haiku draft finding generation
- [ ] WF-01c `tools/report_sections/investigation.py` — `InvestigationSections`: build_evidence_list(), build_detailed_findings() with Exhibit N footnotes, build_open_leads_section(), build_exhibits_appendix()
- [ ] WF-02 `tools/report_sections/due_diligence.py` — `DDSections`: per-subject and consolidated formats; DD intake subject count + relationship fields; template upload option
- [ ] WF-03 `tools/report_sections/transaction_testing.py` — `TTSections`: build_exceptions_table(), build_summary_page() for parent report embedding, build_excel_exceptions() via openpyxl
- [ ] WF-04 `tools/report_sections/sanctions.py` — `SanctionsSections`: build_hit_detail(), build_false_positive_table(), build_exec_summary(); disposition from firm policy + per-hit override
- [ ] WF-05 `firm_profile/sanctions_disposition_policy.json` — default policy file; editable via Settings page

---

### Sprint-FR — FRM Enhanced Deliverable (Session 022 — GATED on RD-01 + P9-05)

**BA:** BA-R-04, BA-R-09

```
FR-01 ─── FR-02
FR-03 ─── FR-06
FR-04 ─── FR-06, RD-06
FR-05 ← RD-01 ─── RD-06
FR-06 ← FR-02 + FR-03 + FR-04 + FR-05
```

- [ ] FR-01 Stakeholder Input form in Input Session workspace: Name/Role/Key Concern/Risk View form; Save → `D_Working_Papers/stakeholder_inputs.json`; separate file uploader for interview notes
- [ ] FR-02 `ProjectManager.get_stakeholder_context(slug)`; inject into FRM junior system prompt; stakeholders in DOCX Appendix
- [ ] FR-03 `recommendation_depth` field in FRM intake schema + `st.radio` in FRM intake form; default "structured"; passed to pipeline
- [ ] FR-04 `tools/frm_excel_builder.py` — `FRMExcelBuilder`: Sheet 1 Risk Register table + Sheet 2 Heat Map (5×5 ARGB colour-coded); atomic write
- [ ] FR-05 `BaseReportBuilder.add_heat_map(risk_items)` — 5×5 colour-coded DOCX table via python-docx cell shading
- [ ] FR-06 Depth-aware recommendation generation: junior system prompt includes depth instruction; RiskItem.recommendation schema adapts per depth; DOCX builder routes to correct renderer


---

### Sprint-FE — Frontend Impact Tasks (Session 022 — GATED on P9-05 design)

**BA:** BA-FE-01 (MISSING — needs /ba or /ux session before build)
**Scope:** Frontend changes required by Sprint-EMB, Sprint-AIC, Sprint-RD, Sprint-WF, Sprint-FR, Phase 9
**Security:** Same as Phase 8 — localhost:8501, no auth, no new data paths

- [ ] FE-GATE-BA: BA-FE-01 decision required before any Sprint-FE task enters build queue — covers: AI questions stage placement, template selector placement, per-hit review screen, DD intake extensions, P9-05 workspace UX

- [ ] FE-01 All 10 workflow pages: add `ai_questions` stage between intake and running
  - State machine: `intake → ai_questions → running → reviewing → done`
  - AIC-01 output rendered as `st.chat_message` style, one question at a time
  - "Skip" button advances to running stage
  - Affects: pages/2, 4, 5, 6, 7, 8, 0, 11, 12, 13

- [ ] FE-02 `pages/settings.py` — add Template Selector section
  - One `render_template_selector(workflow_type)` per workflow type (FRM, Investigation, DD, TT, Sanctions, Proposal)
  - Saves to `firm_profile/firm.json["templates"][workflow_type]`

- [ ] FE-03 `pages/6_FRM.py` — Done stage: add second download button for Excel (.xlsx)
  - `st.download_button("Download Risk Register (.xlsx)", ...)` alongside existing DOCX button

- [ ] FE-04 `pages/12_Sanctions.py` — add per-hit review stage
  - New stage between pipeline and Done: one expander per entity hit
  - Disposition selectbox per hit: True Match / False Positive / Requires Investigation / Escalate
  - Firm default pre-loaded from `sanctions_disposition_policy.json`; consultant can override
  - "Confirm all dispositions" → triggers final report write

- [ ] FE-05 `pages/11_Due_Diligence.py` — extend intake form
  - Add: subject count (`st.number_input`), relationship type (`st.radio`: Unrelated / Related), DD template upload (`st.file_uploader` for .docx)
  - Route to per-subject or consolidated format based on subject count + relationship

- [ ] FE-06 P9-05 Input Session workspace — full UX design pass required
  - Conditional panels by workflow type:
    - All workflows: semantic search bar (EMB-03), AIC follow-up panel, context budget bar
    - FRM only: stakeholder input form (FR-01)
    - Investigation only: exhibit register + leads register (WF-01b)
  - Build order: shared panels first, then workflow-specific panels

- [ ] FE-07 Case Tracker + Project workspace — surface Previous_Versions/
  - In project detail expander: "Previous Versions" section listing versioned reports with download buttons
  - Only shown if `Previous_Versions/` folder exists in project root

---

### Sprint-TPL — Report Template System (Session 024)

**BA:** BA-TPL-01, BA-TPL-02
**Security:** Template uploads are .docx only — validate magic bytes (PK header), size cap 5MB, no macro execution. Template path resolution must not escape `firm_profile/templates/` directory (R-019 pattern). Base templates are read-only — never deletable.
**Note:** `templates.json` already exists in `firm_profile/templates/` with 8 workflow slots. `OutputGenerator.generate_docx()` already accepts `template_path=None`. Sprint-TPL formalises the manager layer, Settings UI, and intake selector on top of this foundation.

```
TPL-01 (TemplateManager) ─── TPL-02, TPL-03, TPL-04, TPL-05
TPL-02 (output_generator) ─── TPL-05
TPL-03 (settings tab) ──────── TPL-05
TPL-04 (intake selector) ───── TPL-05
```

- [ ] **[TPL-01]** Create `tools/template_manager.py` — `TemplateManager` class: `resolve(workflow_type, custom_path=None) -> Path` (fallback chain: custom → base → raise); `validate_docx(path) -> ValidationResult` (magic bytes PK check, ≤5MB, python-docx open, check all 7 required styles: GW_Title, GW_Heading1, GW_Heading2, GW_Body, GW_TableHeader, GW_Caption, GW_Disclaimer); `update_custom(workflow_type, file_bytes) -> Path` (version-rotates existing `_custom.docx` to `_custom.v{N}.docx`, saves new file atomically); `list_templates() -> dict` (reads `firm_profile/templates/templates.json`, returns per-workflow slot with base/custom/versions). Reads/writes `firm_profile/templates/templates.json`. All path operations confined to `firm_profile/templates/` — any path traversal attempt raises ValueError. ← deps: none | AC: `TemplateManager().resolve("frm_risk_register")` returns path ending in `frm_risk_register_base.docx` when no custom exists; `resolve("frm_risk_register", custom_path="../../evil")` raises ValueError; `validate_docx()` returns ValidationResult with `missing_styles` list when styles absent.

- [ ] **[TPL-02]** Update `tools/output_generator.py` — `generate_docx()` to call `TemplateManager().resolve(workflow_type)` when `template_path=None`; apply named styles from template (GW_Title for cover, GW_Heading1 for h1, GW_Heading2 for h2, GW_Body for paragraphs) when template is loaded and styles exist; fall back silently to current basic styling if named style is absent from template; log resolution event to audit_log via `{event: "template_resolved", template: "<filename>", fallback: true/false}`. ← deps: TPL-01 | AC: `generate_docx(content_md="# Title\n\nBody", output_path=..., workflow_type="frm_risk_register")` uses base template and does not crash; audit event `template_resolved` written with `fallback: false` when base template applied.

- [ ] **[TPL-03]** Update `pages/settings.py` — redesign as 4-tab layout `st.tabs(["Firm Profile", "Pricing", "Team & T&C", "Report Templates"])` per UX-018. Tab 4 (Report Templates): render one row per workflow type (Investigation, Due Diligence, FRM, TT, Sanctions, Proposal) showing current template filename, last updated timestamp, and three inline actions — "Upload Custom" (opens conditional `st.file_uploader` for that row), "Preview" (popover showing detected styles from `validate_docx()`), "Reset to Base" (with explicit confirmation). Upload validation fires on upload event: pass → st.success; partial (missing non-critical styles) → st.warning + proceed allowed; fail (missing GW_Heading1 or GW_Body) → st.error + save blocked. Completeness badge at top of page (above tabs): 5 chips — Firm Profile / Pricing / Team / T&C / Templates — green/amber/grey. ← deps: TPL-01 | AC: Tab 4 renders 6 workflow rows; upload of a valid .docx with all 7 styles → st.success + templates.json updated; upload of .docx missing GW_Heading1 → st.error + no file saved; Reset to Base requires explicit "Confirm Reset" button click before deletion.

- [ ] **[TPL-04]** Add template selector to `streamlit_app/shared/intake.py` — `template_selector(st, workflow_type) -> Optional[Path]`. Renders as collapsed `st.expander("Report template", expanded=False)` per UX-019, positioned below last intake field and above Run button. Radio group: (a) "Use saved template: {filename}" — shown only if custom exists for workflow type, pre-selected by default if available; (b) "Upload for this engagement only" — always shown, reveals inline `st.file_uploader`; (c) "Plain Word output (no template)" — always shown, pre-selected if no custom exists. Confirmation caption below radio showing selected template and scope. Session state: selected path stored in `st.session_state["report_template_path"]`; one-time bytes in `st.session_state["report_template_bytes"]`. Template selection event written to audit_log at Run click: `{event: "template_selected", workflow, template, scope: "global"|"one_time"|"none"}`. Add `template_selector()` call to all workflow pages that generate docx output. ← deps: TPL-01 | AC: workflow page with no custom template shows only options (b) and (c); option (a) pre-selected when custom exists; option (b) with no file uploaded disables Run button; selection written to audit_log on Run.

- [ ] **[TPL-05]** AC smoke test — FRM pipeline generates `F_Final/final_report.docx` using `frm_risk_register_base.docx`; open file in python-docx and confirm at least one paragraph with style matching a GW_ style name is present; audit_log contains `template_resolved` event with `fallback: false`; `templates.json` shows correct base filename in `frm_risk_register.base` slot. ← deps: TPL-01, TPL-02, TPL-03, TPL-04 | AC: smoke test script runs without exception and all three assertions pass.

---

### Sprint-EMB — Semantic Embeddings Layer — UPDATED (Session 024 refinements)

**Note:** Sprint-EMB tasks EMB-00 through EMB-04 already written above (Session 022 entries). The tasks below refine and extend the existing entries based on BA-EMB-01 (Session 024 BA pass).

- [ ] **[EMB-01-REF]** Refine `EmbeddingEngine` spec per BA-EMB-01: class takes `case_id`; `embed_document(doc_entry: DocumentEntry)` chunks at 800-char boundary with 80-char overlap; `retrieve(query, case_id, top_k=5) -> list[ChunkResult]` where `ChunkResult` has `chunk_text`, `source_doc_id`, `source_filename`, `chunk_index`, `source_citation` (formatted as `{filename}, chunk {n}`); two-layer fallback — (1) `ImportError` on `sentence_transformers` → `self.available = False`, log warning, no crash; (2) download error (first-run model download fails) → same `self.available = False`. 8000-char cap on total retrieved context per query. ← deps: EMB-00 | AC: `EmbeddingEngine("test-case")` with sentence-transformers absent → `engine.available == False` and `retrieve()` returns `[]` without raising; with library available, `retrieve("fraud indicators")` returns list of `ChunkResult` with non-empty `source_citation`.

- [ ] **[EMB-02-REF]** Refine DocumentManager wire-up per BA-EMB-01: `register_document()` calls `EmbeddingEngine.embed_document()` synchronously (spinner shown in Streamlit during upload per BA open-question resolution — synchronous v1); add `embedding_status: Literal["indexed","pending","failed","unavailable"]` field to `DocumentEntry` schema; if `EmbeddingEngine.available == False` → set status `"unavailable"`, skip embed, no crash; if embedding raises → set status `"failed"`, log warning, return normally. ← deps: EMB-01-REF | AC: `DocumentEntry` has `embedding_status` field; registering a document with engine unavailable returns `embedding_status="unavailable"`; registering with engine available returns `embedding_status="indexed"`.

- [ ] **[EMB-03-REF]** Embedding status badge in Streamlit per UX-013: add `embedding_status` badge to document list in (a) Input Session workspace document panel, (b) Case Tracker detail expander. Badge states: "Indexed — {N} chunks" (green), "Pending" (amber), "Failed" (red), "Unavailable — embedding library not installed" (grey). On hover/expand: chunk count, model name, indexed_at timestamp if available. ← deps: EMB-02-REF | AC: document registered with `embedding_status="indexed"` shows green badge with chunk count; `"unavailable"` shows grey badge with install hint text.

---

### Sprint-P9 — Phase 9 Schema Foundation (Session 024 — refines existing P9-01 tasks)

**Note:** P9-01a/b/c tasks are already written above in the Phase 9 section. The tasks below are the ADDITIONAL tasks designed in Session 024 (BA-P9-01, BA-P9-02, BA-P9-03 extended specs).

- [x] **[P9-01-SLUG]** `schemas/project.py` — `ProjectIntake` Pydantic validator on `project_slug` (7-step): (1) strip leading/trailing whitespace; (2) lowercase; (3) replace spaces and underscores with hyphens; (4) strip all characters not in `[a-z0-9-]`; (5) collapse multiple consecutive hyphens to one; (6) strip leading/trailing hyphens; (7) raise ValueError if result is empty. Allowlist post-validation: raise ValueError if slug contains `..`, `/`, `\`, null byte `\x00`. This is R-019 mitigation. ← deps: none | AC: `"Project Alpha / FRM"` → `"project-alpha-frm"`; `"../etc/passwd"` → ValueError; `"   "` → ValueError; `"__test__"` → `"test"`; `"valid-slug"` → `"valid-slug"`.

- [x] **[P9-01-SESSION]** `schemas/project.py` — `InputSession`: `session_id: str`, `project_slug: str`, `mode: Literal["input","final_run"]`, `status: Literal["open","closed","abandoned","error"]` (4-state lifecycle), `started_at: datetime`, `closed_at: Optional[datetime]`, `documents_registered: list[str]`, `notes_path: Optional[str]`, `key_facts_count: int = 0`, `red_flags_count: int = 0`. Path for session log: `cases/{project_slug}/D_Working_Papers/session_log.jsonl`. ← deps: P9-01-SLUG | AC: `InputSession(project_slug="test", mode="input", status="open", started_at=datetime.now(), session_id="s1", documents_registered=[])` validates with no error; `status="invalid"` raises ValidationError.

- [x] **[P9-01-STATE]** `schemas/project.py` — `ProjectState`: `project_slug: str`, `status: CaseStatus`, `project_health: Literal["green","amber","red"]` (enum), `cases: dict[str, str]` (workflow_type → case_id mapping), `sessions: list[InputSession]`, `language_standard: str = "acfe"`, `context_budget_used_pct: float = 0.0`, `interim_context_written: bool = False`, `last_updated: datetime`, `is_legacy: bool = False` (backward-compat UUID flag for pre-P9 cases). Update triggers: `last_updated` auto-updates on any state change. ← deps: P9-01-SESSION | AC: `ProjectState` imports cleanly; `project_health="invalid"` raises ValidationError; `is_legacy` defaults to False; `cases` dict is empty dict by default (not None).

- [x] **[P9-01-AC]** Import smoke test + security tests for `schemas/project.py`: `from schemas.project import ProjectIntake, InputSession, ProjectState` succeeds; path traversal test `ProjectIntake(project_name="../etc/passwd", ...)` raises ValueError; empty slug `ProjectIntake(project_name="   ", ...)` raises ValueError; invalid language standard `ProjectIntake(language_standard="invalid")` raises ValidationError; run as `python -m pytest tests/test_project_schema.py -v` (create minimal test file if none exists). ← deps: P9-01-SLUG, P9-01-SESSION, P9-01-STATE | AC: all 4 assertions pass; test file runs without import errors.

---

### Sprint-WORK — Interim Workpaper Generation (Session 024)

**BA:** BA-WORK-01 — CONFIRMED 2026-04-19
**Security:** Reads persisted artifacts only — no new API calls unless explicitly triggered by Maher. ANALYTICAL INFERENCE label is a data integrity requirement. Output written to `D_Working_Papers/` only — not E_Drafts or F_Final (unless promoted). Workpaper generation does NOT transition CaseState unless Maher promotes to final.
**AK decisions locked:** (1) Trigger: any point after Junior draft exists — mid or post pipeline; (2) Structure: Maher-driven, presents 9 sections as opt-in/opt-out at generation time; (3) Promotion: workpapers can be promoted to final report → written to F_Final/ with PROMOTED_FROM_WORKPAPER audit flag.
**Gate:** UNBLOCKED — ready to build.

```
WORK-01 (WorkpaperGenerator) ─── WORK-02, WORK-03
```

- [ ] **[WORK-01]** Create `workflows/workpaper.py` — `WorkpaperGenerator` class: `generate(case_id: str, source_artifacts: dict) -> Path`. Single Sonnet call. System prompt hardcodes ACFE Internal Review language standard and instructs: "Every finding must cite at least one registered document by doc_id and filename. If no documentary support exists, label the finding 'ANALYTICAL INFERENCE — no documentary evidence found yet'." 9-section structure per BA-WORK-01: (1) Header with PRELIMINARY watermark; (2) Materials reviewed (from DocumentIndex); (3) Key facts (from key_facts.json); (4) Red flags (from red_flags.json, sorted high→medium→low); (5) Emerging findings (Sonnet-generated, 3–7 items, each with evidence citation); (6) Leads register status (from leads_register.json); (7) Open questions (from findings + open leads + intake_qa); (8) Next steps (Sonnet-generated, 3–5 items); (9) Audit trail summary (session count, document count, facts count). Output: `.md` only (no DOCX for workpapers per BA-WORK-01 out-of-scope). Saved to `D_Working_Papers/interim_workpaper.v{N}.md` (N = next available integer, never overwrites). Appends `WORKPAPER_GENERATED` event to `audit_log.jsonl` with version and model used. ← deps: P9-01-STATE (for ProjectState), EMB-01-REF (optional retrieval) | AC: `generate()` produces a .md file in D_Working_Papers/; file contains "PRELIMINARY" watermark text; findings without doc citations are labelled "ANALYTICAL INFERENCE"; audit_log contains `WORKPAPER_GENERATED` event; calling `generate()` twice creates `v1.md` and `v2.md` — no overwrite.

- [ ] **[WORK-02]** Trigger in Case Tracker — "Generate Workpaper" button in detail expander per UX-015: visible for cases with status `JUNIOR_DRAFT_COMPLETE` or `PM_REVIEW_COMPLETE`. Button calls `WorkpaperGenerator.generate(case_id, source_artifacts)` where source_artifacts are loaded from case folder E_Drafts (junior_output.v*.json, pm_review.v*.json). Shows download button in Case Tracker detail expander after generation: `st.download_button("Download Workpaper (.md)", ...)` with filename pattern `workpaper_{case_id}_{YYYYMMDD}.md`. Greyed out (disabled, tooltip "No draft material yet") for cases with status `INTAKE_CREATED`. Not shown for terminal states (`OWNER_APPROVED`, `DELIVERABLE_WRITTEN`). ← deps: WORK-01 | AC: button visible for `JUNIOR_DRAFT_COMPLETE` case; button absent for `INTAKE_CREATED` case; generated file downloadable from tracker without navigating to case folder.

- [ ] **[WORK-03]** Secondary trigger in pipeline done stage — secondary `st.button("Generate Interim Workpaper")` below primary download button on Investigation and FRM done stages per UX-015. Calls same `WorkpaperGenerator.generate()`. Shows inline `st.spinner("Generating workpaper...")` during generation. Renders a second download button for the workpaper after generation. Does not re-trigger the pipeline. ← deps: WORK-01 | AC: button present on FRM done stage and Investigation done stage; clicking generates workpaper without any agent pipeline re-run (verify by checking audit_log — no new Junior/PM/Partner events); workpaper download available immediately after generation.

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

- [ ] **[CONV-01]** Create `workflows/evidence_chat.py` — `EvidenceChat` class: `chat(case_id: str, message: str, selected_doc_ids: list[str], conversation_history: list[dict]) -> str`. Single Sonnet turn. System prompt: "You are reviewing the documents registered for this forensic engagement. You can only present findings and observations directly supported by the registered documents. For each observation, state the source document and quote the relevant passage. You may explain forensic concepts and fraud patterns as background context. You must not present inferences as conclusions. All observations are preliminary." Context injection per turn (capped at `config.CEM_CONTEXT_CHARS` = 16,000 chars): (1) DocumentIndex summary of all registered docs; (2) key_facts.json and red_flags.json content; (3) `EmbeddingEngine.retrieve(message, case_id, top_k=5)` chunks if embedding available, else `DocumentManager.find_relevant_docs()` excerpt; (4) conversation history (oldest turns dropped first when cap approached). Document-scoped mode: if `selected_doc_ids` is non-empty, retrieval filtered to those doc_ids only. Saves full conversation turn to `D_Working_Papers/evidence_chat_{YYYYMMDD_HHMMSS}.md` on each session_end call (append-only; new CEM session = new file). Auto-save to `evidence_chat_{timestamp}_recovered.md` on mid-session app close. ← deps: EMB-02-REF | AC: `chat(case_id, "What does the bank statement show?", [], [])` returns a non-empty string; system prompt injection confirmed via code inspection; context cap of 16000 chars enforced (verify by unit test with large doc); conversation save creates file in D_Working_Papers/.

- [ ] **[CONV-02]** Create `pages/14_Evidence_Chat.py` (or tab within Investigation per UX-D-07 decision — build as standalone page, refactor to tab if AK decides option B post-build). Two-panel layout per UX-014: Left panel (1/3 width) — document selector loaded from `DocumentManager` index for active case (`st.session_state.active_project` or case_id picker if no active project); each document has a checkbox "Include in context"; shows embedding status badge per EMB-03-REF. Right panel (2/3 width) — chat interface: `st.chat_input("Ask about the evidence...")` + `st.chat_message()` rendering (user and assistant). Per assistant response: three action buttons below the message — "Save as Lead" (appends to leads_register.json + audit event), "Save as Key Fact" (appends to key_facts.json), "Save as Red Flag" (severity selectbox appears before saving). "Flag Response" button appends `FLAGGED` annotation to conversation transcript. Persistent banner at top of right panel: `st.warning("Evidence Exploration Mode — outputs are not reviewed deliverables. Use the Investigation pipeline for reviewed reports.")`. Conversation persists across sessions via `cases/{id}/evidence_chat.jsonl` (new file per session). History trimming banner shown when >50 turns: `st.info("Older turns have been trimmed from context. Full transcript saved to Working Papers.")`. "End Conversation" button closes session and triggers conversation save. ← deps: CONV-01, EMB-02-REF | AC: page loads without error when no active case; chat input sends message and renders response; "Save as Lead" button appends to leads_register.json (verify file exists and has entry); "NOT FOR CLIENT REVIEW" equivalent warning banner present; conversation saved to evidence_chat_{timestamp}.md on "End Conversation" click.

---

### Sprint-UX-FIXES — High-Priority UX Fixes (Session 024)

**UX source:** UX-007 through UX-011, UX-016, UX-017 (all Session 024 review findings)
**Security:** No new data paths. No schema changes. UI layer only.
**Note:** These tasks can run in parallel with all other sprints — no schema or tool dependencies.

- [ ] **[UX-F-01]** Renumber pages + add sidebar section dividers per UX-007: rename page files to eliminate gaps and create groupings (01_Investigation, 02_Persona_Review, 03_Scope → or per AK-approved mapping TBD); inject sidebar section headers in `streamlit_app/shared/session.py` bootstrap via `st.sidebar.markdown` — "INVESTIGATION", "COMPLIANCE", "BUSINESS", "UTILITIES" labels with dividers above each group. Add `st.info("Run Scope first for any new engagement...")` callout on 0_Scope.py. Add `st.page_link()` calls to landing page workflow grid (Streamlit 1.31+; fallback to markdown links if unavailable). Move Case Tracker to sidebar position just before Settings/Team. ← deps: none | AC: sidebar shows section dividers visible in browser; no page-number gaps in sidebar nav; Scope page shows "Start here" callout.

- [ ] **[UX-F-02]** Workflow-specific intake labels + DD merged form per UX-008: update `generic_intake_form()` to accept `submit_label` param mapped from `workflow_id` (e.g. "Run Investigation", "Draft Proposal", "Begin Scoping"); add `placeholder` text to description field per workflow_id map; merge Due Diligence generic + specific fields into single `dd_intake_form()` (eliminates two-phase render); move FRM module dependency enforcement to `st.on_change` callback on multiselect (auto-add Module 2, show inline `st.info()` without clearing form). ← deps: none | AC: FRM page shows "Module 2 added automatically" inline on multiselect change without form submit; DD page renders all fields in one form (no second form appearing after submit); Investigation Run button labelled "Run Investigation" not "Start".

- [ ] **[UX-F-03]** Progress bar + agent label mapping + failure log capture per UX-009: add `st.progress()` bar above status block in running stage (3-step: 33% after Junior start event, 66% after PM start, 100% after Partner complete; FRM: step per module × 3); map internal agent IDs to user-facing labels in `run_in_status()` or `PipelineEvent` construction (`junior_analyst` → "Consultant (Draft)", `pm_review` → "Consultant (Review)", `partner` → "Consultant (Sign-off)"); add static estimated time caption at run start: `st.caption("Estimated time: 2–4 minutes...")`; on pipeline failure, add `st.expander("View pipeline log")` rendering last N events captured in `st.session_state["pipeline_log_events"]` (store events during `on_progress` callbacks). ← deps: none | AC: progress bar visible during FRM run (verify by inspection); agent label "Consultant (Draft)" appears in log (not "junior_analyst"); failure expander appears on pipeline error state.

- [ ] **[UX-F-04]** Inline report preview + copy case ID + "Start Another" in Zone C per UX-010: add `st.expander("Preview report", expanded=False)` in done stage containing `st.markdown(report_text[:3000])` with "Show more" toggle; add "Copy Case ID" button (or render case_id as `st.code()` for easy selection) next to case ID display; collapse `**Location:** cases/{id}/` into "Technical details" expander; add primary "Start Another [Workflow Name]" button in Zone C main content area (not sidebar-only); for FRM done-stage rewrites, update spinner text to `f"Applying {rewrite_count} rewrite(s)..."`. ← deps: none | AC: done stage shows report preview expander; case ID displayed in selectable format; "Start Another FRM" button present in main content below download; location path hidden by default in collapsed expander.

- [ ] **[UX-F-05]** Case Tracker — status label mapping + dataframe row selection + Client column + engagement_id scaffold per UX-011: add `_STATUS_LABELS` dict mapping all CaseStatus values to human-readable strings ("Draft Ready", "Under Review", "Approved", "Error — action needed" etc.); replace `st.selectbox` detail driver with `st.dataframe(on_select="rerun", selection_mode="single-row")` (Streamlit 1.35+; fall back to selectbox if version check fails); add "Client" column to dataframe populated from `client_name` in index; add `engagement_id` column to `cases/index.json` schema (null for all existing cases — Phase 9 ready scaffold); add "Resume / Open" button in detail expander using `st.switch_page()` mapped from workflow key to page path. ← deps: none | AC: tracker shows "Draft Ready" not "JUNIOR_DRAFT_COMPLETE"; Client column visible; row click drives detail panel without requiring separate selectbox interaction; engagement_id field present in index (null for legacy cases).

- [x] **[UX-F-06]** Visual design — create `.streamlit/config.toml` + fix h2/h3 selector + wire severity CSS per UX-016: create `/Users/akaushal011/forensic-ai/.streamlit/config.toml` with `[theme]` block (`primaryColor="#D50032"`, `backgroundColor="#FFFFFF"`, `secondaryBackgroundColor="#F5F2F0"`, `textColor="#282827"`, `font="sans serif"`); fix CSS selector in `session.py` `_CSS` to target `h2, h3` (not h2 only) for red bottom border; wire severity CSS classes in `pipeline.py` `_render_event()`: CRITICAL → `st.markdown('<div class="severity-critical">...</div>', unsafe_allow_html=True)`, WARNING → same with `severity-warning`; add sidebar footer: `st.sidebar.caption(f"GoodWork Forensic AI · {today}")`; remove button color overrides from `_CSS` that now duplicate config.toml. ← deps: none | AC: `.streamlit/config.toml` exists with correct keys; browser shows #D50032 primary color on first load (not CSS-injected); CRITICAL events in pipeline log show left-border accent style; `st.subheader()` text shows red underline (h3 rule now applied).

- [ ] **[UX-F-07]** Settings completeness + T&C textarea + firm.json consolidation per UX-017: add `tc_text` field to Settings page as `st.text_area("Standard Terms & Conditions", height=300)` with helper text; store in `firm.json["tc_text"]`; add completeness indicator at top of Settings page — visual checklist of 5 items (Firm Name, Logo, Pricing, T&C, Team) with green/amber/grey states; in Proposal workflow intake, add pre-flight check: read `firm.json`, if firm_name blank → `st.warning("Firm profile incomplete — go to Settings...")` with `st.page_link()` to Settings; add roadmap item to consolidate `firm_profile.json` and `pricing_model.json` into `firm.json` (mark as REFACTOR-01 in todo, do not implement now). ← deps: none | AC: Settings page shows completeness indicator above tabs; T&C textarea saves to firm.json; Proposal page shows warning when firm_name is blank; REFACTOR-01 logged in todo.md.

---

### Sprint-P9-UI — Phase 9 Engagements UI (Session 024)

**UX:** UX-012
**AK decision locked (2026-04-19):** New `01_Engagements.py` as top-level home. `0_Scope.py` becomes a step inside New Engagement flow — not standalone. Premium two-panel engagement dashboard.
**Gate:** UNBLOCKED — ready to build after P9-01 schemas complete.
**Security:** Same as Phase 8 — localhost:8501, single user; all data in `projects/{slug}/`; slug used only via validated path from P9-01a.

- [ ] **[P9-UI-01]** Create `pages/01_Engagements.py` — two-panel engagement home per UX-012. Left panel (1/3 width): list of named engagement cards from `ProjectManager.list_projects()` — each card shows Engagement Name, Client, Status (health roll-up: green all-done, amber any-error, blue in-progress), Last Activity. "New Engagement" button at top of left panel. Right panel (2/3 width): selected engagement detail — shows all cases under engagement as mini-tracker (workflow type, status, last updated), plus "Run New Workflow" button that routes to relevant workflow page with `active_project` pre-set in session_state. Empty state (no engagements): `st.info("No engagements yet. Start your first engagement.")` with prominent "New Engagement" button spanning both panels. "New Engagement" wizard: multi-field form (Project Name, Client Name, Service Type selectbox, Language Standard selectbox — 4 options per BA-P9-05, Naming Convention); slug preview shown as `st.caption("Folder name: cases/{slug}/")` updating on keystroke; collision detection before `create_project()` call; on success: `st.success("Engagement created: cases/{slug}/")` + list of 6 created subfolders. ← deps: P9-01-SLUG, P9-01-STATE, P9-02 (all from Phase 9 section above) | AC: page loads without error; "New Engagement" form creates `cases/{slug}/` with 6 subfolders; collision warning shown if slug exists; engagement cards visible after creation; "Run New Workflow" sets `st.session_state.active_project`.

- [ ] **[P9-UI-02]** Wire `engagement_id` / `active_project` into all workflow intake pages — add "Continue Engagement" option at top of intake form on all workflow pages: if `st.session_state.active_project` is set, show `st.info("Continuing engagement: {project_name} — client: {client_name}")` banner and pre-fill `client_name`, `language_standard` from project context; lock those fields (render as `st.text()` not `st.text_input()`). If no `active_project`: existing behavior unchanged (standalone case with UUID, backward compat). Add `engagement_id` to `state.json` at case creation if `active_project` is set. ← deps: P9-UI-01, P9-01-STATE | AC: workflow page with `active_project` set shows pre-filled client name and "Continuing engagement" banner; field is read-only (not editable); without `active_project`, page behaves identically to Phase 8 behavior; `state.json` contains `engagement_id` matching project slug when created via engagement context.

---

### Sprint-SETUP — First-Run Setup Page (Session 024 — SHIP BLOCKER — runs BEFORE Phase A)

**BA:** BA-SETUP-01 — CONFIRMED 2026-04-19
**Security:** .env written at runtime — must use load_dotenv(override=True) + config.reload() pattern. setup.json is a cache not authority. No lockout on corrupt/missing setup.json.
**Gate:** UNBLOCKED. Must complete before any other sprint — this is the ship blocker.

- [x] **[SETUP-00]** Consolidate firm profile config: rename `firm_profile/firm_profile.json` references in `core/setup_wizard.py` and `run.py` to read `firm_profile/firm.json` — same file Streamlit uses. Add `config.reload()` function to `config.py` that calls `load_dotenv(override=True)` and rebuilds API clients. ← deps: none | AC: `python run.py` and `streamlit run app.py` both read from `firm_profile/firm.json`; no references to `firm_profile.json` remain outside setup_wizard.py CLI path.

- [x] **[SETUP-01]** Create `streamlit_app/shared/readiness.py` — `check_readiness() -> ReadinessResult` dataclass: checks all 5 conditions (`.env` + ANTHROPIC_API_KEY, `firm.json` + firm_name, `team.json` + one member, `pricing_model.json`, `assets/templates/base_report_base.docx`). Returns `{ready: bool, missing: list[str], setup_json_rebuilt: bool}`. If setup.json missing/corrupt: rebuild silently. ← deps: SETUP-00 | AC: function returns `ready=True` on a correctly set up install; returns `ready=False, missing=["ANTHROPIC_API_KEY"]` when .env is empty; missing setup.json → rebuilt not lockout.

- [x] **[SETUP-02]** Create `pages/00_Setup.py` — 5-step guided setup wizard in Streamlit. Step 1: API keys (ANTHROPIC required, TAVILY optional, test connection button). Step 2: Firm Profile (name required, logo optional). Step 3: Team (at least one member required). Step 4: Pricing model (required). Step 5: Review all + complete button that calls `config.reload()` then `st.switch_page("app.py")`. Progress indicator showing steps completed. ← deps: SETUP-01 | AC: clean install with empty firm_profile/ → setup page renders; completing all steps writes correct files; incomplete required step → blocked with exact error; TAVILY skip → allowed; app redirects to landing after completion.

- [x] **[SETUP-03]** Update `streamlit_app/shared/session.py` bootstrap() — add readiness check at top: call `check_readiness()`, if `not ready` and current page is not `00_Setup.py` → `st.switch_page("pages/00_Setup.py")`. ← deps: SETUP-01, SETUP-02 | AC: fresh install redirects to setup page on any page load; completed install never redirects; deleted setup.json on working install → no redirect (readiness rebuilt from artifacts).

---

### Sprint-TEST — Minimum Test Surface (Session 024 — required before Maher live use)

**Security:** Tests must not use real API keys — mock all external calls. Test fixtures must not contain real client data.
**Gate:** UNBLOCKED. Run after Phase B completes (schemas and core stable).

- [ ] **[TEST-01]** Create `tests/` directory + `tests/conftest.py` with shared fixtures (temp case dir, mock config, mock API clients). ← deps: none | AC: `pytest tests/` runs without import errors.

- [ ] **[TEST-02]** `tests/test_state_machine.py` — test all valid transitions, all invalid transitions (expect TransitionError), is_terminal() for all states, MAX_REVISION_ROUNDS enforcement. ← deps: TEST-01 | AC: 100% branch coverage of core/state_machine.py.

- [ ] **[TEST-03]** `tests/test_file_tools.py` — test case_dir() path traversal (expect ValueError on `../../etc`), write_artifact() atomic write (tmp→replace), write_state() + read_state() roundtrip, build_case_index() with 0/1/N cases, append_audit_event() append-only (verify file grows, never shrinks). ← deps: TEST-01 | AC: path traversal test explicitly tries `../` and confirms ValueError; atomic write verified by checking no .tmp file remains after success.

- [ ] **[TEST-04]** `tests/test_post_hooks.py` — test validate_schema() blocks on missing required fields, persist_artifact() writes to correct path, append_audit_event_hook() appends correct JSON structure, extract_citations() populates citations_index.json. ← deps: TEST-01 | AC: each hook tested in isolation with mock payload; blocking hooks raise HookVetoError on bad input.

- [ ] **[TEST-05]** `tests/test_project_schema.py` (P9-01-AC) — ProjectIntake slug validation (7-step algorithm), path traversal attempts, empty slug rejection, InputSession lifecycle states, ProjectState health enum. ← deps: TEST-01 | AC: `../../etc/passwd` as project_name raises ValueError; empty string raises ValueError; valid name produces correct slug.

- [ ] **[TEST-06]** `tests/test_output_generator.py` — generate_docx() produces a valid .docx file, template_path=None uses base template, named styles present in output. ← deps: TEST-01 | AC: generated file opens with python-docx without error; file size > 0; no .tmp file remains.

- [ ] **[TEST-07]** Workflow smoke tests — `tests/test_workflow_smoke.py`: run_engagement_scoping_workflow(), run_due_diligence_workflow(), run_frm_pipeline() each called with mock agents returning stub artifacts. Verify: state transitions fire, audit events written, final file written to correct path. ← deps: TEST-01 | AC: each workflow completes without exception; audit_log.jsonl contains expected events; final_report.en.md exists in temp case dir.

---

### Sprint-KL — Three-Layer Knowledge Architecture (Session 024)

**BA:** BA-KL-01 — CONFIRMED 2026-04-19
**Gate:** UNBLOCKED after Sprint-EMB (needs ChromaDB). Design only in Phase A; build Phase D onwards.

- [ ] **[KL-00]** Create `knowledge/manifest.json` — index of all knowledge files with doc_id, domain, version, effective_date, supersedes, authority_level. ← deps: none | AC: manifest.json validates against a KnowledgeManifestEntry schema; all existing knowledge/*.md files have entries.

- [ ] **[KL-01]** Create `tools/knowledge_retriever.py` — `KnowledgeRetriever` class: `retrieve(query, case_context) -> KnowledgeBundle`. Queries all three ChromaDB collections (kb_base, kb_user_sanitised, kb_engagement). Returns structured bundle with base_hits, user_hits, engagement_hits, and rules dict per BA-KL-01 retrieval contract. Falls back gracefully if any collection is empty or unavailable. ← deps: EMB-01, KL-00 | AC: returns valid KnowledgeBundle with all three arrays (empty arrays acceptable); BASE layer always returns results if kb_base is indexed; empty USER/ENGAGEMENT layers return empty arrays not errors.

- [ ] **[KL-02]** Engagement harvest pipeline — `tools/knowledge_harvester.py`: `harvest_case(case_id)` runs after OWNER_APPROVED. Extracts approved patterns to `cases/{id}/knowledge_export/approved_patterns.json`. Promotes to `firm_profile/knowledge/engagement/index.jsonl`. Never extracts client identifiers or raw evidence text. ← deps: KL-01 | AC: harvest_case() on approved case produces approved_patterns.json; file contains no client name, no case_id reference in content fields; audit event written.

---

### Sprint-ACT — Activity Ledger (Session 024)

**BA:** BA-ACT-01 — CONFIRMED 2026-04-19
**Security:** logs/ is gitignored for *.jsonl. Log writes are fire-and-forget — never crash the app. No PII in detail fields. Access: open (Path A).
**Gate:** UNBLOCKED. Build in Phase D (after Phase C schemas stable).

- [ ] **[ACT-00]** Create `logs/` directory with `logs/.gitkeep`. Add `logs/*.jsonl` to `.gitignore`. ← deps: none | AC: `logs/` present in repo; `.gitkeep` tracked; activity.jsonl gitignored.

- [ ] **[ACT-01]** Create `tools/activity_logger.py` — `ActivityLogger` class with `log(category, action, actor, engagement_id, case_id, detail, status)` method. Writes to `logs/activity.jsonl` append-only. Log rotation: when file exceeds 50MB rename to `logs/activity_{YYYYMMDD}.jsonl` and start new file. On write failure: emit `st.session_state["act_log_warn"] = True` and continue silently. Categories: SESSION, SETUP, ENGAGEMENT, PIPELINE, DOCUMENT, DELIVERABLE, KNOWLEDGE, TEMPLATE, SETTINGS, ERROR. ← deps: ACT-00 | AC: log() writes valid JSONL event (all fields present, ISO-8601 timestamp, uuid4 event_id); rotation triggers at 50MB; write failure does not raise; `logs/activity.jsonl` gitignored but logs/.gitkeep committed.

- [ ] **[ACT-02]** Wire ActivityLogger into bootstrap() and all pipeline on_progress callbacks — SESSION/PIPELINE events. Wire into 00_Setup.py — SETUP events. Wire into file_tools.py write_artifact() — DOCUMENT/DELIVERABLE events. Wire into settings pages — SETTINGS events. ← deps: ACT-01, SETUP-03 | AC: running a pipeline end-to-end produces ≥5 activity events in logs/activity.jsonl covering SESSION, PIPELINE, DELIVERABLE categories; settings change produces SETTINGS event with old_value + new_value fields.

- [ ] **[ACT-03]** Create `pages/07_Activity_Log.py` — per UX-020. Date range picker + category multiselect + free-text search. Paginated 50 events per page. Export as CSV button. Sidebar warning if `st.session_state.get("act_log_warn")` is True. ← deps: ACT-01 | AC: page renders with empty log (shows "No activity recorded yet"); date filter correctly narrows events; category filter works independently and in combination with date; CSV export produces valid file with all visible events; corrupt log file shows error message, does not crash.

