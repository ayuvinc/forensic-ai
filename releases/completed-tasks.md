# Completed Tasks Archive
Append-only. Each sprint block is added at close. Do not edit existing entries.

---

## Sprint-01 — Phase 1 Foundation (2026-03-29)

- [x] Project plan written and CLAUDE.md committed
- [x] tasks/ scaffold created
- [x] P0-01 requirements.txt + .env.example
- [x] P1-01 config.py
- [x] P1-02 schemas/case.py
- [x] P1-02b schemas/handoff.py
- [x] P1-03 schemas/artifacts.py
- [x] P1-03b schemas/presentation.py
- [x] P1-04 schemas/research.py
- [x] P1-05 core/state_machine.py
- [x] P1-06 core/hook_engine.py
- [x] P1-07 hooks/pre_hooks.py + post_hooks.py
- [x] P1-08 core/tool_registry.py
- [x] P1-09 core/agent_base.py
- [x] P1-10 core/orchestrator.py
- [x] P1-11 tools/research/general_search.py
- [x] P1-12 tools/research/regulatory_lookup.py
- [x] P1-13 tools/research/sanctions_check.py
- [x] P1-14 tools/research/company_lookup.py
- [x] P1-15 tools/file_tools.py

---

## Sprint-02 — Phases 2–6 (~49 modules) (2026-03-29)

- [x] Phase 1 revisions: requirements.txt, config.py, schemas/case.py updated
- [x] schemas/documents.py — NEW
- [x] schemas/evidence.py — NEW
- [x] schemas/plugins.py (AgentHandoff, ArtifactEnvelope, PluginManifest) — NEW
- [x] tools/research/regulatory_lookup.py — jurisdictions param redesign
- [x] tools/research/company_lookup.py — jurisdictions param redesign
- [x] tools/document_manager.py — bounded retrieval design — NEW
- [x] core/setup_wizard.py — env+deps + firm profile wizard
- [x] core/plugin_loader.py — manifest loader — NEW
- [x] tools/file_tools.py — write_envelope, load_envelope added
- [x] agents/junior_analyst/ — manifest.json, agent.py, prompts.py, tools.py
- [x] agents/project_manager/ — manifest.json, agent.py, prompts.py, tools.py
- [x] agents/partner/ — manifest.json, agent.py, prompts.py, tools.py
- [x] workflows/frm_risk_register.py — 8-module pipeline — NEW
- [x] tools/evidence/excel_analyzer.py — NEW
- [x] tools/evidence/email_parser.py — NEW
- [x] tools/evidence/evidence_classifier.py — NEW
- [x] tools/output_generator.py — docx/pptx — NEW
- [x] tools/formatting.py — Arabic translation — NEW
- [x] workflows/new_case_intake.py, investigation_report.py, client_proposal.py, proposal_deck.py, policy_sop.py, training_material.py, persona_review.py, case_tracker.py, browse_sops.py — NEW
- [x] personas/cfo/, lawyer/, regulator/, insurance_adjuster/ — NEW
- [x] ui/menu.py, progress.py, display.py, guided_intake.py — NEW
- [x] templates/arabic_glossary.md — NEW
- [x] run.py — full main loop — NEW
- [x] CODEX_REVIEW.md — sprint-02 review instruction
- [x] Sprint-02 finding fixes: P3 (model_validator), P4 (_sanitize web-only), P5 (load_envelope), P6 (PermissibilityStatus Enum)
- [x] BUG-01 fix: ToolRegistry.call() param renamed name→tool_name (found in QR-05)

---

## QA Gate — Sprint-02 QR-01..16 (2026-03-29 / 2026-04-02)

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

---

## Sprint-03 — Codex Review Completed Findings (2026-04-02 / 2026-04-04)

### C-01 — Workflow quality split
- [x] C-01a DECISION: classify policy_sop / training_material as "Mode B: Assisted generation" — menu.py labels 4/5/7/8 with "Assisted —"; README has Workflow Modes section. Session 006.
- [x] C-01c Added write_artifact + append_audit_event to policy_sop, training_material, client_proposal, proposal_deck. All 4 Mode B workflows write deliverable artifact + audit event. Session 007.

