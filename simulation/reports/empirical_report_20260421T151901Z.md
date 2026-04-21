# Forensic-AI Empirical Simulation Report — Phase 2

**Generated:** 20260421T151901Z
**Phase 1 parametric report:** simulation/reports/sim_report_*.md
**Methodology:** Real code execution — hooks, orchestrator, state machine, schemas — with controlled inputs.

---

## 1. PII Sanitisation — Empirical Results

*Ran 15 inputs through real `sanitize_pii` hook*

### What sanitize_pii STRIPS (confirmed)

- ✓ `passport_number`: Stripped to: 'passport: [PASSPORT_REDACTED]'
- ✓ `bank_account`: Stripped to: 'account number: [ACCOUNT_REDACTED]'
- ✓ `ssn`: Stripped to: 'SSN: [SSN_REDACTED]'
- ✓ `credit_card`: Stripped to: 'card: [ACCOUNT_REDACTED]'

### What sanitize_pii MISSES (confirmed gaps)

- 🔴 `iban_uae`: PII PASSED THROUGH UNCHANGED: 'iban: AE070331234567890123456'
- 🔴 `null_bytes`: PII PASSED THROUGH UNCHANGED: '\x00\x01\x02'

**SIM-05..14 STATUS: CONFIRMED** — 2 PII type(s) bypass sanitize_pii

### Special characters / injection strings (passed through — expected for non-PII)

- ℹ `xss_script`: passed (not a PII pattern — hook works as designed)
- ℹ `sql_injection`: passed (not a PII pattern — hook works as designed)
- ℹ `xss_img`: passed (not a PII pattern — hook works as designed)
- ℹ `jinja_template`: passed (not a PII pattern — hook works as designed)
- ℹ `log4shell`: passed (not a PII pattern — hook works as designed)
- ℹ `literal_null`: passed (not a PII pattern — hook works as designed)
- ℹ `literal_undefined`: passed (not a PII pattern — hook works as designed)
- ℹ `literal_none`: passed (not a PII pattern — hook works as designed)
- ℹ `normal_text`: passed (not a PII pattern — hook works as designed)

---

## 2. Hook Chain Empirical Results

### E1.2 validate_input

- → `valid`: PASSED — Correctly passed valid payload
- 🛡 `empty_case_id`: BLOCKED — [validate_input] blocked: Missing required fields: ['case_id']
- 🛡 `none_case_id`: BLOCKED — [validate_input] blocked: Missing required fields: ['case_id']
- 🛡 `empty_workflow`: BLOCKED — [validate_input] blocked: Missing required fields: ['workflow']
- 🛡 `none_workflow`: BLOCKED — [validate_input] blocked: Missing required fields: ['workflow']
- 🛡 `both_empty`: BLOCKED — [validate_input] blocked: Missing required fields: ['case_id', 'workflow']
- 🛡 `missing_case_id`: BLOCKED — [validate_input] blocked: Missing required fields: ['case_id']
- 🛡 `missing_workflow`: BLOCKED — [validate_input] blocked: Missing required fields: ['workflow']

### E1.3 Pre-hook chain (all 4 hooks)

- → `valid_en`: PASSED — _meta attached
- 🛡 `missing_case_id`: BLOCKED — [validate_input] blocked: Missing required fields: ['case_id']
- → `pii_in_desc`: PASSED — description mutated: 'card: 4111111111111111'→'card: [ACCOUNT_REDACTED]'; _meta attached
- → `arabic_lang`: PASSED — _meta attached
- → `bad_language`: PASSED — language normalised: zh→en; _meta attached
- 🛡 `empty_workflow`: BLOCKED — [validate_input] blocked: Missing required fields: ['workflow']

### E2.1 validate_schema (JuniorDraft)

- → `valid_full`: PASSED — Schema accepted payload
- 🛡 `missing_findings`: BLOCKED — [validate_schema] blocked: 1 validation error for JuniorDraft
findings
  Input should be a valid lis
