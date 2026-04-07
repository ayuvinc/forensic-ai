# TODO

## SESSION STATE
Status:         OPEN
Active task:    SESSION-012-OPEN
Active persona: architect
Blocking issue: none
Last updated:   2026-04-07 16:10:14 UTC — Session 012 open by session-open (fallback)

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
Sprint-10G (chaining) ← Phase 8 (FE-01..06)
Phase 8 (Streamlit) ← FE-01..06
Phase 9 (chaining UI) ← Sprint-10G
Phase 7 (blank framework) ← P7-GATE
```

Completed tasks archived in: releases/completed-tasks.md
Sprint-01, Sprint-02, QR-01..16, Sprint-03 (completed), Sprint-04 AKR, Sprint-06, Sprint-09, Sprint-10A, Sprint-10B, Sprint-10B-KQ — all DONE, see releases/completed-tasks.md.

---

## PENDING TASKS

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

### Sprint-10E — New Service Line Workflows (depends on Sprint-10A + Sprint-10B — UNBLOCKED after merge)

- [ ] SL-GATE-01 workflows/due_diligence.py — Mode B; Individual/Entity branch via DDIntakeIndividual/DDIntakeEntity; 5-phase methodology from KF-02; report structure: Executive Summary → Profile → Methodology → Sanctions → PEP/UBO → Adverse Media → Conclusion; ARCH-GAP-01 disclaimer auto-injected; ARCH-GAP-02 flag if Phase 2 selected. GATED on ARCH-S-02, KF-02.
- [ ] SL-GATE-02 workflows/sanctions_screening.py — Mode B; intake per BA-008; wire existing tools/research/sanctions_check.py; ARCH-GAP-01 disclaimer; output: clearance memo or full report per intake. GATED on KF-04.
- [ ] SL-GATE-03 workflows/transaction_testing.py — 2-stage intake per BA-009; testing plan generated and shown before document ingestion; state: INTAKE_CREATED → SCOPE_CONFIRMED → DELIVERABLE_WRITTEN; uses TTIntakeContext and TestingPlan. GATED on ARCH-S-03, ARCH-S-05, KF-01.

---

### Sprint-10F — Engagement Scoping Workflow (depends on KF-NEW — UNBLOCKED after merge)

- [ ] SCOPE-WF-01 workflows/engagement_scoping.py — 5-step problem-first flow per BA-010; reads knowledge/engagement_taxonomy/ at runtime; produces ConfirmedScope; routes to existing workflow via run.py/app.py dispatch. GATED on KF-NEW, ARCH-S-04.
- [ ] SCOPE-WF-02 run.py / app.py: add "0. Scope New Engagement" as optional entry point; existing 10 menu items unchanged. GATED on SCOPE-WF-01.

---

### Sprint-10G — Workflow Chaining (GATED on Phase 8 Streamlit)

- [ ] CHAIN-00 core/chain_router.py — CHAIN_MAP: dict[str, list[str]] — 11 valid chains per BA-011; get_compatible_chains(workflow_id) → list[str]; blocked chains enforced by omission. GATED on FE-01..06.
- [ ] CHAIN-01 Post-workflow "Add another deliverable?" prompt — calls chain_router.get_compatible_chains(); threads case_id; updates state.json with all workflow runs. GATED on CHAIN-00.
- [ ] CHAIN-02 case_tracker (Option 9): show all deliverables per case_id when chaining used. GATED on CHAIN-01.

---

### Sprint-10H — Disclaimers and Templates (can run parallel with Sprint-10E)

- [ ] ARCH-GAP-01 Licensed database disclaimer text — add to templates/ and inject into all DD and Sanctions deliverables: "This screening was conducted using publicly available official lists (OFAC, UN, EU, UK OFSI, UAE). It does not include WorldCheck, WorldCompliance, or other commercial databases. For acquisition-grade or regulatory-grade due diligence, commercial database screening is recommended."
- [ ] ARCH-GAP-02 HUMINT scope flag text — add to templates/ and inject when Phase 2/Enhanced DD selected: "This scope includes components that require discreet source enquiries (HUMINT). HUMINT cannot be performed by this tool. Execution requires qualified human investigators. This section defines the HUMINT scope; delivery is manual."
