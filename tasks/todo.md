# TODO

## SESSION STATE
Status:         CLOSED
Active task:    none
Active persona: none
Blocking issue: none
Last updated:   2026-04-07 18:30:00 UTC — Session 014 close by session-close (fallback)

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
- [ ] FE-03 Pipeline progress → Streamlit spinner + status text
- [ ] FE-04 Output display → Streamlit markdown render + file download buttons
- [ ] FE-05 Firm profile setup → Streamlit settings page (replaces terminal wizard)
- [ ] FE-06 Case tracker → Streamlit table with case status + open/download links

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

- [ ] P7-GATE Run `python run.py` with live API keys; complete one FRM workflow end-to-end; verify final_report.en.md written, audit_log.jsonl populated, state.json = OWNER_APPROVED
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

### Phase 8 — Streamlit Frontend Migration (GATED on FE-01..06)

- [ ] P8-01 Add Streamlit to requirements.txt; pin version
- [ ] P8-02 Create app.py (Streamlit entry point) alongside run.py (CLI kept for dev)
- [ ] P8-03 Wire all 10 menu options as Streamlit sidebar navigation
- [ ] P8-04 Document ingestion UI — file upload widget → DocumentManager.register_document()
- [ ] P8-05 Case tracker → Streamlit dataframe with case status + download buttons
- [ ] P8-06 End-to-end smoke test via Streamlit: Option 4 + Option 6

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

- [ ] SRL-02 `agents/partner/prompts.py` — DEFECT: junior-dev removed regulatory_lookup
      instruction from build_task_message() unconditionally. FIX REQUIRED before READY_FOR_REVIEW:
      add research_mode param to build_task_message(); restore "Use regulatory_lookup..." line
      when research_mode == "live". Rest of the mode-aware prompt logic is correct.

- [ ] SRL-03a `agents/project_manager/agent.py` — import config.RESEARCH_MODE; pass as
      research_mode=config.RESEARCH_MODE to prompts.build_system_prompt(). No other changes.

- [ ] SRL-03b `agents/partner/agent.py` — same as SRL-03a. Also pass research_mode to
      prompts.build_task_message() after SRL-02 defect is fixed.

- [ ] SRL-04 Smoke test (AK manual): run `python run.py` → Option 6 → FRM 2 modules →
      knowledge_only. Confirm PM approves without citation revision requests.
      Run 3 consecutive times — all must pass. This IS P7-GATE.

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

- [ ] PPH-01a `config.py` — Change RESEARCH_MODE default:
      `RESEARCH_MODE = os.getenv("RESEARCH_MODE", "live" if TAVILY_API_KEY else "knowledge_only")`
      Key present → live by default. No key → knowledge_only automatically. Explicit env var always wins.

- [ ] PPH-01b `run.py` — At startup, after validate_config(), print one line showing active research mode:
      `[Research: LIVE — Tavily enabled]` or `[Research: KNOWLEDGE-ONLY — no external data]`
      So consultant sees it on every run, not buried in output.

#### PPH-02 — Sanctions screening degraded-mode warning (P1 — must fix before production)

**Risk:** In knowledge_only mode, sanctions_screening workflow returns model-knowledge output with a
disclaimer buried in text. A consultant could interpret this as a live screen result — "no match found"
when no live screen was conducted. This is a compliance and liability issue.

- [ ] PPH-02a `workflows/sanctions_screening.py` — At top of workflow, before any agent run:
      if RESEARCH_MODE != "live": print a prominent warning panel (Rich Panel, red border):
      "SANCTIONS SCREENING — LIVE DATA DISABLED. This output is based on model knowledge only.
       No live OFAC/UN/EU screening was conducted. This result CANNOT be used as a sanctions clearance.
       Set RESEARCH_MODE=live in .env and re-run with a valid TAVILY_API_KEY for a live screen."
      Workflow still runs (consultant may want the template structure) but warning is unmissable.

#### PPH-03 — Knowledge-only disclaimer surfaced as UI warning (P2 — before first client delivery)

**Risk:** Knowledge-only disclaimer is appended as plain text inside agent output. Consultant sees it
inline with the draft content and may not register it as a system-level limitation.

- [ ] PPH-03a `ui/display.py` — Add `display_research_mode_banner(mode: str)` function. Called once
      at session start (by run.py PPH-01b). Renders Rich panel appropriate to mode.

- [ ] PPH-03b `core/agent_base.py` — After appending knowledge-only disclaimer text, also call a
      lightweight `warn_knowledge_only()` that writes one line to stderr/console so it's visible
      separate from the draft output. Keep the text disclaimer in the output for audit trail.

#### PPH-04 — Guardrail mode-awareness rule (P2 — engineering practice)

**Learning:** Any guardrail that enforces external-data quality (citations, sources, live lookups) must
check RESEARCH_MODE before firing. This is now a design constraint, not a one-off fix.

- [ ] PPH-04a `docs/lld/guardrails.md` — Document the mode-awareness rule: "Every guardrail that
      references external data (citations, authoritative sources, live lookups) MUST condition on
      RESEARCH_MODE == 'live'. In knowledge_only mode, replace hard block with disclaimer."
      This is the rule junior-dev applies to any new guardrail going forward.

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

- [ ] TAX-01 Create `knowledge/taxonomy/industries.json` — Level 1 industries + Level 2 sub-sectors.
      Minimum: Manufacturing, Financial Services, Real Estate, Healthcare, Retail, Government, Technology, Construction.
      Each entry: `{id, label, sub_sectors[], suggested_frm_modules[], rationale}`.

- [ ] TAX-02 Create `knowledge/taxonomy/frm_modules.json` — extract FRM module definitions from
      frm_risk_register.py. Each entry: `{id, label, description, dependencies[], default_enabled}`.
      frm_risk_register.py reads from this file — no module definitions in code.

- [ ] TAX-03 Move `JURISDICTION_REGISTRY` from `config.py` to `knowledge/taxonomy/jurisdictions.json`.
      config.py loads the file at startup and exposes the same API (get_jurisdiction_domains etc).
      No behaviour change — pure data extraction.

- [ ] TAX-04 Create `knowledge/taxonomy/routing_table.json` — maps `{industry_id, workflow_id}` →
      `knowledge_file_path`. Agents read this to load the right knowledge baseline. Start with FRM + DD.

- [ ] TAX-05 Add `prompt_with_options(question, options, allow_free_text=True)` to `ui/guided_intake.py`.
      Displays numbered list + "0. Other (type your own)" option. Returns structured value with
      `{selected_id, label, is_custom}` so downstream code knows if it was a taxonomy pick or free text.

- [ ] TAX-06 Wire `prompt_with_options` into all workflow intake flows that currently ask free-text for
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

