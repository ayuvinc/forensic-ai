# Deferred Backlog
Tasks moved here are NOT deleted — they are deferred. Re-activate by moving back to tasks/todo.md
and opening a BA session if BA sign-off is missing.

---

## Sprint-03 — Proposal + PPT QA Gate (CLI-era, Streamlit now primary)

Proposal workflow (Option 7) and PPT pack (Option 8) implemented in sprint-02 but never QA'd
against the CLI path. Streamlit is now the primary interface. Defer until CLI path is explicitly
re-prioritised.

- [ ] PQA-01 Firm profile setup — confirm pricing_model.json, team.json, firm_profile.json written correctly
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

## Sprint-03 — Pricing Model Gap (CLI-era)

ISSUE: run_firm_profile_setup() is only triggered once. If user skips it, _load_pricing() returns
silent fallback {model:daily, currency:AED, rates:{}} — fee section generates blank.

- [ ] PGP-01 Add pricing completeness check in run_client_proposal_workflow(): if rates all empty, warn and offer to run firm profile setup inline
- [ ] PGP-02 Add pricing review step: show loaded rates before drafting; allow inline override without touching firm_profile/

---

## Sprint-03 — Open Codex Findings (CLI-era)

### C-01b — Upgrade client_proposal to orchestrated path (Medium)
- [ ] C-01b Move client_proposal onto orchestrated path (Junior draft → PM review → Partner sign-off).

### C-04c / QR-17 — Document ingestion smoke test (Low, gated on API key)
- [ ] QR-17 / C-04c Document ingestion path test — GATED on live API key.

### C-06 — Integration tests (Low)
- [ ] C-06a Integration test: investigation_report happy path (mocked API)
- [ ] C-06b Integration test: FRM multi-module run (modules 1, 2, 3 with dependency enforcement)
- [ ] C-06c Integration test: interrupted resume — write partial state.json, restart, verify orchestrator offers resume
- [ ] C-06d Integration test: document ingestion → read_excerpt → agent receives bounded content
- [ ] C-06e Integration test: persona review against a saved case folder

---

## Frontend Migration — FE-01..09 (DONE in Phase 8 Streamlit)

FE-01 through FE-09 were completed during Phase 8 (merged commit 97626d9). Listed here for
historical traceability only. Do not re-open.

- [x] FE-01 Replace ui/ terminal components with Streamlit pages — DONE Phase 8
- [x] FE-02 Conversational intake → Streamlit multi-step form per workflow — DONE Phase 8
- [x] FE-03 Pipeline progress → Streamlit spinner + status text — DONE Phase 8
- [x] FE-04 Output display → Streamlit markdown render + file download buttons — DONE Phase 8
- [x] FE-05 Firm profile setup → Streamlit settings page — DONE Phase 8
- [x] FE-06 Case tracker → Streamlit table with case status — DONE Phase 8
- [x] FE-07 Risk item review → Streamlit card per item with A/F/R buttons — DONE Phase 8
- [x] FE-08 Case folder UX — interim artifacts restructured — DONE Phase 8 (P8-05a)
- [x] FE-09 Word document design — branding template applied — DONE Phase 8 (P8-07-FE09)

---

## Phase 9 (old) — Workflow Chaining (Superseded by Sprint-10G)

These tasks were written before Sprint-10G refined the chaining design. Sprint-10G (CHAIN-00..02)
supersedes these. Do not activate — use Sprint-10G instead.

- [ ] CH-01 Post-workflow "Add another deliverable to this case?" prompt (Y/N) — see CHAIN-01
- [ ] CH-02 If Y → present only compatible follow-on workflows — see CHAIN-00
- [ ] CH-03 Chain state: state.json updated with all workflow runs — see CHAIN-02
- [ ] CH-04 Integration test: investigation_report → persona_review on same case_id
