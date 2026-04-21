# Forensic-AI Combined Remediation Plan

**Generated:** 20260421T154211Z
**Covers:**
  - Phase 1: Parametric Monte Carlo (11 workflows, 9,500 runs) — sim_report_*.md
  - Phase 2: Empirical execution (hooks, orchestrator, state machine, schemas) — empirical_report_*.md
  - Phase 3: Future-direction simulation (10 planned workflows) — this file

**Total action items:** 30 (8 confirmed current defects, 22 future-direction risks)

---

## Executive Summary

### Current codebase — confirmed defects (Phase 2 empirical)
| Severity | Count | Top issues |
|----------|-------|-----------|
| P1 (ship-blocking) | 4 | IBAN PII bypass, RiskItem range validation, PM feedback threading |
| P2 (next sprint) | 3 | JuniorDraft empty findings, Partner recovery path, evidence chain mismatch |
| P3 (before scale) | 1 | CaseState last_updated checkpoint fix |

### Future direction — highest risks
| Workflow | Success Rate | Top Risk |
|----------|-------------|---------|
| multi_tenant_workstream | 14.2% | MAX_TURNS |
| expert_witness_report | 24.8% | PIPELINE_ERROR |
| custom_investigation | 27.6% | PIPELINE_ERROR |
| frm_guided_exercise | 28.6% | PIPELINE_ERROR |
| aup_investigation | 31.6% | PIPELINE_ERROR |

