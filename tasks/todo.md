# TODO

## SESSION STATE
Status:         OPEN
Active task:    ARCH-S-01 + KF-00 (Sprint-10A schemas + policy_sop knowledge file)
Active persona: junior-dev (build)
Blocking issue: none
Last updated:   2026-04-07 15:15:22 UTC — Session 011 open by session-open (fallback)

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

### Frontend Migration (post-smoke-test, design decision required)

**Decision required:** Pick one option before starting. See architect assessment in session 009.

Options (complexity low→high):
- A: Streamlit — 3-5 days, Python-native, no JS, browser-based
- B: FastAPI + HTMX + HTML templates — 1.5-2 weeks, professional UI, server-rendered
- C: Electron desktop app — 3-4 weeks, native .app/.exe, no terminal/browser needed
- D: FastAPI + React/Next.js — 4-6 weeks, most polished, multi-user capable

Recommended for Maher delivery: **Option A (Streamlit)** first, upgrade later if needed.

- [x] FE-00 Confirmed: Streamlit (Option A) — AK decision Session 009 (2026-04-04)
- [ ] FE-01 (A) Replace ui/ terminal components with Streamlit pages
- [ ] FE-02 (A) Conversational intake → Streamlit multi-step form per workflow
- [ ] FE-03 (A) Pipeline progress → Streamlit spinner + status text
- [ ] FE-04 (A) Output display → Streamlit markdown render + file download buttons
- [ ] FE-05 (A) Firm profile setup → Streamlit settings page (replaces terminal wizard)
- [ ] FE-06 (A) Case tracker → Streamlit table with case status + open/download links

### Sprint-04 — AK-CogOS v2.0 Remediation (Session 005, 2026-04-04)

Architect: session 005 | Origin: claude-core | Target: AK-CogOS v2.0 (Feb 2026)
Source spec: ~/AK-Cognitive-OS — git 508be8b "feat(v2.0.0): conversation-first, artifact-driven development"

```
DEPENDENCY GRAPH — Sprint-04 AK-CogOS v2.0 Remediation

AKR-01 (ba-logic.md) ──────────────────────────────────── P0, independent
AKR-02 (ux-specs.md) ──────────────────────────────────── P0, independent
AKR-03 (framework-improvements.md) ────────────────────── P0, independent
AKR-04 (releases/ directory) ──────────── AKR-05, AKR-11 ─ P0, independent
AKR-05 (session-N.md retrospective) ← AKR-04 ──────────── P1
AKR-06 (CLAUDE.md v2.0 upgrades) ──────────────────────── P0, independent
AKR-07 (docs/ planning scaffold — stubs only) ─── AKR-08 ─ P1, independent
AKR-08 (docs/ discovery: BA+architect sessions) ← AKR-07 ─ P2, human-input-required
AKR-09 (install v2.0 commands from AK-CogOS) ──────────── P1, independent [RISK: may overwrite]
AKR-10 (audit-log.jsonl format migration notice) ──────── P1, independent
AKR-11 (framework/governance metrics populate) ← AKR-04 ── P2
AKR-12 (channel.md v2.0 format) ───────────────────────── P1, independent
AKR-13 (/codex-intake-check validation gate) ← ALL P0+P1 ─ P3 (gate)
```

#### AKR-01 — Create tasks/ba-logic.md [P0, no deps — BLOCKS all skills]
- [x] AKR-01a Create tasks/ba-logic.md — v2.0 stub, sections: Business Logic Decisions,
      Acceptance Rules, Data Rules, Edge Cases, Open Decisions
      Header: "# BA Logic — GoodWork Forensic AI / Stub — populate via /ba discovery session"

#### AKR-02 — Create tasks/ux-specs.md [P0, no deps — BLOCKS /codex-intake-check]
- [x] AKR-02a Create tasks/ux-specs.md — v2.0 stub, sections: UX Flows, Interaction Rules,
      Terminal UI Components, Mobile Constraints (N/A — CLI only), Open UX Decisions
      Header: "# UX Specs — GoodWork Forensic AI / Stub — populate via /ux session"
      Note: project is CLI, not web — UX section covers Rich terminal UI conventions only

#### AKR-03 — Create framework-improvements.md [P0, no deps — BLOCKS /framework-delta-log]
- [x] AKR-03a Create framework-improvements.md at repo root
      Format: append-only log; each entry has date, origin, improvement description
      `/framework-delta-log` appends here at every session close; never delete entries

#### AKR-04 — Create releases/ directory [P0, no deps — v2.0 canonical audit location]
- [x] AKR-04a Create releases/ directory
- [x] AKR-04b Create releases/audit-log.md — human-readable audit trail (mirrors tasks/audit-log.md
      but at the v2.0 canonical path); existing tasks/audit-log.md remains for backward compat;
      going forward, BOTH paths updated on each audit event
- [x] AKR-04c Add .gitignore exception: releases/audit-log.md must NOT be in .gitignore
      (audit trail should be committed; only cases/ and firm_profile/ are excluded)
      VERIFIED: .gitignore does not exclude releases/ — audit-log.md will be committed. Session 006.
- [x] AKR-04d CONSTRAINT: tasks/audit-log.jsonl is the machine-readable log for the forensic
      pipeline; do NOT remove or rename it; it coexists with releases/audit-log.md
      VERIFIED: both paths coexist. Session 006.

#### AKR-05 — Session summary files retrospective [P1, requires AKR-04]
- [x] AKR-05a Create releases/session-001.md — Sprint 01 summary (Foundation: 18 files, 2026-03-29) Session 006
- [x] AKR-05b Create releases/session-002.md — Sprint 02 summary (Phases 2–6: 49 modules, 2026-03-29) Session 006
- [x] AKR-05c Create releases/session-003.md — Sprint 03 summary (QR-01..15 PASS, 2026-03-29) Session 006
- [x] AKR-05d Create releases/session-004.md — Session 004 summary (C-03 complete, QR-16 PASS, 2026-04-02) Session 006

#### AKR-06 — CLAUDE.md v2.0 upgrades [P0, no deps — CRITICAL: append-only, no existing content modified]
- [x] AKR-06a Add ## AK-CogOS v2.0 Path Overrides section (append at end of CLAUDE.md):
      audit_log: tasks/audit-log.jsonl (machine) + releases/audit-log.md (human)
      ba_logic: tasks/ba-logic.md
      ux_specs: tasks/ux-specs.md
      channel: channel.md
      framework_improvements: framework-improvements.md
      session_summaries: releases/session-N.md
      planning_docs: docs/
