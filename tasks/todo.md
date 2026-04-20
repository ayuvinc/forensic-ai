# TODO

## SESSION STATE
Status:         CLOSED
Active task:    none
Active persona: architect
Blocking issue: none
Last updated:   2026-04-20T04:10:01Z — state transition by MCP server
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

- ~~[x] EMB-00~~ DONE (requirements.txt updated)
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
**Note:** TPL-01 through TPL-04 DONE (merged Phase C + Phase D). TPL-05 is the remaining AC smoke test.

- [ ] **[TPL-05]** AC smoke test — FRM pipeline generates `F_Final/final_report.docx` using `frm_risk_register_base.docx`; open file in python-docx and confirm at least one paragraph with style matching a GW_ style name is present; audit_log contains `template_resolved` event with `fallback: false`; `templates.json` shows correct base filename in `frm_risk_register.base` slot. ← deps: TPL-01, TPL-02, TPL-03, TPL-04 | AC: smoke test script runs without exception and all three assertions pass.
- [ ] **[TPL-05]** AC smoke test — FRM pipeline generates `F_Final/final_report.docx` using `frm_risk_register_base.docx`; open file in python-docx and confirm at least one paragraph with style matching a GW_ style name is present; audit_log contains `template_resolved` event with `fallback: false`; `templates.json` shows correct base filename in `frm_risk_register.base` slot. ← deps: TPL-01, TPL-02, TPL-03, TPL-04 | AC: smoke test script runs without exception and all three assertions pass.

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

---

### Sprint-ACT — Activity Ledger (Session 024)

**BA:** BA-ACT-01 — CONFIRMED 2026-04-19
**Note:** ACT-00 and ACT-01 DONE (merged Phase D). ACT-02 and ACT-03 are next.

- [x] **[ACT-02]** Wire ActivityLogger into bootstrap() and all pipeline on_progress callbacks — SESSION/PIPELINE events. Wire into 00_Setup.py — SETUP events. Wire into file_tools.py write_artifact() — DOCUMENT/DELIVERABLE events. Wire into settings pages — SETTINGS events. ← deps: ACT-01, SETUP-03 | AC: running a pipeline end-to-end produces ≥5 activity events in logs/activity.jsonl covering SESSION, PIPELINE, DELIVERABLE categories; settings change produces SETTINGS event with old_value + new_value fields.
- [x] **[ACT-03]** Create `pages/07_Activity_Log.py` — per UX-020. (Built as 15_Activity_Log.py — 07 conflicts with existing 07_Proposal.py) Date range picker + category multiselect + free-text search. Paginated 50 events per page. Export as CSV button. Sidebar warning if `st.session_state.get("act_log_warn")` is True. ← deps: ACT-01 | AC: page renders with empty log (shows "No activity recorded yet"); date filter correctly narrows events; category filter works independently and in combination with date; CSV export produces valid file with all visible events; corrupt log file shows error message, does not crash.

---