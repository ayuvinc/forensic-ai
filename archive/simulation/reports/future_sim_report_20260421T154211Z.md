# Forensic-AI Future-Direction Simulation Report

**Generated:** 20260421T154211Z
**Seed:** 42
**Monte Carlo:** 500 runs × 10 future workflows
**Uncertainty delta:** +5% on all base probabilities (no empirical baseline)
**Source documents:** docs/hld.md, docs/lld/product-ia-design.md, docs/product-packaging.md,
  tasks/ba-logic.md, tasks/todo.md (Sprint-IA-01)

**Note on methodology:** Future workflows are UNBUILT. Probabilities are derived from design
documents, known analogous patterns in existing code, and constraint analysis. The +5%
uncertainty delta represents the epistemic gap between design intent and implementation reality.
Treat all percentages as directional, not predictive.

---

## 1. Future-Direction Monte Carlo Results

*500 runs per planned workflow — parametric with 5% uncertainty delta*

*All probabilities are estimates from design documents — no implementation exists yet.*

| Workflow | Type | Success Rate | Risk | Top Failure Mode | Notes |
|----------|------|-------------|------|-----------------|-------|
| multi_tenant_workstream | pipeline | 14.2% █░░░░░░░░░ | 🔴 CRITICAL | MAX_TURNS | uncertainty +5% |
| expert_witness_report | pipeline | 24.8% ██░░░░░░░░ | 🔴 CRITICAL | PIPELINE_ERROR | uncertainty +5% |
| custom_investigation | pipeline | 27.6% ███░░░░░░░ | 🔴 CRITICAL | PIPELINE_ERROR | uncertainty +5% |
| frm_guided_exercise | pipeline | 28.6% ███░░░░░░░ | 🔴 CRITICAL | PIPELINE_ERROR | uncertainty +5% |
| aup_investigation | pipeline | 31.6% ███░░░░░░░ | 🔴 CRITICAL | PIPELINE_ERROR | uncertainty +5% |
| co_work_session | mode_b | 58.0% ██████░░░░ | 🟠 HIGH | PIPELINE_ERROR | uncertainty +5% |
| evidence_chat_session | mode_b | 58.0% ██████░░░░ | 🟠 HIGH | PIPELINE_ERROR | uncertainty +5% |
| knowledge_harvester | utility | 61.8% ██████░░░░ | 🟠 HIGH | HOOK_VETO_POST | uncertainty +5% |
| workpaper_promotion | utility | 66.8% ███████░░░ | 🟠 HIGH | PIPELINE_ERROR | uncertainty +5% |
| app_bootstrap | mode_b | 67.0% ███████░░░ | 🟠 HIGH | PIPELINE_ERROR | uncertainty +5% |

### Failure breakdown (top 3 per future workflow)

**multi_tenant_workstream** (success 14.2% — CRITICAL)
  - `MAX_TURNS`: 82/500 (16.4%)
  - `HOOK_VETO_PRE`: 74/500 (14.8%)
  - `PIPELINE_ERROR`: 67/500 (13.4%)
  - Input sensitivity: doc_count=0.500, tenant_count=0.132

**expert_witness_report** (success 24.8% — CRITICAL)
  - `PIPELINE_ERROR`: 87/500 (17.4%)
  - `MAX_TURNS`: 71/500 (14.2%)
  - `HOOK_VETO_PRE`: 47/500 (9.4%)
  - Input sensitivity: doc_count=0.667, jurisdiction=0.089

**custom_investigation** (success 27.6% — CRITICAL)
  - `PIPELINE_ERROR`: 108/500 (21.6%)
  - `MAX_TURNS`: 52/500 (10.4%)
  - `TIMEOUT`: 48/500 (9.6%)
  - Input sensitivity: doc_count=0.846, has_template=0.014

**frm_guided_exercise** (success 28.6% — CRITICAL)
  - `PIPELINE_ERROR`: 97/500 (19.4%)
  - `MAX_TURNS`: 58/500 (11.6%)
  - `HOOK_VETO_PRE`: 45/500 (9.0%)
  - Input sensitivity: doc_count=0.625, module_count=0.155

**aup_investigation** (success 31.6% — CRITICAL)
  - `PIPELINE_ERROR`: 81/500 (16.2%)
  - `MAX_TURNS`: 55/500 (11.0%)
  - `TIMEOUT`: 46/500 (9.2%)
  - Input sensitivity: doc_count=1.000, remarks_length=1.000

**co_work_session** (success 58.0% — HIGH)
  - `PIPELINE_ERROR`: 114/500 (22.8%)
  - `SCHEMA_VALIDATION`: 36/500 (7.2%)
  - `HOOK_VETO_PRE`: 35/500 (7.0%)
  - Input sensitivity: doc_count=0.857, concurrent_writers=0.022

**evidence_chat_session** (success 58.0% — HIGH)
  - `PIPELINE_ERROR`: 109/500 (21.8%)
  - `API_ERROR`: 36/500 (7.2%)
  - `HOOK_VETO_PRE`: 36/500 (7.2%)
  - Input sensitivity: turn_count=1.000, doc_count=1.000