- [x] AKR-06b Add ## Anti-Sycophancy Protocol section (mandatory v2.0 standing instruction):
      6 rules + SPIRAL DETECTION + trigger phrases as defined in ~/AK-Cognitive-OS/ANTI-SYCOPHANCY.md
      Note: append only; this does NOT override existing forensic app instructions
- [x] AKR-06c HARD CONSTRAINT: do NOT modify any existing CLAUDE.md content above the new sections;
      all additions are append-only at end of file
      VERIFIED: constraint respected across sessions 005–006. Session 006.

#### AKR-07 — docs/ planning scaffold — STUBS ONLY [P1, no deps]
- [x] AKR-07a Create docs/ directory Session 006
- [x] AKR-07b Create docs/problem-definition.md — stub with sections: Who, What, Why, Problem Statement Session 006
- [x] AKR-07c Create docs/scope-brief.md — stub with sections: Must-Have, Should-Have, Cut, Out-of-Scope Session 006
- [x] AKR-07d Create docs/hld.md — Architecture Overview, Data Flow, Agent Pipeline, Key Integrations
      Derived sections from CLAUDE.md; gaps marked [TO VERIFY VIA /architect SESSION] Session 006
- [x] AKR-07e Create docs/assumptions.md — Confirmed, Inferred, Unresolved Session 006
- [x] AKR-07f Create docs/decision-log.md — 11 confirmed decisions backfilled; 2 open decisions noted Session 006
- [x] AKR-07g Create docs/release-truth.md — 57-module status table (REAL/STRUCTURAL/PARTIAL/STUB/MISSING) Session 006
- [x] AKR-07h Create docs/traceability-matrix.md — stub + 10 backfilled entries from QR checks Session 006
- [x] AKR-07i Create docs/lld/ directory + docs/lld/README.md Session 006

#### AKR-08 — docs/ population via discovery sessions [P2, requires AKR-07, human-input-required]
- [x] AKR-08a Run /ba session: docs/problem-definition.md, docs/scope-brief.md, tasks/ba-logic.md
      populated via 8-question discovery conversation with AK. Session 006.
      User: Maher Hashash MD GoodWork LLC UAE. Core value: time/cost saved on grunt work, solo practitioner.
- [ ] AKR-08b Run /architect session: populate docs/hld.md gaps + draft docs/lld/ files per feature
      PARTIAL: hld.md derived from CLAUDE.md this session; gaps marked TO VERIFY. Full /architect session pending.
- [x] AKR-08c Update docs/release-truth.md — written Session 006 with full 57-module status table
      (REAL/STRUCTURAL/PARTIAL/STUB/MISSING). Smoke test pending (R-002).

