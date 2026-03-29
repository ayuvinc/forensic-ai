# TODO

## SESSION STATE
- Status: CLOSED
- Session ID: 003
- Sprint ID: sprint-03
- Last Session Summary: Sprint-02 QA gate QR-01..15 all PASS. External findings F-EXT-01..03 resolved (case persistence, Arabic wiring, DocumentManager). Codex review findings C-01..07 logged to todo. Proposal QA items PQA-01..12 logged. Pricing gap PGP-01..02 logged. .gitignore created. Test cases cleaned. channel.md and CODEX_REVIEW.md reset for next session.
- Opened At: 2026-03-29
- Closed At: 2026-03-29

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
QR-01..12 (Phase 1 QA gate) ← all P1 ── P2-01
P2-01 (plugins) ← P1-09 ─────────── P2-02..05
P2-02 (junior) ← P2-01,P1-10..14 ── P2-05
P2-03 (pm) ← P2-01, P1-10 ────────── P2-05
P2-04 (partner) ← P2-01, P1-10 ───── P2-05
P2-05 (run.py) ← P2-02..04 ──────── P3-01, P4-01..09
P3-01 (frm) ← P2-05, P1-14 ──────── P5-05
P4-01 (proposal) ← P2-05 ─────────── P4-02
P4-02 (deck) ← P4-01
P4-03..09 (workflows) ← P2-05
P5-01..04 (personas) ← P2-01 ─────── P4-07
P5-05 (ui) ← P3-01, P4-01 ─────────── P6-01
P6-01 (arabic) ← P5-05 ──────────── P6-02
P6-02 (EN/AR gen) ← P6-01 ─────── P6-03
P6-03 (E2E test) ← P6-02 ─────── P6-04
P6-04 (zip+README) ← P6-03
```

---

## PENDING TASKS

### Sprint-03 — Proposal + PPT QA Gate (NOT YET RUN)

Proposal workflow (Option 7) and PPT pack (Option 8) were implemented in sprint-02 but never
received a dedicated QA pass. Steps to define and run before smoke test:

- [ ] PQA-01 Firm profile setup — confirm pricing_model.json, team.json, firm_profile.json all
      written correctly by run_firm_profile_setup(); confirm loaded correctly in _load_pricing()
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
- [ ] PQA-12 case_tracker (Option 9) discovers PROP-XXXX cases via intake.json (needs F-EXT-01 fix)

### Sprint-03 — Pricing Model Gap (design issue flagged 2026-03-29)

ISSUE: run_firm_profile_setup() collects pricing but is only triggered once (before first menu).
If user skips it, _load_pricing() returns silent fallback {model:daily, currency:AED, rates:{}}.
Proposal then generates fee section with blank rates — consultant may not notice.

- [ ] PGP-01 Add pricing completeness check in run_client_proposal_workflow(): if rates all empty,
      warn consultant and offer to run firm profile setup inline before continuing
- [ ] PGP-02 Add pricing review step to proposal flow: show loaded rates before drafting,
      allow inline override for this specific proposal without touching firm_profile/

---

### Sprint-03 — Codex Review Findings (2026-03-29)

Source: external Codex review. Assessment: architecture good, operational completeness moderate.
Priority order: C-03 (safety/enforcement) → C-01 (consistency) → C-02 (persistence) → C-04 (doc layer) → C-05 (docs) → C-06 (tests) → C-07 (hygiene)

#### C-01 (Medium) — Workflow quality split: two standards inside one product
Files: workflows/policy_sop.py, training_material.py, client_proposal.py, proposal_deck.py

investigation_report and frm_risk_register use the full stack (orchestrator, state machine,
hooks, artifact persistence, structured schemas). The other four workflows are single-model
generators with no review layer, no state machine, no hook chain.

Options (pick one per workflow before sprint-04):
- [ ] C-01a DECISION: classify policy_sop / training_material as "Mode B: Assisted generation"
      — document this explicitly in README and in-app menu labels so users understand the difference
- [ ] C-01b UPGRADE: move client_proposal onto orchestrated path (Junior draft → PM review →
      Partner sign-off) — higher effort but closes the quality gap for the highest-value workflow
- [ ] C-01c Add lightweight post-hook chain to Mode B workflows (persist_artifact +
      append_audit_event at minimum) so audit trail is consistent even without multi-agent review

#### C-02 (Medium) — Case lifecycle persistence inconsistency
Files: workflows/new_case_intake.py:131, ui/guided_intake.py:20, run.py:101, workflows/case_tracker.py:68

NOTE: F-EXT-01 (this session) added _persist_intake() to run.py for options 2–8.
That fixes intake.json and initial state.json. Remaining gap: Mode B workflows (policy_sop,
training_material, proposal_deck) do not update state.json after completion — case stays at
INTAKE_CREATED even when deliverable is written.

- [ ] C-02a After each Mode B workflow completes, transition state to a terminal-like status
      (e.g. OWNER_APPROVED or a new DELIVERABLE_WRITTEN status) so case_tracker shows correct state
- [ ] C-02b case_tracker (Option 9): verify it discovers and displays all workflow types, not just
      investigation / FRM cases

#### C-03 (Medium) — Evidence-chain validation is prompt-enforced, not code-enforced
Files: tools/evidence/evidence_classifier.py:68, schemas/evidence.py:26, agents/partner/agent.py

EvidenceClassifier.validate_finding_chain() exists and partner prompts instruct validation,
but no runtime call enforces it in the partner agent path. If the model ignores the instruction,
inadmissible evidence can enter approved findings silently.

- [ ] C-03a In agents/partner/agent.py: after partner produces ApprovalDecision, call
      EvidenceClassifier.validate_finding_chain() on all FindingChain items in the output before
      allowing approved=True — raise HookVetoError if any chain fails
- [ ] C-03b Add a post-hook "enforce_evidence_chain" to the partner stage in orchestrator for
      investigation_report workflow — runs after partner output, before final persist
- [ ] C-03c Add QR check: QR-16 — partner approval blocked when finding chain contains
      LEAD_ONLY or INADMISSIBLE evidence items

#### C-04 (Low) — DocumentManager is present but not first-class in the user journey
Files: tools/document_manager.py, run.py, workflows/investigation_report.py:59, frm_risk_register.py:60

NOTE: F-EXT-03 (this session) wired DocumentManager into options 2 and 6 in run.py.
Remaining gap: there is no UI entry point for a consultant to actually ingest documents into a
case. DocumentManager.register_document() exists but is never called from the menu flow.

- [ ] C-04a Add document ingestion step to investigation_report and frm_risk_register intake flows:
      after case intake, ask "Do you have case documents to upload? (Y/n)" → if Y, prompt for
      file paths one at a time, call document_manager.register_document() for each
- [ ] C-04b Add Option 1 extension: after new_case_intake creates folder, offer document ingestion
      inline ("Upload documents to the case folder now?")
- [ ] C-04c Add QR check: QR-17 — document ingestion path: register_document() → index written →
      read_excerpt() returns bounded content

#### C-05 (Low) — README and runtime behavior still diverge
Files: README.md, hooks/post_hooks.py:158

NOTE: Arabic claims corrected this session (F-EXT-02). Remaining divergences:
- README implies resumability for all workflows; only orchestrated workflows (investigation, FRM)
  actually support resume via state.json detection
- README output file table shows final_report.ar.md without conditional note in all examples

- [ ] C-05a Update README resumability section: clarify resume only applies to investigation_report
      and frm_risk_register (orchestrated workflows); Mode B workflows do not resume
- [ ] C-05b Audit all README output examples for accuracy against actual written files

#### C-06 (Low) — No scripted integration tests for actual workflows
Current QA (QR-01..15) is static analysis + unit-level mocks. No end-to-end scripted tests.

- [ ] C-06a Write integration test scaffold: investigation_report happy path (mocked API)
- [ ] C-06b Write integration test: FRM multi-module run (modules 1, 2, 3 with dependency enforcement)
- [ ] C-06c Write integration test: interrupted resume — write partial state.json, restart,
      verify orchestrator offers resume and loads from correct artifact
- [ ] C-06d Write integration test: document ingestion → read_excerpt → agent receives bounded content
- [ ] C-06e Write integration test: persona review against a saved case folder

#### C-07 (Low) — Repo hygiene
- [ ] C-07a Add .gitignore: cover .DS_Store, __pycache__/, *.pyc, cases/*, firm_profile/,
      venv/, .env — generated artifacts and secrets must not be committed
- [ ] C-07b Verify .gitignore is present and correct before any push to remote

---

### QA Gate — Sprint-02 — COMPLETE (2026-03-29)

- [x] QR-01 Import sweep — 57 modules, all clean
- [x] QR-02 Schema validation — all Pydantic models validate correctly
- [x] QR-03 State machine transitions — all paths correct
- [x] QR-04 Hook chain end-to-end — veto, PII, metadata, artifact, audit, md
- [x] QR-05 Tool registry enforcement — PASS + inline fix: name→tool_name in ToolRegistry.call()
- [x] QR-06 Orchestrator happy path — 5-event status trail, audit written
- [x] QR-07 Orchestrator revision loop — junior ran twice on PM revision
- [x] QR-08 Orchestrator resume via load_envelope() — persisted payload loaded correctly
- [x] QR-09 Research tool trust enforcement — domain filter, authoritative marking, no-result disclaimer
- [x] QR-10 File tools atomicity + envelope wrapping — versioning, no .tmp stale, envelope wrap/unwrap
- [x] QR-11 Code quality (simplify pass) — no syntax errors, bare excepts, or star imports
- [x] QR-12 Security — HTML/script stripped, web tools truncated, doc tools pass-through, PII redacted
- [x] QR-13 FRM workflow structure — 8 modules, dependency enforcement, RiskItem extraction
- [x] QR-14 Document manager bounded retrieval — read_excerpt ≤8k, small docs full, read_pages ≤60k
- [x] QR-15 Evidence classifier — LEAD_ONLY classification, FindingChain validation

---

## COMPLETED TASKS

### Sprint-01 (Phase 1 Foundation — 18 files)
- [x] Project plan written and CLAUDE.md committed (2026-03-29)
- [x] tasks/ scaffold created (2026-03-29)
- [x] P0-01 requirements.txt + .env.example (2026-03-29)
- [x] P1-01 config.py (2026-03-29)
- [x] P1-02 schemas/case.py (2026-03-29)
- [x] P1-02b schemas/handoff.py (2026-03-29)
- [x] P1-03 schemas/artifacts.py (2026-03-29)
- [x] P1-03b schemas/presentation.py (2026-03-29)
- [x] P1-04 schemas/research.py (2026-03-29)
- [x] P1-05 core/state_machine.py (2026-03-29)
- [x] P1-06 core/hook_engine.py (2026-03-29)
- [x] P1-07 hooks/pre_hooks.py + post_hooks.py (2026-03-29)
- [x] P1-08 core/tool_registry.py (2026-03-29)
- [x] P1-09 core/agent_base.py (2026-03-29)
- [x] P1-10 core/orchestrator.py (2026-03-29)
- [x] P1-11 tools/research/general_search.py (2026-03-29)
- [x] P1-12 tools/research/regulatory_lookup.py (2026-03-29)
- [x] P1-13 tools/research/sanctions_check.py (2026-03-29)
- [x] P1-14 tools/research/company_lookup.py (2026-03-29)
- [x] P1-15 tools/file_tools.py (2026-03-29)

### Sprint-02 (Phases 1 Revisions + Phases 2–6 — ~49 modules)
- [x] Phase 1 revisions: requirements.txt, config.py, schemas/case.py updated (2026-03-29)
- [x] schemas/documents.py — NEW (2026-03-29)
- [x] schemas/evidence.py — NEW (2026-03-29)
- [x] schemas/plugins.py (AgentHandoff, ArtifactEnvelope, PluginManifest) — NEW (2026-03-29)
- [x] tools/research/regulatory_lookup.py — jurisdictions param redesign (2026-03-29)
- [x] tools/research/company_lookup.py — jurisdictions param redesign (2026-03-29)
- [x] tools/document_manager.py — bounded retrieval design — NEW (2026-03-29)
- [x] core/setup_wizard.py — env+deps + firm profile wizard (2026-03-29)
- [x] core/plugin_loader.py — manifest loader — NEW (2026-03-29)
- [x] tools/file_tools.py — write_envelope, load_envelope added (2026-03-29)
- [x] agents/junior_analyst/ — manifest.json, agent.py, prompts.py, tools.py (2026-03-29)
- [x] agents/project_manager/ — manifest.json, agent.py, prompts.py, tools.py (2026-03-29)
- [x] agents/partner/ — manifest.json, agent.py, prompts.py, tools.py (2026-03-29)
- [x] workflows/frm_risk_register.py — 8-module pipeline — NEW (2026-03-29)
- [x] tools/evidence/excel_analyzer.py — NEW (2026-03-29)
- [x] tools/evidence/email_parser.py — NEW (2026-03-29)
- [x] tools/evidence/evidence_classifier.py — NEW (2026-03-29)
- [x] tools/output_generator.py — docx/pptx — NEW (2026-03-29)
- [x] tools/formatting.py — Arabic translation — NEW (2026-03-29)
- [x] workflows/new_case_intake.py, investigation_report.py, client_proposal.py, proposal_deck.py, policy_sop.py, training_material.py, persona_review.py, case_tracker.py, browse_sops.py — NEW (2026-03-29)
- [x] personas/cfo/, lawyer/, regulator/, insurance_adjuster/ — NEW (2026-03-29)
- [x] ui/menu.py, progress.py, display.py, guided_intake.py — NEW (2026-03-29)
- [x] templates/arabic_glossary.md — NEW (2026-03-29)
- [x] run.py — full main loop — NEW (2026-03-29)
- [x] CODEX_REVIEW.md — sprint-02 review instruction (2026-03-29)
- [x] Sprint-02 finding fixes: P3 (model_validator), P4 (_sanitize web-only), P5 (load_envelope), P6 (PermissibilityStatus Enum) (2026-03-29)
- [x] BUG-01 fix: ToolRegistry.call() param renamed name→tool_name (found in QR-05) (2026-03-29)
- [x] Sprint-02 QA gate: QR-01..15 all PASS (2026-03-29)