**knowledge_harvester** (success 61.8% — HIGH)
  - `HOOK_VETO_POST`: 54/500 (10.8%)
  - `HOOK_VETO_PRE`: 42/500 (8.4%)
  - `PIPELINE_ERROR`: 35/500 (7.0%)
  - Input sensitivity: embedding_available=0.108, source_type=0.059

**workpaper_promotion** (success 66.8% — HIGH)
  - `PIPELINE_ERROR`: 51/500 (10.2%)
  - `HOOK_VETO_PRE`: 39/500 (7.8%)
  - `SCHEMA_VALIDATION`: 26/500 (5.2%)
  - Input sensitivity: workpaper_count=0.287, has_pii_content=0.054

**app_bootstrap** (success 67.0% — HIGH)
  - `PIPELINE_ERROR`: 155/500 (31.0%)
  - `HOOK_VETO_PRE`: 5/500 (1.0%)
  - `API_ERROR`: 4/500 (0.8%)
  - Input sensitivity: has_firm_profile=0.072, first_run=0.068


---

## 2. Future-Direction Conflict Analysis

**Summary:** 5 HIGH, 1 MEDIUM, 0 LOW, 3 INFO

### 🔴 HIGH

**[slug]** Artifact filenames appear to be named by agent + version only (e.g. junior_output.v1.json). When two workflow types run under the same case_id (AUP Type 8 can host multiple workstreams), workflow A's junior_output.v1.json overwrites workflow B's silently. Confirmed risk from BA-IA-03 (min 1 workstream per engagement).
  - Files: schemas/artifacts.py, core/orchestrator.py
  - Fix: Prefix artifact filenames with workflow slug: {workflow}_{agent}_output.v{N}.json (e.g. aup_investigation_junior_output.v1.json). Update persist_artifact hook and orchestrator to use workflow-scoped paths.
  - Sprint ref: `Sprint-IA-01 IA-03`

**[bootstrap]** app.py calls bootstrap() without a try/except wrapper. If bootstrap() raises (missing firm_profile/, first-run), Streamlit shows a blank error page. Combined with an unconditional redirect to 00_Setup.py, this can produce an infinite redirect loop on first-run installs.
  - Files: app.py
  - Fix: Wrap bootstrap() in try/except ImportError/FileNotFoundError. On exception, render a setup prompt directly rather than redirect. Pass caller_file=__file__ to prevent recursive bootstrap calls.
  - Sprint ref: `Sprint-IA-01 IA-01`

**[bootstrap]** 00_Setup.py calls bootstrap() AND app.py calls bootstrap(). If app.py redirects to setup on bootstrap failure, and setup itself calls bootstrap(), the redirect chain becomes circular. First-run users will hit a loop.
  - Files: app.py, pages/00_Setup.py
  - Fix: Setup page must NOT call bootstrap(). Only app.py initialises the session. Setup page should write firm_profile/, then call st.rerun() once.
  - Sprint ref: `Sprint-IA-01 IA-01`

**[template]** templates/ directory exists but contains no .docx files. Any workflow that calls python-docx with a template path will raise FileNotFoundError.
  - Files: templates/
  - Fix: Add at least one reference .docx template for each investigation type. Add a validation step at intake that checks the template file exists before the pipeline starts.
  - Sprint ref: `Sprint-IA-02`

**[locking]** No file locking primitives found in orchestrator.py or tools/file_tools.py. Current atomic write uses os.replace() — safe for single-writer scenarios. Co-Work model (Model 3) and multi-tenant SaaS (Model 5) both require concurrent writes to state.json. Without locking: (1) two consultants writing state.json simultaneously → last write wins, one consultant's status update silently overwritten; (2) two tenant pipelines sharing filesystem → state corruption across tenants.
  - Files: core/orchestrator.py, tools/file_tools.py
  - Fix: For Co-Work/multi-tenant: add advisory file locking via `filelock` library. Pattern: `with FileLock(state_path.with_suffix('.lock')):` around all state reads and writes. For single-user (Models 1, 2), existing os.replace() is sufficient. Gate behind a config flag: ENABLE_FILE_LOCKING = (SHIPPING_MODEL in ('co_work', 'saas')).
  - Sprint ref: `Sprint-IA-02 (co-work / shipping models 3+)`

### 🟡 MEDIUM

**[audit]** append_audit_event in post_hooks.py does not appear to call mkdir(parents=True) before opening audit_log.jsonl. If the case directory doesn't exist yet (new case, workpaper promotion before first pipeline run), FileNotFoundError will block promotion with no recovery path.
  - Files: hooks/post_hooks.py
  - Fix: In append_audit_event, add: `audit_path.parent.mkdir(parents=True, exist_ok=True)` before opening the log file. This makes audit log creation idempotent.
  - Sprint ref: `Sprint-IA-01 (workpaper)`


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

*Future simulation: simulation/harness_future.py | conflict_detector_future.py | run_future.py*
*Source analysis: docs/hld.md | docs/lld/product-ia-design.md | docs/product-packaging.md | tasks/ba-logic.md*