#### AKR-09 — Install v2.0 commands from AK-Cognitive-OS [P1, no deps]
- [x] AKR-09a RISK ASSESSMENT completed Session 006: install-claude-commands.sh installs to
      ~/.claude/commands/ (GLOBAL), not to project .claude/commands/. Both already contain v2.0
      format commands. AK-Cognitive-OS skills/ dir contains OLDER v1.x format (## Role / ## Scope)
      vs project's v2.0 format (## WHO YOU ARE / ## YOUR RULES / ## ON ACTIVATION).
      FINDING: running the install script would DOWNGRADE project commands — do NOT run.
- [x] AKR-09b DEFERRED: script not run. Reason: project commands already at v2.0 standard.
      Install script contains older format that would downgrade. Logged as AK_DECISION below.
- [x] AKR-09c DEFERRED: N/A — see AKR-09b.
- [x] AKR-09d VERIFIED: forensic-specific commands are in v2.0 format, not overwritten. Safe.
      AK_DECISION: revisit AKR-09 only if AK-Cognitive-OS skills/ are updated to v2.0 format first.

#### AKR-10 — Audit log format migration notice [P1, no deps]
- [x] AKR-10a Append migration notice to tasks/audit-log.jsonl:
      {"entry_id":"AE-005-001","timestamp_utc":"2026-04-04T00:00:00Z","session_id":"005",
      "sprint_id":"sprint-04","agent":"architect","actor":"architect","event_type":"FRAMEWORK_DELTA_LOGGED",
      "origin":"claude-core","status":"PASS",
      "summary":"AK-CogOS v2.0 remediation: event_type going forward is UPPERCASE per exhaustive list.
      Prior entries (sessions 001-004) used lowercase; not retroactively modified.",
      "artifact_links":["tasks/todo.md"]}
- [x] AKR-10b Going forward: all new audit entries use UPPERCASE event_type from exhaustive list in
      ~/AK-Cognitive-OS/schemas/audit-log-schema.md and include "origin" field
      VERIFIED: all session-006 audit entries use UPPERCASE event_type + origin field. Convention active. Session 006.

#### AKR-11 — Populate framework/governance/metrics-tracker.md [P2, requires AKR-04]
- [x] AKR-11a Add session entries for sessions 001–005 (retrospective)
      Use mode: SOLO_CLAUDE (Codex not involved in those sessions)
      Derive metrics from tasks/todo.md completed tasks + audit-log.jsonl
      DONE: 5 session entries written to framework/governance/metrics-tracker.md. Session 006.

#### AKR-12 — Update channel.md to v2.0 format [P1, no deps]
- [x] AKR-12a Rewrite channel.md with v2.0 machine-readable sections:
      Current State (Status, Sessions completed, Last closed, Last agent run)
      Pipeline Queue (Status, Next queue, Mode)
      Active Sprint (sprint_id, tasks, blocking_items)
      Framework Version (v2.0, interop-contract v1.0.0)

#### AKR-13 — /codex-intake-check validation gate [P3, gate — requires AKR-01..12]
- [x] AKR-13a Run /codex-intake-check: all required artifacts present — PASS. Session 006.
      ba-logic.md ✓ | ux-specs.md ✓ | releases/audit-log.md ✓ | framework-improvements.md ✓
      docs/ (7 stubs + lld/) ✓ | channel.md ✓ | session-001..005.md ✓ | metrics-tracker.md ✓
- [x] AKR-13b Remaining gaps documented in tasks/risk-register.md as AK_DECISION items. Session 006.
- [x] AKR-13c ARCHITECTURE_COMPLETE audit event appended to tasks/audit-log.jsonl. Session 006.

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
- [x] C-01a DECISION: classify policy_sop / training_material as "Mode B: Assisted generation"
      — document this explicitly in README and in-app menu labels so users understand the difference
      VERIFIED: menu.py already labels options 4/5/7/8 with "Assisted —"; README has Workflow Modes
      section distinguishing Full Pipeline (2,6) from Assisted Generation (4,5,7,8). Session 006.
- [ ] C-01b UPGRADE: move client_proposal onto orchestrated path (Junior draft → PM review →
      Partner sign-off) — higher effort but closes the quality gap for the highest-value workflow
- [x] C-01c Added write_artifact + append_audit_event to policy_sop, training_material, client_proposal
      (before return). Added append_audit_event to proposal_deck (storyboard already persisted via
      _atomic_write). All 4 Mode B workflows now write a deliverable artifact + audit event. Session 007.

#### C-02 (Medium) — Case lifecycle persistence inconsistency
Files: workflows/new_case_intake.py:131, ui/guided_intake.py:20, run.py:101, workflows/case_tracker.py:68

NOTE: F-EXT-01 (this session) added _persist_intake() to run.py for options 2–8.
That fixes intake.json and initial state.json. Remaining gap: Mode B workflows (policy_sop,
training_material, proposal_deck) do not update state.json after completion — case stays at
INTAKE_CREATED even when deliverable is written.

- [x] C-02a Added DELIVERABLE_WRITTEN to CaseStatus enum + TERMINAL_STATUSES. Added
      _mark_deliverable_written() in run.py, called after choices 4,5,7,8 complete. Session 007.
- [x] C-02b case_tracker _scan_cases() reads any state.json in cases/; DELIVERABLE_WRITTEN now in
      CaseStatus enum so it renders as green (terminal) in the table. Verified by code read. Session 007.

#### C-03 (Medium) — Evidence-chain validation is prompt-enforced, not code-enforced
Files: tools/evidence/evidence_classifier.py:68, schemas/evidence.py:26, agents/partner/agent.py

EvidenceClassifier.validate_finding_chain() exists and partner prompts instruct validation,
but no runtime call enforces it in the partner agent path. If the model ignores the instruction,
inadmissible evidence can enter approved findings silently.

- [x] C-03a Partner agent: _enforce_evidence_chains() overrides approved=True when FindingChain
      references LEAD_ONLY/INADMISSIBLE evidence (agents/partner/agent.py) — session 004
- [x] C-03b Post-hook enforce_evidence_chain added to POST_HOOKS (position 2, between
      validate_schema and persist_artifact) — HookVetoError on bad chain (hooks/post_hooks.py) — session 004
- [x] C-03c Evidence items threaded via closure in partner_fn; _build_evidence_items() converts
      DocumentEntry→EvidenceItem (workflows/investigation_report.py) — session 004
- [x] C-03d QR-16: 7/7 sub-checks PASS — validate_finding_chain rejects LEAD_ONLY, hook vetoes
      bad approval, passes approved=False, passes PERMISSIBLE, no-op for FRM, no-op without
      evidence_items, agent-level override works — session 004

#### C-04 (Low) — DocumentManager is present but not first-class in the user journey
Files: tools/document_manager.py, run.py, workflows/investigation_report.py:59, frm_risk_register.py:60

NOTE: F-EXT-03 (this session) wired DocumentManager into options 2 and 6 in run.py.
Remaining gap: there is no UI entry point for a consultant to actually ingest documents into a
case. DocumentManager.register_document() exists but is never called from the menu flow.

- [x] C-04a Added _run_document_ingestion() helper in run.py; called for choice 2 (investigation)
      and choice 6 (FRM) after document_manager created, before pipeline runs. 7-type menu with
      graceful fallback if API unavailable. Session 007.
- [x] C-04b Added _offer_document_ingestion() in new_case_intake.py; called after case creation
      panel with Confirm prompt. Same 7-type menu + graceful fallback. Session 007.
- [ ] C-04c QR-17 — document ingestion path: register_document() → document_index.json written →
      read_excerpt() returns bounded content ≤8k chars. Run when API key available (smoke test gate).

#### C-05 (Low) — README and runtime behavior still diverge
Files: README.md, hooks/post_hooks.py:158

NOTE: Arabic claims corrected this session (F-EXT-02). Remaining divergences:
- README implies resumability for all workflows; only orchestrated workflows (investigation, FRM)
  actually support resume via state.json detection
- README output file table shows final_report.ar.md without conditional note in all examples

- [x] C-05a README "If Something Gets Interrupted" section rewritten to clarify resume applies to
      Options 2+6 only; Options 4,5,7,8 single-pass, no resume. Troubleshooting FAQ updated. Session 007.
- [x] C-05b README output file table updated: case ID format corrected to {YYYYMMDD}-{6-char} pattern;
      intake.json added; Mode B vs Full Pipeline artifact distinction added; Quick Reference Card
      corrected from hardcoded 0001 to CASE-ID placeholder. Session 007.

#### C-06 (Low) — No scripted integration tests for actual workflows
Current QA (QR-01..15) is static analysis + unit-level mocks. No end-to-end scripted tests.

- [ ] C-06a Write integration test scaffold: investigation_report happy path (mocked API)
- [ ] C-06b Write integration test: FRM multi-module run (modules 1, 2, 3 with dependency enforcement)
- [ ] C-06c Write integration test: interrupted resume — write partial state.json, restart,
      verify orchestrator offers resume and loads from correct artifact
- [ ] C-06d Write integration test: document ingestion → read_excerpt → agent receives bounded content
- [ ] C-06e Write integration test: persona review against a saved case folder

#### C-07 (Low) — Repo hygiene
- [x] C-07a Add .gitignore: cover .DS_Store, __pycache__/, *.pyc, cases/*, firm_profile/,
      venv/, .env — generated artifacts and secrets must not be committed
      VERIFIED: all required paths present in .gitignore. No changes needed. Session 006.
- [x] C-07b Verify .gitignore is present and correct before any push to remote
      VERIFIED: .gitignore present and correct. Session 006.

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
- [x] QR-16 Evidence chain enforcement — partner approval blocked on LEAD_ONLY/INADMISSIBLE (7/7 sub-checks PASS, session 004)
- [ ] QR-17 Document ingestion path: _offer_document_ingestion() / _run_document_ingestion() →
      register_document() → document_index.json written → read_excerpt() returns ≤8k chars.
      GATED on API key (R-002). Session 007.

---

### Phase 7 — Blank Framework Packaging (GATED on smoke test passing)

**GATE: Do not start Phase 7 until R-002 is resolved and GoodWork instance smoke test passes.**
Rationale: blank framework must be extracted from a verified working instance, not from structural-only code.

Architect: session 006 | Origin: claude-core | Target: sellable blank framework for other consulting firms

```
DEPENDENCY GRAPH — Phase 7

P7-GATE (smoke test pass) ─────────────────────────── blocks ALL P7 tasks
P7-01 (audit hardcoded refs) ← P7-GATE ──────── P7-02, P7-03
P7-02 (instance_config/ + firm.json) ← P7-01 ── P7-03, P7-04, P7-05
P7-03 (fix 4 hardcoded defaults) ← P7-01 ─────── P7-05
P7-04 (knowledge/ template guide) ← P7-02 ─────── P7-05, P7-06
P7-05 (create_blank_instance.py) ← P7-02,03,04 ─ P7-07
P7-06 (INSTANCE_GUIDE.md) ← P7-04 ─────────────── P7-07
P7-07 (end-to-end blank instance test) ← P7-05,06
```

#### P7-GATE — Smoke test (prerequisite, NOT a Phase 7 task)
- [ ] P7-GATE Run `python run.py` with live API keys; complete one FRM workflow end-to-end; verify
      final_report.en.md written, audit_log.jsonl populated, state.json = OWNER_APPROVED
      BLOCKED: R-002 (API key not confirmed in environment)

#### P7-01 — Audit all hardcoded firm/domain references [requires P7-GATE]
- [ ] P7-01a Grep entire codebase for "GoodWork", "Maher", "forensic" as string literals (not in
      comments/docs). Confirm only 4 locations: run.py:331, partner/prompts.py:8, setup_wizard.py:161,
      run.py:2 (docstring). Flag any additional hardcoded references found.

#### P7-02 — Create instance_config/ directory [requires P7-01]
- [ ] P7-02a Create `instance_config/` directory at repo root
- [ ] P7-02b Create `instance_config/firm.json` — instance-level config:
      {firm_name, firm_type, primary_industry, primary_jurisdiction, enabled_workflows[], persona_set[],
      language_default, billing_currency}
      GoodWork values pre-populated; new firms edit this file at setup
- [ ] P7-02c Update `config.py` to load `instance_config/firm.json` at startup; expose FIRM_NAME,
      FIRM_TYPE, PRIMARY_INDUSTRY as module-level constants
- [ ] P7-02d Update `run.py` to read firm_name from config, not hardcoded fallback

#### P7-03 — Fix 4 hardcoded default strings [requires P7-01]
- [ ] P7-03a `run.py:331` — replace hardcoded "GoodWork Forensic Consulting" fallback with
      `config.FIRM_NAME` (loaded from instance_config/firm.json)
- [ ] P7-03b `agents/partner/prompts.py:8` — replace default `firm_name="GoodWork Forensic Consulting"`
      with `firm_name=config.FIRM_NAME`
- [ ] P7-03c `core/setup_wizard.py:161` — keep "GoodWork LLC" as Prompt default for Maher's instance
      but wrap in `config.FIRM_NAME` so new instances see their own name after first setup

#### P7-04 — Knowledge base template guide [requires P7-02]
- [ ] P7-04a Create `knowledge/README.md` — explains that knowledge/ is instance-specific:
      forensic/ is GoodWork's domain knowledge; new instances replace with their own domain
- [ ] P7-04b Create `knowledge/_template/` directory with stub files:
      framework.md (populate with your firm's methodology), sources.md (populate with your authoritative sources)
      Mark clearly: "GoodWork forensic knowledge is in knowledge/frm/ and knowledge/investigation/ — do not delete,
      use as reference for structure"

#### P7-05 — Blank instance packaging script [requires P7-02, P7-03, P7-04]
- [ ] P7-05a Create `scripts/create_blank_instance.py`:
      - Copies full repo to target directory
      - Removes GoodWork-specific knowledge content (keeps structure, clears content)
      - Resets firm_profile/ to empty
      - Resets instance_config/firm.json to blank defaults
      - Preserves all engine code (core/, schemas/, hooks/, agents/, workflows/, tools/, ui/)
      - Outputs a zip file ready for distribution
- [ ] P7-05b Add README section: "For new firms: run scripts/create_blank_instance.py to generate
      your own instance"

#### P7-06 — Instance onboarding guide [requires P7-04]
- [ ] P7-06a Create `INSTANCE_GUIDE.md` at repo root:
      Step 1: Run create_blank_instance.py → get clean copy
      Step 2: Edit instance_config/firm.json with your firm details
      Step 3: Populate knowledge/ with your domain methodology and sources
      Step 4: Run python run.py → setup wizard collects firm profile
      Step 5: Run your first workflow
      Step 6: Customize agent prompts for your domain (optional — generic prompts work as starting point)

#### P7-07 — End-to-end blank instance test [requires P7-05, P7-06]
- [ ] P7-07a Run create_blank_instance.py → new instance directory created
- [ ] P7-07b Run setup wizard on blank instance — firm profile collected for a test firm
- [ ] P7-07c Run Option 6 (FRM) on blank instance — confirm it works without GoodWork knowledge
- [ ] P7-07d Verify no GoodWork data bleeds into blank instance output

---

### Phase 8 — Streamlit Frontend Migration (GATED on FE-01..FE-06 complete)

**GATE: FE-01..FE-06 must all be done before Phase 8 wiring.**

- [ ] P8-01 Add Streamlit to requirements.txt; pin version
- [ ] P8-02 Create app.py (Streamlit entry point) alongside run.py (CLI kept for development)
- [ ] P8-03 Wire all 10 menu options as Streamlit sidebar navigation
- [ ] P8-04 Document ingestion UI — file upload widget → DocumentManager.register_document()
- [ ] P8-05 Case tracker → Streamlit dataframe with case status + download buttons
- [ ] P8-06 End-to-end smoke test via Streamlit: Option 4 + Option 6

---

### Phase 9 — Workflow Chaining (GATED on Phase 8 complete)

**Approach: same case_id threaded across multiple deliverable workflows.**

- [ ] CH-01 Post-workflow "Add another deliverable to this case?" prompt (Y/N)
- [ ] CH-02 If Y → present only compatible follow-on workflows based on existing case type
- [ ] CH-03 Chain state: state.json updated with all workflow runs; case_tracker shows all deliverables per case_id
- [ ] CH-04 Integration test: investigation_report → persona_review on same case_id

---

### Phase 10 — New Service Lines (GATED on planning session with Maher)

**GATE: /ba + /architect planning session required before building. Scope below is provisional.**

New service lines identified Session 009 — each needs precision intake questionnaire (8–12 questions) + knowledge file:

- [ ] SL-01 Transaction Testing (sub-service of Fraud Audit) — knowledge/transaction_testing/
- [ ] SL-02 Due Diligence — knowledge/due_diligence/ (commercial, legal, reputational)
- [ ] SL-03 Fraud Audit — knowledge/fraud_audit/ (ACFE methodology, T&M scope)
- [ ] SL-04 Sanctions Screening — knowledge/sanctions_screening/ (OFAC/UN/EU, PEP)
- [ ] SL-05 ESI (Electronic Evidence) Review — knowledge/esi_review/ (EDRM, collection, culling)
- [ ] SL-06 Expert Witness Support — knowledge/expert_witness/ (court standard, admissibility)
- [ ] SL-07 HUMINT (Source-based Intelligence) — knowledge/humint/ (methodology, ethics, chain-of-custody)

Scope hierarchy design:
- Level 1: Service Line (Investigation, FRM, Compliance, etc.)
- Level 2: Engagement Type (specific sub-service)
- Level 3: Specific Deliverable (report, register, policy, deck)

---

### Phase 11 — Precision Intake Questionnaires (GATED on Phase 10 planning)

**Requires planning session output: approved question sets per scope.**

- [ ] PQ-01 Transaction Testing intake: 8–12 questions (transaction types, date range, population size, red flag criteria, regulatory context)
- [ ] PQ-02 Due Diligence intake: 8–12 questions (target type, purpose, depth, jurisdictions, timeline)
- [ ] PQ-03 Fraud Audit intake: 8–12 questions (allegation type, population, data access, preliminary evidence)
- [ ] PQ-04 Sanctions intake: 8–12 questions (entity type, jurisdictions, screening lists, existing relationships)
- [ ] PQ-05 ESI Review intake: 8–12 questions (data volume, custodians, date range, relevance criteria)
- [ ] PQ-06 Expert Witness intake: 8–12 questions (matter type, jurisdiction, opposing expert, issue framing)
- [ ] PQ-07 HUMINT intake: 8–12 questions (subject type, jurisdictions, engagement limits, client authorization)

---

### Phase 12 — Knowledge Files for New Service Lines (GATED on Phase 10 planning)

**Quickest win: knowledge/policy_sop/ fixes Whistleblower Policy quality gap already observed.**

- [x] KF-00 knowledge/policy_sop/ — priority 1; fixes 8 gaps identified in ChatGPT review Session 009
      Gaps: anonymous complaint handling, retaliation mechanism + disciplinary matrix, evidence/chain-of-custody,
      SLA for closure comms, malicious vs good-faith definition (legal precision), DPDP Act 2023 integration,
      vendor/third-party enforcement, metrics/KPI reporting framework
- [x] KF-01 knowledge/transaction_testing/ (framework + sources)
- [x] KF-02 knowledge/due_diligence/ (framework + sources)
- [ ] KF-03 knowledge/fraud_audit/ (framework + sources)
- [x] KF-04 knowledge/sanctions_screening/ (framework + sources)
- [ ] KF-05 knowledge/esi_review/ (EDRM framework + sources)
- [ ] KF-06 knowledge/expert_witness/ (framework + sources)
- [ ] KF-07 knowledge/humint/ (framework + methodology)

---

### Phase 13 — FRM Guided Exercise Redesign (GATED on planning session — HIGHEST PRIORITY)

**Core design shift:** FRM is a structured assessment exercise, not a one-shot generation.
Model leads consultant through the exercise step by step. Output is co-created, not AI-generated.

Flow design (to be validated with Maher in planning session):
```
STEP 1 — Show plan
  "Here is the FRM scope: Modules 2, 3. Here is what we will cover in each. Ready to start?"

STEP 2 — Per module, per risk sub-area
  "Module 2 — AML Risk. Sub-area: Customer Due Diligence.
   Does this apply to ABC Inc? [Y/N/Partial]"

STEP 3 — Per applicable sub-area, gather context
  "Any known incidents or red flags in this area? (or press Enter to skip)"
  "What controls currently exist? (or Enter for none known)"
  "Probability of occurrence (1-5): __"
  "Impact if it occurs (1-5): __"

STEP 4 — Model generates risk item from consultant input + regulatory baseline
  Risk item shown: Title, Description, Rating, Owner, Recommendations
  Consultant: [Approve / Edit / Skip]

STEP 5 — Register assembled from approved items only
```

Zero-information case: model pre-populates Step 3 with industry-baseline answers, clearly labelled
BASELINE (unverified) — consultant reviews each one rather than starting from blank.

- [x] FRM-R-00 Planning gate: validate guided-exercise flow design with Maher — CONFIRMED Session 010 (2026-04-06). Edit = structured conversation, model recommends all parameters. See BA-002.
- [ ] FRM-R-01 New intake: after module selection, present plan summary before starting
      "We will assess X sub-areas across Y modules. Here is the structure. Proceed?"
- [ ] FRM-R-02 Per-module loop: for each module, present sub-areas list → consultant confirms scope
- [ ] FRM-R-03 Per-risk-area: structured question sequence (incident? controls? probability? impact?)
      Store answers in risk_context dict; pass to model for item generation
- [ ] FRM-R-04 Model generates risk item from risk_context + regulatory knowledge
      Output is one RiskItem at a time, not the full register in one call
- [ ] FRM-R-05 Review loop: show each generated risk item → Approve / Edit / Skip
      Edits fed back to model for one revision before final acceptance
- [ ] FRM-R-06 Register assembly: only approved/edited items enter the final register
- [ ] FRM-R-07 Zero-info mode: if consultant skips all context questions, model pre-fills with
      industry-baseline answers labelled BASELINE; consultant still reviews each item
- [ ] FRM-R-08 Apply same guided-exercise pattern to Investigation Report scoping phase

### Phase 13 — Zero-Information Draft Design (GATED on planning session)

**Core principle:** Engine must produce a usable starting-point draft even with zero client documents
and minimal intake. Never return a blank deliverable when domain knowledge exists.

Design: each workflow has a "content floor" — baseline items populated from knowledge file when
consultant provides no evidence. Consultant adds/removes/adjusts from this baseline.

- [x] ZID-00 Planning: define content floor per workflow — CONFIRMED Session 010 (2026-04-06). All 7 workflows defined. See BA-004.
- [ ] ZID-01 FRM: if findings=[] after junior run → inject industry-baseline risks from knowledge file
      before PM review (not as final answer — as starting point for consultant review)
- [ ] ZID-02 Investigation: if no documents registered → system prompt instructs junior to draft from
      publicly known typologies + generate open_questions list for consultant to answer
- [ ] ZID-03 Policy/SOP: if minimal intake → draft from regulatory framework defaults + flag gaps
      (already partially working — knowledge/policy_sop/ KF-00 will improve this)
- [ ] ZID-04 All agent system prompts: add explicit instruction "never return empty findings/risks —
      populate with industry baseline if no client-specific evidence is available, clearly labelled
      as BASELINE (unverified) for consultant review"
- [ ] ZID-05 Session context hygiene: session-open checks must warn if context approaching limit;
      close sessions before 80% to preserve carry-forward fidelity

### Phase 10–13 Architecture + Build Tasks (Session 010 — 2026-04-06)

**Architect decisions:**
- FRM Exercise Engine: Option A (refactor in place, not generic engine yet)
- DD + Sanctions: Mode B first (single-pass), upgrade to full pipeline later (same path as C-01b)
- Transaction Testing: new SCOPE_CONFIRMED state between INTAKE_CREATED and DELIVERABLE_WRITTEN
- Chaining: new core/chain_router.py provides logic; Phase 9 CH-01..04 provide UI
- Historical Library: tools/knowledge_library.py — sanitisation is a HARD GATE before any index write

**Critical path:**
Schemas → Knowledge files → Historical Library → Workflows → Scoping → Chaining

#### Sprint-10A — Schemas (no deps — build first, everything else blocks on these)

- [x] ARCH-S-01 schemas/artifacts.py: add RiskContextItem — stores Maher's per-sub-area answers for FRM exercise (incident: str, existing_controls: str, probability: int 1-5, impact: int 1-5, consultant_notes: str). GATES: FRM-R-03.
- [x] ARCH-S-02 schemas/dd.py — new file: DDIntakeIndividual (14 fields per BA-006), DDIntakeEntity (14 fields per BA-007), DDReport (subject_profile, methodology, sanctions_results, pep_results|beneficial_ownership, adverse_media, risk_classification: Literal["LOW","MEDIUM","HIGH"], recommendation: str). GATES: SL-GATE-01.
- [x] ARCH-S-03 schemas/transaction_testing.py — new file: TTIntakeContext (engagement_context: Literal["fraud_discovery","fraud_quantification","audit_compliance","due_diligence","regulatory"], fraud_typology, data_inventory, population_size, date_range, evidence_standard), TestingPlan (tests: list[TestObjective], population, method, caveats), TTResult. GATES: SL-GATE-03.
- [x] ARCH-S-04 schemas/engagement_scope.py — new file: ScopeIntake (client_situation: str, trigger: str, desired_outcome: str, constraints: str), ScopeRecommendation (engagement_types: list[str], scope_components: list[str], deliverables: list[str], sequencing: list[str], caveats: list[str]), ConfirmedScope. GATES: SCOPE-WF-01.
- [x] ARCH-S-05 core/state_machine.py: add SCOPE_CONFIRMED to CaseStatus enum; add INTAKE_CREATED → SCOPE_CONFIRMED and SCOPE_CONFIRMED → DELIVERABLE_WRITTEN transitions to VALID_TRANSITIONS. GATES: SL-GATE-03.
- [x] ARCH-S-06 tools/knowledge_library.py (scaffold): define module-level SanitisationError exception class. Location is tools/, not schemas/ — it is a runtime validation error, not a data model. Must be importable by HRL-00 without circular dep. GATES: HRL-00.
- [x] ARCH-S-07 schemas/artifacts.py: add SanitisedIndexEntry model — {service_type: str, industry: str, jurisdiction: str, company_size_band: Literal["<50","50-200","200-1000",">1000"], engagement_date_year: int, scope_components: list[str], risk_count: int, key_patterns: list[str], source_file_hash: str, provenance: Literal["BASELINE","FROM_SIMILAR_ENGAGEMENT"]}. No PII fields by design — enforced at model level, not convention. GATES: HRL-00, HRL-02..06.

#### Sprint-10B — Knowledge Files (parallel with schemas, no code deps)

- [x] KF-NEW knowledge/engagement_taxonomy/framework.md — AK-CONFIRMED list (2026-04-07): Investigation Report (7 distinct sub-type entries: general/procurement/payroll/expense/financial-stmt/AML/whistleblower), FRM Risk Register (8 modules), Due Diligence Individual, Due Diligence Entity, Transaction Testing, Sanctions Screening, Policy/SOP, Training Material, Client Proposal, Engagement Scoping, ABC Programme (can be standalone OR bundled with FRM). EXCLUDED: Insurance Fraud, Asset Tracing (always part of investigation), Insolvency Fraud, Expert Witness (deferred), ESI (deferred), HUMINT (deferred). Each entry: triggering scenarios, standard scope components, typical deliverables, applicable frameworks, common chains, exclusions, red flags that escalate. Quality standard: tier B from draft (claim labels, provenance metadata). GATES: SCOPE-WF-01.
- [ ] KF-02 knowledge/due_diligence/framework.md — GoodWork 5-phase DD methodology (CE Creates reports NOT available as reference — derive from standard FATF/ACFE methodology + BA-006/007 report structure). Source list by jurisdiction. Risk classification: LOW/MEDIUM/HIGH + CLEAR/FLAG with explicit criteria (no model judgment). Licensed DB gap disclaimer text (ARCH-GAP-01). HUMINT scope disclaimer (ARCH-GAP-02). Quality standard: tier B from draft. GATES: SL-GATE-01.
- [ ] KF-04 knowledge/sanctions_screening/framework.md — 5 official screening lists (OFAC/UN/EU/UK OFSI/UAE), PEP classification, false positive analysis methodology, risk rating criteria, WorldCheck gap disclaimer. GATES: SL-GATE-02.
- [ ] KF-01 knowledge/transaction_testing/framework.md — ACFE transaction testing methodology, Benford's law procedure, three-way matching procedure, test objectives by fraud typology (6 types), UAE regulatory testing requirements per regulator, sampling standards. GATES: SL-GATE-03.
- [x] KF-00 knowledge/policy_sop/framework.md — BUILT Sprint-10A (2026-04-07). Needs KQ-01 remediation pass (quality standard). Sources.md missing (KQ-03).

#### Sprint-10B-KQ — Knowledge Quality Remediation (parallel with Sprint-10B, no build deps)

**Quality standard defined in:** docs/lld/knowledge-quality-standard.md (2026-04-07)
**Codex finding:** knowledge/policy_sop/framework.md mixes law/best-practice/product-rules without labels; uses absolute language without citation; frm + investigation files need provenance metadata.

- [x] KQ-01 knowledge/policy_sop/framework.md: remediation pass — add [LAW]/[BEST_PRACTICE]/[PRODUCT_RULE]/[ADVISORY] labels to all substantive claims; replace "must"/"legally insufficient"/"courts have ruled" with labeled claims or softer language; add provenance metadata per section; add quality header (tier C → B). No content changes — labeling only.
- [x] KQ-02 knowledge/frm/frm_framework.md + knowledge/investigation/investigation_framework.md: light remediation — add quality header block (tier B); add provenance metadata to major sections; no claim rewrites needed.
- [x] KQ-03 knowledge/policy_sop/sources.md: create companion sources file (BA-013 confirmed). Same structure as knowledge/frm/sources.md. Cover: UAE onshore (Federal laws + MOHRE), DIFC, ADGM, India (SEBI/POSH/DPDP), UK (FCA/ICO), international (ISO 37001, ACFE, IIA). Authoritative URLs only for [LAW] sources; note that ISO/ACFE/IIA are subscription-based (no public URL).
- [x] KQ-04 knowledge/due_diligence/sources.md: create alongside KF-02. UAE registries (MOEC, DED, ADGM, DIFC), GCC registries, India (MCA21), UK (Companies House), international (OpenCorporates). Note: Orbis, LexisNexis Diligence, WorldCheck are licensed — not accessible to tool.
- [x] KQ-05 knowledge/sanctions_screening/sources.md: create alongside KF-04. The 5 official list URLs (ofac.treas.gov, un.org/securitycouncil/sanctions, sanctions.ec.europa.eu, assets.publishing.service.gov.uk/ofsi, uaecabinet.ae). PEP registers are not openly searchable — note this explicitly.
- [x] KQ-06 knowledge/transaction_testing/sources.md: create alongside KF-01. ACFE Fraud Examiners Manual (subscription), IIA standards, UAE CBUAE/DFSA/SCA/ADGM FSRA regulatory testing requirements (authoritative URLs), Benford's Law source reference.
- [x] KQ-07 knowledge/engagement_taxonomy/sources.md: create alongside KF-NEW. References ACFE Practice Guides, IIA IPPF, UAE SCA/DFSA/ADGM engagement requirements by type.

#### Sprint-10C — Historical Knowledge Library (depends on Sprint-10A schemas)

- [ ] HRL-00 tools/knowledge_library.py — [SCAFFOLD first] KnowledgeLibrary class: ingest(file_path, service_type) → runs intake conversation → sanitise() → index_entry(). sanitise() strips: names, passport/ID numbers, company reg numbers, case IDs, dates that identify specific engagements. Retrieval: match_similar(engagement_params) → list[HistoricalMatch] sorted by similarity. Hard gate: if sanitise() fails validation, ingest() raises SanitisationError — no partial index entries written. GATES: HRL-01..06.
- [ ] HRL-01 Historical register/report import wizard — extend setup_wizard.py or add guided_import.py; prompts Maher to upload FRM registers, DD reports, proposals, scope letters; calls KnowledgeLibrary.ingest() per file; shows index summary after each import. CE Creates DD reports (3) are the documented seed entries. GATED on HRL-00.
- [ ] HRL-02 firm_profile/historical_registers/ dir + index.json schema — GATED on HRL-00.
- [ ] HRL-03 firm_profile/historical_reports/due_diligence/ dir + index.json schema — GATED on HRL-00.
- [ ] HRL-04 firm_profile/historical_reports/sanctions_screening/ dir + index.json schema — GATED on HRL-00.
- [ ] HRL-05 firm_profile/historical_reports/transaction_testing/ dir + index.json schema — GATED on HRL-00.
- [ ] HRL-06 firm_profile/historical_scopes/ dir + index.json schema — GATED on HRL-00.

#### Sprint-10D — FRM Guided Exercise Redesign (depends on ARCH-S-01)

- [ ] FRM-R-01 workflows/frm_risk_register.py: intake updated — after module selection, present plan summary before starting. "We will assess X sub-areas across Y modules. Proceed?" GATED on ARCH-S-01.
- [ ] FRM-R-02 Per-module loop: for each module, present sub-areas list → Maher confirms which apply (Y/N/Partial). Store confirmed sub-areas in list before entering per-risk loop.
- [ ] FRM-R-03 Per-risk-area: structured 4-question sequence (incidents? controls? probability? impact?). Store answers in RiskContextItem; pass to model for item generation. GATED on ARCH-S-01.
- [ ] FRM-R-04 One-item-at-a-time generation: model generates one RiskItem from RiskContextItem + regulatory baseline. Output: risk title, scenario, impact rating, probability rating, residual risk — all recommended by model. Never generate full register in one call.
- [ ] FRM-R-05 Review loop: show each RiskItem → Approve / Edit / Skip. Edit triggers structured model conversation (model asks follow-ups and re-recommends all parameters). One revision cycle per item. Override after revision recorded in audit_log.
- [ ] FRM-R-06 Register assembly: only approved items enter final register. Explicitly skipped items recorded in state.json as excluded. Empty register warning before final assembly.
- [ ] FRM-R-07 Zero-info mode: if all Step 3 answers skipped, model pre-fills RiskContextItem with industry-baseline answers labelled BASELINE. Maher still reviews each item — no auto-approval.
- [ ] FRM-R-08 BASELINE flag handling: BASELINE label stored in state.json per item. Maher's approval removes it from the deliverable. audit_log records provenance (BASELINE vs consultant-input vs FROM_SIMILAR_ENGAGEMENT) for every item.

#### Sprint-10E — New Service Line Workflows (depends on Schemas + Knowledge Files)

- [ ] SL-GATE-01 workflows/due_diligence.py — Mode B; Individual/Entity branch at intake using DDIntakeIndividual / DDIntakeEntity; 5-phase methodology from KF-02; report structure mirrors CE Creates template (Executive Summary → Profile → Methodology → Sanctions → PEP/UBO → Adverse Media → Conclusion); ARCH-GAP-01 disclaimer injected automatically; ARCH-GAP-02 flag injected if Phase 2 selected. GATED on ARCH-S-02, KF-02.
- [ ] SL-GATE-02 workflows/sanctions_screening.py — Mode B; intake per BA-008; wire existing tools/research/sanctions_check.py; ARCH-GAP-01 disclaimer; output: clearance memo or full report per intake Q10. GATED on ARCH-S-02 (extend for sanctions intake), KF-04.
- [ ] SL-GATE-03 workflows/transaction_testing.py — 2-stage intake per BA-009; testing plan generated and shown to Maher before document ingestion; state transitions: INTAKE_CREATED → SCOPE_CONFIRMED → DELIVERABLE_WRITTEN; uses TTIntakeContext and TestingPlan schemas. GATED on ARCH-S-03, ARCH-S-05, KF-01.

#### Sprint-10F — Engagement Scoping Workflow (depends on KF-NEW)

- [ ] SCOPE-WF-01 workflows/engagement_scoping.py — 5-step problem-first flow per BA-010; reads knowledge/engagement_taxonomy/ at runtime; produces ConfirmedScope; routes to existing workflow via run.py/app.py dispatch. GATED on KF-NEW, ARCH-S-04.
- [ ] SCOPE-WF-02 run.py / app.py: add "0. Scope New Engagement" as optional entry point; existing 10 menu items unchanged. GATED on SCOPE-WF-01.

#### Sprint-10G — Workflow Chaining (depends on Phase 8 Streamlit)

- [ ] CHAIN-00 core/chain_router.py — CHAIN_MAP: dict[str, list[str]] defining 11 valid chains per BA-011; get_compatible_chains(workflow_id) → list[str]; blocked chains enforced by omission. GATED on Phase 8 (FE-01..FE-06).
- [ ] CHAIN-01 Post-workflow "Add another deliverable?" prompt — calls chain_router.get_compatible_chains(); offers compatible options; threads case_id through; updates state.json with all workflow runs. GATED on CHAIN-00.
- [ ] CHAIN-02 case_tracker (Option 9): update to show all deliverables per case_id when chaining has been used. GATED on CHAIN-01.

#### Sprint-10H — Disclaimers and Templates

- [ ] ARCH-GAP-01 Licensed database disclaimer — standard text block for all DD and Sanctions outputs: "This screening was conducted using publicly available official lists (OFAC, UN, EU, UK OFSI, UAE). It does not include WorldCheck, WorldCompliance, or other commercial database screening. For acquisition-grade or regulatory-grade due diligence, commercial database screening is recommended." Add to templates/ and inject into all DD/Sanctions deliverables.
- [ ] ARCH-GAP-02 HUMINT scope flag — standard text block: "This scope includes components that require discreet source enquiries (HUMINT). HUMINT cannot be performed by this tool. Execution requires qualified human investigators. This section defines the HUMINT scope; delivery is manual." Add to templates/ and inject when Phase 2 / Enhanced DD is selected.

**Security model — all new tasks:**
- Auth: single user, local install — no auth layer required
- Data boundaries: all case data stays in cases/{id}/; historical library stays in firm_profile/; never transmitted except as model prompt content
- PII: DDIntake fields (name, DOB, passport) stored in cases/{id}/intake.json only; sanitisation in KnowledgeLibrary is a HARD GATE — SanitisationError blocks index write if PII detected in stripped output
- Audit: every ingest, every workflow run, every state transition appended to audit_log.jsonl
- Abuse surface: uploaded files parsed by python-docx/PyPDF2 only — no shell execution; web research results truncated to 2000 chars and HTML-stripped (existing guardrail); RiskContextItem fields validated against schema before model call

---

## COMPLETED TASKS

### Sprint-09 (Smoke Test + Scope Expansion — Session 009)
- [x] BUG-02 agents/*/tools.py: _DOC_TOOL_NAMES filter — doc tools excluded from get_tool_definitions()
      when document_manager=None; prevents ToolNotFoundError on runs without documents. (2026-04-04)
- [x] BUG-03 tools/document_manager.py: has_documents() method added; read_excerpt() returns graceful
      message instead of raising FileNotFoundError when doc not found. (2026-04-04)
- [x] BUG-04 agents/junior_analyst/agent.py: _parse_output() handles ```json code block wrapping;
      regex extracts from code block first, then falls back to greedy {.*}. (2026-04-04)
- [x] BUG-05 run.py: active_doc_manager=None guard — only pass DocumentManager to agents when
      has_documents() is True; prevents model hallucinating doc_ids when no docs registered. (2026-04-04)
- [x] SMOKE-01 Option 4 (Policy/SOP) smoke test PASSED — Whistleblower Policy generated, 4 citations,
      final_report.en.md + final_report.en.docx written, audit_log populated. (2026-04-04)
- [x] WORD-01 tools/file_tools.py write_final_report(): auto-generates .docx alongside .md via
      OutputGenerator; graceful skip if python-docx unavailable. (2026-04-04)
- [x] FE-00 Frontend option confirmed: Streamlit (Option A). (2026-04-04)
- [x] SCOPE-01 Scope expanded: Phases 8–12 defined (Frontend, Chaining, New Service Lines,
      Precision Intake, Knowledge Files). Completion recalibrated to 48%. (2026-04-04)
- [x] PLAN-01 Planning session agenda set: 3-level scope hierarchy validation, top 3 scope priorities,
      intake questionnaires (8–12 questions each), knowledge file drafting, chaining design. (2026-04-04)

### Sprint-06 (Shipping Readiness)
- [x] SW-UX-01 setup_wizard.py: collect ANTHROPIC_API_KEY + TAVILY_API_KEY via Prompt.ask(password=True),
      write directly to .env with atomic tmp→replace; empty-value retry loop; no manual file editing
      required. (2026-04-04)

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