- → `empty_findings_list`: PASSED — Schema accepted payload
- → `empty_citations`: PASSED — Schema accepted payload
- → `extra_unknown_field`: PASSED — Schema accepted payload
- 🛡 `missing_summary`: BLOCKED — [validate_schema] blocked: 1 validation error for JuniorDraft
summary
  Field required [type=missing
- 🛡 `missing_citations`: BLOCKED — [validate_schema] blocked: 1 validation error for JuniorDraft
citations
  Field required [type=missi

### E2.2 enforce_evidence_chain

- ✓ `valid_evidence`: PASSED — Hook did not block
- ✓ `bad_evidence_id`: PASSED — Hook did not block — UNEXPECTED: should have blocked
- ✓ `non_permissible_evidence`: PASSED — Hook did not block — UNEXPECTED: should have blocked
- ✓ `empty_supporting_evidence`: PASSED — Hook did not block
- ✓ `non_evidence_workflow`: PASSED — Hook did not block
- ✓ `pm_agent_skips`: PASSED — Hook did not block

**SIM-01 hook gap:** 0 cases blocked, 6 passed

### E2.3 Hook ordering (persist_artifact vs extract_citations)

- → `write_artifact`: artifact written: ['junior_output.v1.json']
- → `empty_source_url`: citations_index written with 0 entries
- → `persist_before_citations`: SIM-16 REFUTED: both artifact and citations_index written

---

## 3. Orchestrator Revision Loop — Empirical Results

| Test | Description | Outcome | Jr Calls | PM Calls | Detail |
|------|-------------|---------|----------|----------|--------|
| E3.1 | Basic pipeline — no revisions | ✓ PASS | 1 | 1 | junior_calls=1, pm_calls=1, terminal_status=owner_ready |
| E3.2 | PM revision feedback threading | ✓ PASS | 2 | 2 | junior_calls=2, pm_calls=2, feedback_in_context=None — SIM-02 CONFIRMED: PM feed |
| E3.3 | Revision limit exhaustion | ✓ PASS | 3 | 2 | Raised RevisionLimitError after junior_calls=3, pm_calls=2 — PM exceeded max rev |
| E3.4 | Partner revision is terminal | ✓ PASS | 1 | 1 | Raised PipelineError after partner called 1 time(s) — Partner requested revision |
| E3.5 | Resume from checkpoint | ⚡ EXCEPTION | 0 | 0 | 1 validation error for CaseState
last_updated
  Field required [type=missing, in |

- **E3.2** (SIM-02): ✓ CONFIRMED — junior_calls=2, pm_calls=2, feedback_in_context=None — SIM-02 CONFIRMED: PM feedback NOT in Junior c
- **E3.3** (SIM-02): ✓ CONFIRMED — Raised RevisionLimitError after junior_calls=3, pm_calls=2 — PM exceeded max revision rounds (2) — M
- **E3.4** (SIM-04): ✓ CONFIRMED — Raised PipelineError after partner called 1 time(s) — Partner requested revision — re-run pipeline f

---

## 4. State Machine Boundary — Empirical Results

**Valid transitions:** 14 PASS, 0 FAIL out of 14
**Invalid transitions blocked:** 7 PASS, 0 FAIL out of 7

**Special cases:**
- ℹ **E4.3-pipeline_error_reachability**: reachable_via_transition=False, in_TERMINAL_STATUSES=True. SIM-17 CONFIRMED: orchestrator sets PIPELINE_ERROR directly, bypassing transition(). This i
  → SIM-17
- ✓ **E4.4-rejected_recovery**: Full path OK: OWNER_READY→owner_rejected→junior_draft_complete
- ✓ **E4.5-is_terminal_consistency**: All 12 states consistent

---

## 5. Schema Adversarial — Empirical Results

| Test | Schema | Input | Outcome | Gap? | Finding |
|------|--------|-------|---------|------|---------|
| E5.1-zero_risk | RiskItem | likelihood=0, impact=0 | ACCEPTED | YES | SIM-LOW (RiskItem zero values) |
| E5.2-null_content_en | FinalDeliverable | content_en=None | REJECTED | no | SIM schema gap REFUTED |
| E5.3-empty_excerpt | EvidenceItem | source_excerpt='' | REJECTED | no | SIM-MEDIUM REFUTED |
| E5.4-slug_traversal | derive_slug | traversal_inputs | REJECTED | no | R-019 CONFIRMED FIXED |
| E5.5-empty_findings | JuniorDraft | findings=[] | ACCEPTED | YES | SIM-02 contributing factor (empty_findings) |
| E5.6-likelihood=6 | RiskItem | likelihood=6 | ACCEPTED | YES | RiskItem range validation gap |
| E5.6-impact=6 | RiskItem | impact=6 | ACCEPTED | YES | RiskItem range validation gap |
| E5.6-likelihood=0 | RiskItem | likelihood=0 | ACCEPTED | YES | RiskItem range validation gap |

**5 schema gap(s) confirmed:**
- 🔴 **RiskItem.likelihood=0, impact=0**: risk_rating=0 — zero-risk item accepted by schema
- 🔴 **JuniorDraft.findings=[]**: Empty findings accepted — zero-findings draft can pass schema and reach PM
- 🔴 **RiskItem.likelihood=6**: Out-of-range value accepted: likelihood=6, impact=3, rating=18
- 🔴 **RiskItem.impact=6**: Out-of-range value accepted: likelihood=3, impact=6, rating=18
- 🔴 **RiskItem.likelihood=0**: Out-of-range value accepted: likelihood=0, impact=5, rating=0

---

## 6. SIM Ticket Verdict Table

| SIM-N | Phase 1 Claim | Empirical Verdict | Evidence |
|-------|---------------|-------------------|----------|
| SIM-01 | investigation_report 54.4% (HOOK_VETO_POST evidence chain) | PARTIAL | 0 evidence chain block cases confirmed |
| SIM-02 | frm_risk_register revision limits + feedback threading | CONFIRMED | PM feedback threading: CONFIRMED | Raised RevisionLimitError after junior_calls=3, pm_calls=2 — |
| SIM-04 | Partner rejection 46.4% — no recovery path | CONFIRMED | Raised PipelineError after partner called 1 time(s) — Partne |
| SIM-05..14 | PII (IBAN, special chars) bypass sanitize_pii | CONFIRMED | 2 PII types bypass hook |
| SIM-16 | persist_artifact before extract_citations — silent data loss | REFUTED/INCONCLUSIVE | SIM-16 REFUTED: both artifact and citations_index written |
| SIM-17 | PIPELINE_ERROR unreachable via transition() | CONFIRMED (intentional bypass) | reachable_via_transition=False, in_TERMINAL_STATUSES=True. S |
| SIM-schema | Schema validation gaps (RiskItem, FinalDeliverable, EvidenceItem) | CONFIRMED | 5 gaps confirmed: E5.1-zero_risk, E5.5-empty_findings, E5.6-likelihood=6 |

---

*Empirical suite: test_empirical_hooks.py | test_empirical_orchestrator.py | test_empirical_state_machine.py | test_empirical_schemas.py*
*All tests use real code with mocked LLM calls. No Anthropic API calls made.*