### C-02 — Case lifecycle persistence
- [x] C-02a Added DELIVERABLE_WRITTEN to CaseStatus enum + TERMINAL_STATUSES. Added _mark_deliverable_written() in run.py for choices 4,5,7,8. Session 007.
- [x] C-02b case_tracker _scan_cases() updated; DELIVERABLE_WRITTEN renders as green (terminal). Session 007.

### C-03 — Evidence-chain enforcement
- [x] C-03a Partner agent: _enforce_evidence_chains() overrides approved=True on LEAD_ONLY/INADMISSIBLE evidence. Session 004.
- [x] C-03b Post-hook enforce_evidence_chain added to POST_HOOKS (position 2). HookVetoError on bad chain. Session 004.
- [x] C-03c Evidence items threaded via closure in partner_fn; _build_evidence_items() converts DocumentEntry→EvidenceItem. Session 004.
- [x] C-03d QR-16: 7/7 sub-checks PASS. Session 004.

### C-04 — DocumentManager wiring
- [x] C-04a Added _run_document_ingestion() in run.py for options 2 and 6. 7-type menu + graceful fallback. Session 007.
- [x] C-04b Added _offer_document_ingestion() in new_case_intake.py. Session 007.

### C-05 — README accuracy
- [x] C-05a README "If Interrupted" section rewritten — resume applies to Options 2+6 only. Session 007.
- [x] C-05b README output file table updated: case ID format corrected, intake.json added, Mode B/Full Pipeline distinction. Session 007.