### Conflict analysis — highest priority gaps
- **slug**: Artifact filenames appear to be named by agent + version only (e.g. junior_output.v1.json). When two
- **bootstrap**: app.py calls bootstrap() without a try/except wrapper. If bootstrap() raises (missing firm_profile/,
- **bootstrap**: 00_Setup.py calls bootstrap() AND app.py calls bootstrap(). If app.py redirects to setup on bootstra
- **template**: templates/ directory exists but contains no .docx files. Any workflow that calls python-docx with a 
- **locking**: No file locking primitives found in orchestrator.py or tools/file_tools.py. Current atomic write use

---

## 3. Unified Remediation Plan

*Ordered by: severity × proximity to shipping × implementation effort*

*P1 = ship-blocking | P2 = next sprint | P3 = before scale | P4 = post-MVP*

| ID | Priority | Area | Description | Effort | Sprint |
|----|----------|------|-------------|--------|--------|
| FUT-01 | P1 | pii | Add UAE IBAN regex to sanitize_pii (AE07... pattern confirmed bypassed) | S | Sprint-SIM |
| FUT-02 | P1 | pii | Strip null bytes (\x00..\x02) from free-text fields in sanitize_pii | S | Sprint-SIM |
| FUT-03 | P1 | schema | Add ge=1, le=5 validators to RiskItem.likelihood and RiskItem.impact — 0 and 6 both accepted by Pydantic today | S | Sprint-SIM |
| FUT-04 | P1 | orchestrator | Thread pm_feedback into Junior context on revision runs — confirmed missing: feedback_in_context=None on E3.2 | M | Sprint-SIM |
| FUT-05 | P2 | schema | Add min_length=1 to JuniorDraft.findings list — empty findings accepted today | S | Sprint-SIM |
| FUT-06 | P2 | orchestrator | Add Partner→PM feedback recovery path — Partner rejection is currently a terminal dead-end (SIM-04 confirmed) | L | Sprint-SIM |
| FUT-07 | P2 | hook | Investigate enforce_evidence_chain context key mismatch — E2.2 shows 0/6 cases blocked; hook may not fire on r | M | Sprint-SIM |
| FUT-08 | P3 | orchestrator | Fix E3.5 CaseState.last_updated required field — resume from checkpoint fails with validation error | S | Sprint-SIM |
| FUT-09 | P1 | future_workflow | multi_tenant_workstream: CRITICAL — success_rate=14.2%, top failure=MAX_TURNS | L | Sprint-IA-01/02 |
| FUT-10 | P1 | future_workflow | expert_witness_report: CRITICAL — success_rate=24.8%, top failure=PIPELINE_ERROR | L | Sprint-IA-01/02 |
| FUT-11 | P1 | future_workflow | custom_investigation: CRITICAL — success_rate=27.6%, top failure=PIPELINE_ERROR | L | Sprint-IA-01/02 |
| FUT-12 | P1 | future_workflow | frm_guided_exercise: CRITICAL — success_rate=28.6%, top failure=PIPELINE_ERROR | L | Sprint-IA-01/02 |
| FUT-13 | P1 | future_workflow | aup_investigation: CRITICAL — success_rate=31.6%, top failure=PIPELINE_ERROR | L | Sprint-IA-01/02 |
| FUT-14 | P2 | future_workflow | co_work_session: HIGH — success_rate=58.0%, top failure=PIPELINE_ERROR | M | Sprint-IA-01/02 |
| FUT-15 | P2 | future_workflow | evidence_chat_session: HIGH — success_rate=58.0%, top failure=PIPELINE_ERROR | M | Sprint-IA-01/02 |
| FUT-16 | P2 | future_workflow | knowledge_harvester: HIGH — success_rate=61.8%, top failure=HOOK_VETO_POST | M | Sprint-IA-01/02 |
| FUT-17 | P2 | future_workflow | workpaper_promotion: HIGH — success_rate=66.8%, top failure=PIPELINE_ERROR | M | Sprint-IA-01/02 |
| FUT-18 | P2 | future_workflow | app_bootstrap: HIGH — success_rate=67.0%, top failure=PIPELINE_ERROR | M | Sprint-IA-01/02 |
| FUT-19 | P2 | slug | Artifact filenames appear to be named by agent + version only (e.g. junior_output.v1.json). When two workflow  | M | Sprint-IA-01 IA-03 |
| FUT-20 | P1 | bootstrap | app.py calls bootstrap() without a try/except wrapper. If bootstrap() raises (missing firm_profile/, first-run | M | Sprint-IA-01 IA-01 |
| FUT-21 | P1 | bootstrap | 00_Setup.py calls bootstrap() AND app.py calls bootstrap(). If app.py redirects to setup on bootstrap failure, | M | Sprint-IA-01 IA-01 |
| FUT-22 | P2 | template | templates/ directory exists but contains no .docx files. Any workflow that calls python-docx with a template p | M | Sprint-IA-02 |
| FUT-23 | P1 | locking | No file locking primitives found in orchestrator.py or tools/file_tools.py. Current atomic write uses os.repla | M | Sprint-IA-02 (co-work / shipping models 3+) |
| FUT-24 | P3 | audit | append_audit_event in post_hooks.py does not appear to call mkdir(parents=True) before opening audit_log.jsonl | S | Sprint-IA-01 (workpaper) |
| FUT-25 | P2 | future_design | evidence_chat_session: cap CEM context at 50 turns with explicit truncation warning (CEM_CONTEXT_CHARS=16,000  | S | Sprint-IA-02 (CEM) |
| FUT-26 | P2 | future_design | workpaper_promotion: require audit_log.jsonl to exist before promotion — surface friendly error on missing log | S | Sprint-IA-01 |
| FUT-27 | P2 | future_design | knowledge_harvester: implement PII filter (client names, case IDs, financial amounts) as a mandatory pre-write | M | Sprint-IA-02 (future) |
| FUT-28 | P3 | future_design | multi_tenant_workstream + co_work_session: add filelock advisory locking on state.json and audit_log.jsonl bef | M | Sprint-IA-02 (co-work) |
| FUT-29 | P3 | future_design | Prefix artifact filenames with workflow slug to prevent multi-workstream collision: {workflow}_{agent}_output. | S | Sprint-IA-01 IA-03 |
| FUT-30 | P4 | future_design | frm_guided_exercise: define auto-baseline behaviour for 0-document intake (auto-fill fires at 11% — should be  | S | Sprint-IA-02 (FRM guided) |

---

## Priority 1 — Ship-blocking (fix before any external user sees this)

### FUT-01: [pii] Add UAE IBAN regex to sanitize_pii (AE07... pattern confirmed bypassed)
### FUT-02: [pii] Strip null bytes (\x00..\x02) from free-text fields in sanitize_pii
### FUT-03: [schema] Add ge=1, le=5 validators to RiskItem.likelihood and RiskItem.impact — 0 and 6 both accepted by Pydantic today
### FUT-04: [orchestrator] Thread pm_feedback into Junior context on revision runs — confirmed missing: feedback_in_context=None on E3.2
### FUT-09: [future_workflow] multi_tenant_workstream: CRITICAL — success_rate=14.2%, top failure=MAX_TURNS
### FUT-10: [future_workflow] expert_witness_report: CRITICAL — success_rate=24.8%, top failure=PIPELINE_ERROR
### FUT-11: [future_workflow] custom_investigation: CRITICAL — success_rate=27.6%, top failure=PIPELINE_ERROR
### FUT-12: [future_workflow] frm_guided_exercise: CRITICAL — success_rate=28.6%, top failure=PIPELINE_ERROR
### FUT-13: [future_workflow] aup_investigation: CRITICAL — success_rate=31.6%, top failure=PIPELINE_ERROR
### FUT-20: [bootstrap] app.py calls bootstrap() without a try/except wrapper. If bootstrap() raises (missing firm_profile/, first-run), Streaml
### FUT-21: [bootstrap] 00_Setup.py calls bootstrap() AND app.py calls bootstrap(). If app.py redirects to setup on bootstrap failure, and setup
### FUT-23: [locking] No file locking primitives found in orchestrator.py or tools/file_tools.py. Current atomic write uses os.replace() — saf

---

## Priority 2 — Next sprint

### FUT-05: [schema] Add min_length=1 to JuniorDraft.findings list — empty findings accepted today
### FUT-06: [orchestrator] Add Partner→PM feedback recovery path — Partner rejection is currently a terminal dead-end (SIM-04 confirmed)
### FUT-07: [hook] Investigate enforce_evidence_chain context key mismatch — E2.2 shows 0/6 cases blocked; hook may not fire on real payload structure (SIM-01 PARTIAL)
### FUT-14: [future_workflow] co_work_session: HIGH — success_rate=58.0%, top failure=PIPELINE_ERROR
### FUT-15: [future_workflow] evidence_chat_session: HIGH — success_rate=58.0%, top failure=PIPELINE_ERROR
### FUT-16: [future_workflow] knowledge_harvester: HIGH — success_rate=61.8%, top failure=HOOK_VETO_POST
### FUT-17: [future_workflow] workpaper_promotion: HIGH — success_rate=66.8%, top failure=PIPELINE_ERROR
### FUT-18: [future_workflow] app_bootstrap: HIGH — success_rate=67.0%, top failure=PIPELINE_ERROR
### FUT-19: [slug] Artifact filenames appear to be named by agent + version only (e.g. junior_output.v1.json). When two workflow types run 
### FUT-22: [template] templates/ directory exists but contains no .docx files. Any workflow that calls python-docx with a template path will r
### FUT-25: [future_design] evidence_chat_session: cap CEM context at 50 turns with explicit truncation warning (CEM_CONTEXT_CHARS=16,000 confirmed limit; CONTEXT_WINDOW_EXHAUSTED at 14%)
### FUT-26: [future_design] workpaper_promotion: require audit_log.jsonl to exist before promotion — surface friendly error on missing log; auto-init if parent dir exists
### FUT-27: [future_design] knowledge_harvester: implement PII filter (client names, case IDs, financial amounts) as a mandatory pre-write gate before patterns enter shared knowledge library

---

## Priority 3 — Before scale

### FUT-08: [orchestrator] Fix E3.5 CaseState.last_updated required field — resume from checkpoint fails with validation error
### FUT-24: [audit] append_audit_event in post_hooks.py does not appear to call mkdir(parents=True) before opening audit_log.jsonl. If the c
### FUT-28: [future_design] multi_tenant_workstream + co_work_session: add filelock advisory locking on state.json and audit_log.jsonl before Co-Work or SaaS shipping models are enabled
### FUT-29: [future_design] Prefix artifact filenames with workflow slug to prevent multi-workstream collision: {workflow}_{agent}_output.v{N}.json

---

## Priority 4 — Post-MVP

### FUT-30: [future_design] frm_guided_exercise: define auto-baseline behaviour for 0-document intake (auto-fill fires at 11% — should be explicit user opt-in, not silent)

---

*Combined analysis: simulation/run_future.py*
*Phase 1 report: simulation/reports/sim_report_*.md*
*Phase 2 report: simulation/reports/empirical_report_*.md*
*Phase 3 report: simulation/reports/future_sim_report_20260421T154211Z.md*