### C-07 — Repo hygiene
- [x] C-07a .gitignore covers .DS_Store, __pycache__/, *.pyc, cases/*, firm_profile/, venv/, .env. Verified Session 006.
- [x] C-07b .gitignore present and correct. Verified Session 006.

---

## Sprint-04 — AK-CogOS v2.0 Remediation (2026-04-04)

- [x] AKR-01 tasks/ba-logic.md created — v2.0 stub
- [x] AKR-02 tasks/ux-specs.md created — v2.0 stub
- [x] AKR-03 framework-improvements.md created at repo root
- [x] AKR-04 releases/ directory + releases/audit-log.md created; .gitignore exception verified; tasks/audit-log.jsonl coexists
- [x] AKR-05 releases/session-001..004.md retrospective summaries created
- [x] AKR-06 CLAUDE.md: AK-CogOS v2.0 Path Overrides + Anti-Sycophancy Protocol appended (append-only, no existing content modified)
- [x] AKR-07 docs/ scaffold: problem-definition.md, scope-brief.md, hld.md, assumptions.md, decision-log.md, release-truth.md, traceability-matrix.md, lld/README.md
- [x] AKR-08a /ba session run: docs/problem-definition.md, docs/scope-brief.md, tasks/ba-logic.md populated via 8-question discovery with AK. User: Maher Hashash MD GoodWork LLC UAE. Session 006.
- [x] AKR-09 Risk assessed: install-claude-commands.sh would DOWNGRADE project commands (project is v2.0, AK-CogOS skills/ is older v1.x). Script not run. Deferred pending AK-CogOS update.
- [x] AKR-10 Audit log format migration notice appended. UPPERCASE event_type convention active from Session 005+.
- [x] AKR-11 framework/governance/metrics-tracker.md populated: 5 session entries (sessions 001–005). Session 006.
- [x] AKR-12 channel.md rewritten to v2.0 format with machine-readable sections.
- [x] AKR-13 /codex-intake-check PASS: all required artifacts present. Gaps documented in risk-register.md. ARCHITECTURE_COMPLETE audit event appended. Session 006.

---

## Sprint-06 — Shipping Readiness (2026-04-04)

- [x] SW-UX-01 setup_wizard.py: collect API keys via Prompt.ask(password=True), write to .env with atomic tmp→replace; empty-value retry loop.

---

## Sprint-09 — Smoke Test + Scope Expansion (2026-04-04)

- [x] BUG-02 agents/*/tools.py: _DOC_TOOL_NAMES filter — doc tools excluded from get_tool_definitions() when document_manager=None.
- [x] BUG-03 tools/document_manager.py: has_documents() added; read_excerpt() returns graceful message on FileNotFoundError.
- [x] BUG-04 agents/junior_analyst/agent.py: _parse_output() handles ```json code block wrapping.
- [x] BUG-05 run.py: active_doc_manager=None guard — only pass DocumentManager when has_documents() is True.
- [x] SMOKE-01 Option 4 (Policy/SOP) smoke test PASSED — Whistleblower Policy, 4 citations, .md + .docx written, audit_log populated.
- [x] WORD-01 tools/file_tools.py write_final_report(): auto-generates .docx via OutputGenerator; graceful skip if python-docx missing.
- [x] FE-00 Frontend confirmed: Streamlit (Option A).
- [x] SCOPE-01 Scope expanded: Phases 8–12 defined. Completion recalibrated to 48%.
- [x] PLAN-01 Planning session agenda set: scope hierarchy, intake questionnaires, knowledge files, chaining design.

---

## Sprint-10A — Schemas (feature/sprint-10A-schemas-kf00, 2026-04-07)

- [x] ARCH-S-01 schemas/artifacts.py: RiskContextItem added (incident, existing_controls, probability 1-5, impact 1-5, consultant_notes).
- [x] ARCH-S-02 schemas/dd.py: new file — DDIntakeIndividual (14 fields), DDIntakeEntity (14 fields), DDReport (subject_profile, methodology, sanctions_results, pep_results/beneficial_ownership, adverse_media, risk_classification LOW/MEDIUM/HIGH, recommendation).
- [x] ARCH-S-03 schemas/transaction_testing.py: new file — TTIntakeContext, TestingPlan (tests: list[TestObjective], population, method, caveats), TTResult.
- [x] ARCH-S-04 schemas/engagement_scope.py: new file — ScopeIntake, ScopeRecommendation, ConfirmedScope.
- [x] ARCH-S-05 core/state_machine.py: SCOPE_CONFIRMED added to CaseStatus enum; INTAKE_CREATED→SCOPE_CONFIRMED and SCOPE_CONFIRMED→DELIVERABLE_WRITTEN transitions added.
- [x] ARCH-S-06 tools/knowledge_library.py (scaffold): SanitisationError exception class defined.
- [x] ARCH-S-07 schemas/artifacts.py: SanitisedIndexEntry added (service_type, industry, jurisdiction, company_size_band, engagement_date_year, scope_components, risk_count, key_patterns, source_file_hash, provenance BASELINE/FROM_SIMILAR_ENGAGEMENT).

---

## Sprint-10B — Knowledge Files (feature/sprint-10B-knowledge-files, 2026-04-07)

- [x] KF-NEW knowledge/engagement_taxonomy/framework.md + sources.md — all 11 engagement types, triggering scenarios, chains, exclusions, red flags.
- [x] KF-00 knowledge/policy_sop/framework.md — 8 quality gaps fixed; KQ-01 claim labels applied; sources.md created (KQ-03).
- [x] KF-01 knowledge/transaction_testing/framework.md + sources.md — ACFE methodology, Benford's Law, 6 fraud typologies, UAE regulatory testing requirements.
- [x] KF-02 knowledge/due_diligence/framework.md + sources.md — FATF/ACFE 5-phase methodology, risk classification criteria, licensed DB disclaimer.
- [x] KF-04 knowledge/sanctions_screening/framework.md + sources.md — 5 official screening lists, PEP methodology, false positive analysis.

---

## Sprint-10B-KQ — Knowledge Quality Remediation (feature/sprint-10B-knowledge-files, 2026-04-07)

Quality standard: docs/lld/knowledge-quality-standard.md

- [x] KQ-01 knowledge/policy_sop/framework.md: [LAW]/[BEST_PRACTICE]/[PRODUCT_RULE]/[ADVISORY] labels applied; absolute language softened; provenance metadata added; quality tier C→B.
- [x] KQ-02 knowledge/frm/frm_framework.md + knowledge/investigation/investigation_framework.md: quality header (tier B) + provenance metadata added.
- [x] KQ-03 knowledge/policy_sop/sources.md: created — UAE onshore, DIFC, ADGM, India (SEBI/POSH/DPDP), UK (FCA/ICO), international (ISO 37001, ACFE, IIA).
- [x] KQ-04 knowledge/due_diligence/sources.md: created — UAE registries (MOEC, DED, ADGM, DIFC), GCC, India (MCA21), UK (Companies House), OpenCorporates.
- [x] KQ-05 knowledge/sanctions_screening/sources.md: created — 5 official list URLs; PEP registers noted as not openly searchable.
- [x] KQ-06 knowledge/transaction_testing/sources.md: created — ACFE (subscription), IIA, UAE CBUAE/DFSA/SCA/ADGM FSRA URLs, Benford's reference.
- [x] KQ-07 knowledge/engagement_taxonomy/sources.md: created — ACFE Practice Guides, IIA IPPF, UAE SCA/DFSA/ADGM engagement requirements.

---

## Phase 13 — Planning Gates Confirmed (2026-04-06)

- [x] FRM-R-00 Guided-exercise flow validated with Maher — CONFIRMED Session 010. Edit = structured conversation, model recommends all parameters. See BA-002.
- [x] ZID-00 Content floor per workflow defined — CONFIRMED Session 010. All 7 workflows defined. See BA-004.

---

## Sprint-10E — New Service Line Workflows (feature/sprint-10B-knowledge-files, 2026-04-07)

- [x] SL-GATE-01 workflows/due_diligence.py — Mode B; Individual/Entity branch; 5-phase methodology; ARCH-GAP-01 always injected; ARCH-GAP-02 if Phase 2.
- [x] SL-GATE-02 workflows/sanctions_screening.py — Mode B; aliases capped at 3; deduped citations; clearance memo or full report.
- [x] SL-GATE-03 workflows/transaction_testing.py — 2-stage intake; testing plan proposed + confirmed before document ingestion; state INTAKE_CREATED → SCOPE_CONFIRMED → DELIVERABLE_WRITTEN.

---

## Sprint-10H — Disclaimers and Templates (feature/sprint-10B-knowledge-files, 2026-04-07)

- [x] ARCH-GAP-01 templates/disclaimer_licensed_db.md — standard licensed-DB gap disclaimer; injected in all DD and Sanctions deliverables.
- [x] ARCH-GAP-02 templates/disclaimer_humint_scope.md — HUMINT scope flag; injected when Phase 2/Enhanced DD selected.

---

## Sprint-10F — Engagement Scoping Workflow (feature/SCOPE-WF-01-engagement-scoping, 2026-04-07)

- [x] SCOPE-WF-01 workflows/engagement_scoping.py — 5-step problem-first flow per BA-010; reads knowledge/engagement_taxonomy/framework.md at runtime; produces ConfirmedScope; routes to existing workflows via _WORKFLOW_ROUTE map.
- [x] SCOPE-WF-02 run.py + ui/menu.py — Option 0 "Scope New Engagement" added (SCOPING category); exit moved from "0" to "q"; choices list updated to ["q","0".."13"].

## Phase 8 Completed Tasks — Archived Session 022 (2026-04-19)

All tasks below are QA_APPROVED and committed. AC criteria omitted for brevity.

- [x] Sprint-10I — RESEARCH_MODE flag + knowledge_only mode for all 4 research tools (BUG-09a..e) — DONE
- [x] P8-01 — streamlit added to requirements.txt — DONE
- [x] P8-03-SHARED — streamlit_app/shared/session.py, intake.py, pipeline.py — DONE
- [x] P8-04-APP — app.py entry point — DONE
- [x] P8-07-FE09 — DOCX template_path fix (via P8-05a) — DONE
- [x] ARCH-INS-01 — PipelineEvent severity (CRITICAL/WARNING/INFO) in run_in_status() — QA_APPROVED
- [x] P8-08-PAGES — 10 workflow pages (Investigation, Persona Review, Policy SOP, Training, Proposal, PPT Pack, Scope, DD, Sanctions, TT) — QA_APPROVED
- [x] ARCH-INS-02 — Materialized case index (cases/index.json, _update_case_index, build_case_index) — QA_APPROVED
- [x] P8-09a — pages/9_Case_Tracker.py — QA_APPROVED (commit 8908fcb)
- [x] P8-10a — pages/settings.py — QA_APPROVED (commit 62126e6)
- [x] P8-10b — pages/10_Team.py — QA_APPROVED (commit f85153e)
- [x] P8-11a — Document ingestion UI (4 pages) — QA_APPROVED (commit f3c0ad9)
- [x] Sprint-10L Phase A — SRL-01..04 — PM/Partner mode-aware review chain — P7-GATE PASSED
- [x] Sprint-10K (PPH-01..04) — RESEARCH_MODE smart default, sanctions warning, display banner, guardrails docs — DONE
- [x] BUG-10 — Citation guard mode-aware fix (NoCitationsError blocked knowledge_only) — DONE
- [x] Sprint-10J (TAX-01..06) — Taxonomy JSON files (industries, frm_modules, jurisdictions, routing_table), prompt_with_options UI helper, wire into intake flows — DONE

---

## Phase C Completed Tasks — Archived Session 026 (2026-04-20, commit c6a0599)

- [x] EMB-02-REF — pages/12_Case_Tracker.py + schemas/documents.py — `embedding_status` field on DocumentEntry; badge rendering in Case Tracker detail expander — QA_APPROVED
- [x] TPL-02 — tools/template_manager.py — TemplateManager: resolve/validate/update_custom; path-traversal blocked; GW_ style validation; ValidationResult with has_critical_missing — QA_APPROVED
- [x] UX-F-03 — streamlit_app/shared/pipeline.py — run_in_status() severity (CRITICAL/WARNING/INFO) wired to st.error/st.warning/st.info — QA_APPROVED
- [x] UX-F-04 — streamlit_app/shared/session.py + bootstrap() — active_project plumbed through session — QA_APPROVED
- [x] UX-F-05 — pages/12_Case_Tracker.py — on_select="rerun" dataframe row-click + selectbox fallback — QA_APPROVED
- [x] UX-F-07 — pages/14_Settings.py — completeness indicator chips moved to top of Settings page — QA_APPROVED
- [x] TEST-04 — tests/test_template_manager.py — 12 tests; ValidationResult, path-traversal, GW_ style checks — QA_APPROVED
- [x] TEST-06 — tests/test_case_tracker_page.py — 8 tests; badge rendering, row-click, fallback — QA_APPROVED
- [x] TEST-07 — tests/test_pipeline_severity.py — 6 tests; severity-to-widget mapping — QA_APPROVED

---

## Phase D Completed Tasks — Archived Session 027 (2026-04-20, commit dfe9d65)

- [x] EMB-03-REF — pages/12_Case_Tracker.py — document embedding badges (🟢/🟡/🔴/⚪) from document_index.json; badge expander in case detail; F_Final/ search for P9 report files — QA_APPROVED
- [x] TPL-03 — pages/14_Settings.py — 4-tab layout (Firm Profile/Pricing/Team & T&C/Report Templates); 5 completeness chips above tabs; per-workflow template upload/preview/reset; critical GW_ style gate — QA_APPROVED
- [x] TPL-04 — streamlit_app/shared/intake.py — template_selector() collapsed expander (saved/upload/plain); session state persistence; template_selector_ready() gate helper — QA_APPROVED
- [x] WORK-01 — workflows/workpaper.py — WorkpaperGenerator; 9-section ACFE workpaper; single Sonnet call; PRELIMINARY watermark; versioned D_Working_Papers/interim_workpaper.vN.md; atomic write; WORKPAPER_GENERATED audit event — QA_APPROVED
- [x] P9-UI-01 — pages/01_Engagements.py — two-panel named engagement home; New Engagement wizard with slug preview + collision detection; A-F folder tree expander; Run Workflow button sets active_project + st.switch_page() — QA_APPROVED
- [x] P9-02 — tools/project_manager.py — ProjectManager A-F lifecycle; all-or-nothing folder creation with rollback; InputSession; session notes/key facts/red flags append; interim context write; context summary; atomic JSON writes — QA_APPROVED (unlisted dep, built inline)
- [x] KL-00 — knowledge/manifest.json — 14-entry manifest covering all knowledge/*.md; fields: doc_id, path, domain, version, effective_date, authority_level, title, tags — QA_APPROVED
- [x] KL-01 — tools/knowledge_retriever.py — KnowledgeRetriever 3-layer ChromaDB lookup (kb_base/kb_user_sanitised/kb_engagement); KnowledgeBundle.as_context_block(); graceful fallback when chromadb unavailable — QA_APPROVED
- [x] ACT-00 — logs/.gitkeep + .gitignore — logs/ directory tracked; logs/*.jsonl gitignored — QA_APPROVED
- [x] ACT-01 — tools/activity_logger.py — ActivityLogger append-only JSONL; 50MB rotation; fire-and-forget; module-level singleton; 10 event categories — QA_APPROVED

---

## Phase E Completed Tasks — Archived Session 028 (2026-04-20, commit 0c127e9)

- [x] WORK-02 — pages/12_Case_Tracker.py — "Generate Workpaper" button in case detail expander; status-gated routing (_TERMINAL download-only, INTAKE_CREATED disabled+tooltip, _ELIGIBLE active); _load_source_artifacts() searches E_Drafts/ then root; calls WorkpaperGenerator.generate() + st.download_button() — QA_APPROVED
- [x] WORK-03 — streamlit_app/shared/done_zone.py — enable_workpaper: bool = False param; secondary "Generate Interim Workpaper" button with spinner; wired on FRM (pages/06_FRM.py) and Investigation (pages/02_Investigation.py) done stages — QA_APPROVED
- [x] ACT-02 — session.py/pipeline.py/settings.py/file_tools.py — SESSION_START in bootstrap(); PIPELINE_START/COMPLETE/ERROR in run_in_status(); SETTINGS event with old/new values in Settings save; DOCUMENT event in write_artifact(); DELIVERABLE event in mark_deliverable_written() — QA_APPROVED
- [x] ACT-03 — pages/15_Activity_Log.py — paginated log viewer (50/page, prev/next); date range + category multiselect + free-text filters; CSV export; act_log_warn sidebar banner; named 15_ (07 conflicts with 07_Proposal.py) — QA_APPROVED
- [x] KL-02 — tools/knowledge_harvester.py — harvest_case(case_id): loads partner_approval + junior_output; _sanitise_patterns() strips _BLOCKED_FIELDS + PII regex; _promote_to_firm_index() appends hashed entry to firm_profile/knowledge/engagement/index.jsonl; writes cases/{id}/knowledge_export/approved_patterns.json atomically; KNOWLEDGE_HARVEST_COMPLETE audit event — QA_APPROVED
- [x] P9-UI-02 — schemas/case.py + intake.py + pages/06_FRM.py + core/orchestrator.py — engagement_id: Optional[str] in CaseIntake; render_engagement_banner() info banner + pre-fill client_name; FRM pre-writes state.json with engagement_id before pipeline; orchestrator._set_status() carries forward engagement_id on each transition — QA_APPROVED
- [x] TEST-05 — tests/test_project_schema.py — ProjectIntake slug validation, path traversal rejection, empty slug rejection, InputSession lifecycle, ProjectState health enum; 120 tests pass total — QA_APPROVED

---

## Post-Session Warning Fixes — AK Approved (2026-04-20, commit b71952b)

- [x] W-02/TEST-07b — tests/test_file_tools_artifacts.py — 11 tests: write_final_report() file creation, language param, no tmp, interim/ migration, permanent files preserved; mark_deliverable_written() state value, audit event, workflow field, last_updated refresh. 131 total tests pass — RESOLVED
- [x] W-03 — schemas/documents.py: chunk_count: Optional[int] added to DocumentEntry; tools/embedding_engine.py: chunk_count(doc_id) method queries ChromaDB; tools/document_manager.py: sets entry.chunk_count after successful embed; pages/12_Case_Tracker.py: passes chunk_count to _embedding_badge() — badge now shows "🟢 Indexed — N chunks" — RESOLVED
- [x] W-06 — pages/00_Setup.py: ActivityLogger SETUP/setup_completed event logged on "Launch GoodWork →" click; fire-and-forget, non-blocking — RESOLVED

---

## Phase F Completed Tasks — Session 029 (2026-04-20, commit 4315d2a)

- [x] CONV-01 — workflows/evidence_chat.py — EvidenceChat class: chat() single Sonnet turn; CEM_CONTEXT_CHARS=16000 cap enforced via _trim_history(); EmbeddingEngine.retrieve() with DocumentManager.find_relevant_docs() fallback; context from DocumentIndex + key_facts.json + red_flags.json; session_end() flushes transcript to D_Working_Papers/evidence_chat_{ts}.md; session_end_recovered() for mid-session app close — QA_APPROVED
- [x] CONV-02 — streamlit_app/shared/evidence_chat_panel.py — persistent collapsible panel (shared component, not standalone page per AK locked decision); two-panel layout st.columns([1,2]); doc selector with embedding status badges; st.chat_input + st.chat_message rendering; Save as Lead/Key Fact/Red Flag action buttons per turn; "Evidence Exploration Mode" warning banner; End Conversation triggers session_end(); leads_register.json append; audit events on save actions — QA_APPROVED
- [x] AIC-01 — streamlit_app/shared/aic.py render_intake_questions() — Haiku generates up to 3 follow-up questions post-intake; displayed via st.chat_message("assistant") per spec; st.text_area answers; "Save & Continue" persists to D_Working_Papers/intake_qa.json; "Skip for now" button; state machine in session_state — QA_APPROVED
- [x] AIC-02 — streamlit_app/shared/aic.py render_prefinalrun_review() — Sonnet generates 3-5 warning cards from accumulated materials; Resolve/Proceed anyway per card; Run button gated until all cards acknowledged; results to D_Working_Papers/prefinalrun_review.json; severity-styled cards using brand CSS classes — QA_APPROVED
- [x] AIC-03 — tools/project_manager.py — ProjectManager.get_intake_qa_context(slug) + get_prefinalrun_context(slug): read D_Working_Papers/ JSON files; return formatted strings with section headers for agent context injection; return "" when files absent — QA_APPROVED
- [x] P9-04a — tools/file_tools.py — AF_FOLDERS tuple: 6 A-F folder names constant — QA_APPROVED
- [x] P9-04b — tools/file_tools.py — is_af_project(case_id) -> bool: True when cases/{id}/E_Drafts/ exists; False for legacy UUID cases — QA_APPROVED
- [x] config.py — CEM_CONTEXT_CHARS=16000; CONTEXT_BUDGET_CHARS=400000 added

---

## Phase G Completed Tasks — Session 029 (2026-04-20, commit 9f83126)

- [x] P9-04c — tools/file_tools.py — artifact_path() and next_version() AF-aware: AF projects route to E_Drafts/; legacy unchanged. load_envelope() searches E_Drafts/ first with root fallback. write_final_report() writes to F_Final/ for AF projects. — QA_APPROVED
- [x] P9-04d — tools/file_tools.py — write_final_report() migration: AF projects move root *.v*.json → E_Drafts/; legacy projects → interim/ (unchanged). — QA_APPROVED
- [x] P9-05 — pages/16_Workspace.py — Input Session workspace: project header; A-F folder tree with per-folder upload; Input/Final Run mode radio; Input panel (evidence upload → C_Evidence/, session notes, key facts form, red flags form, context budget bar + 75% warning); Final Run panel (materials summary, AIC-02 gate, Run Pipeline button). Engagements page wired with Open Workspace → switch_page(16_Workspace.py). — QA_APPROVED
- [x] P9-06 — tools/document_manager.py — get_total_chars(), context_usage_pct(), _trigger_interim_context_write() (Haiku, best-effort, non-blocking), get_context_for_agents() (returns interim_context.md when present + new docs since, else all excerpts). register_document() auto-checks ≥75% threshold. — QA_APPROVED
- [x] RD-01 — tools/report_builder.py — BaseReportBuilder: add_cover_page(), add_toc(), add_section(), add_subsection(), set_header(), set_footer(), save() (atomic .tmp→os.replace). Template fallback to blank Document on missing/incompatible template. — QA_APPROVED

---

---

## Phase H — RD-02..06, P9-07A/B, P9-08 (2026-04-20 — Session 030, commit dff5671)

- [x] RD-02: `streamlit_app/shared/template_selector.py` — `render_template_selector(workflow_type)`, `_save_template()`, `_clear_template()`; saves to firm.json["templates"][workflow_type]
- [x] RD-03: `tools/file_tools.py:write_final_report()` — uses BaseReportBuilder instead of OutputGenerator; accepts `workflow` and `section_overrides` params; calls _version_existing_report() before write
- [x] RD-04: `tools/file_tools.py:_version_existing_report(case_id)` — moves final_report.* to Previous_Versions/final_report.v{N}.*; AF-aware path resolution
- [x] RD-05: `workflows/investigation_report.py` — 13-section section_overrides dict passed to write_final_report(); AI review wired after orch.run(), before write
- [x] RD-06: `workflows/frm_risk_register.py` — 7-section section_overrides; run_frm_finalize() accepts optional context param; AI review wired
- [x] P9-07Ac: `streamlit_app/shared/session.py:bootstrap()` — loads default_language_standard from firm.json into session_state
- [x] P9-07Ba: `agents/shared/language_standards.py` — LANGUAGE_STANDARD_BLOCKS dict (4 keys: acfe/expert_witness/regulatory/board_pack) + get_language_block()
- [x] P9-07Bb/Bc: All three agent prompts (junior/pm/partner) accept language_standard param; __call__() passes context.get("language_standard","acfe")
- [x] P9-08a: `agents/reviewer/review_agent.py` — ReviewAgent.__call__(draft, context) → list[ReviewAnnotation]
- [x] P9-08b: `schemas/artifacts.py:ReviewAnnotation` — Pydantic model with finding_id, support_level, evidence_cited, logic_gaps, rewritten_text
- [x] P9-08c: ReviewAgent logic — citations=[] → auto-unsupported (no API call); Haiku single-turn for rest; persists to D_Working_Papers/ai_review_{YYYYMMDD}.json
- [x] P9-08d: ReviewAgent wired in investigation_report.py + frm_risk_register.py (after orch.run(), before write_final_report())
- [x] P9-08e: `pages/06_FRM.py:_render_ai_review_badges()` — 🟢/🟡/🔴 expandable badges per risk item in done stage

20 ACs verified QA_APPROVED. No regressions.

---

## Phase I — P9-09 (2026-04-20 — Session 031, commit c8ee66f)

- [x] P9-09a: All three intake forms (`generic_intake_form`, `frm_intake_form`, `dd_intake_form`) — pre-fill client_name from project meta; `disabled=True` on field; use project slug as `case_id` when `active_project` is set — QA_APPROVED
- [x] P9-09b: `streamlit_app/shared/intake.py` — `get_project_dm(st)` returns `DocumentManager(slug)` for project; `get_project_language_standard(st)` reads from index entry. Investigation page: project DM fallback + language_standard in headless_params. FRM confirm: project DM fallback. PARTIAL: `interim_context.md` content accessible via DM but not injected into agent prompt text (get_context_for_agents() not called by agents — scoped to Sprint-EMB/EMB-04). — QA_APPROVED with warning
- [x] P9-09c: `tools/file_tools.py:get_final_report_path(case_id)` — returns `F_Final/final_report.en.md` for AF projects; all 8 done-stage workflow pages use this instead of hardcoded root path — QA_APPROVED
- [x] P9-09d: `pages/12_Case_Tracker.py` — "View Project" button rendered when `engagement_id` is set on a case; sets `active_project` and switches to Engagements page; absent for legacy UUID cases — QA_APPROVED
- [x] P9-09e: Backward compatibility — when `active_project` is not set, all intake forms fall through to UUID case_id generation; `get_project_dm` returns None; pipeline behavior unchanged — QA_APPROVED
- [x] status-update skill: `.claude/commands/status-update.md` — `/status-update` slash command for comprehensive project status table

5 ACs verified, 4 full PASS, 1 partial (P9-09b interim_context injection depth). 131 tests pass. No regressions.
