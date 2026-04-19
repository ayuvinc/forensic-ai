# CODEX REVIEW — GoodWork Forensic Consulting Framework

## Review Status
- Last review cycle: Sprint-03 (2026-03-29)
- All sprint-01 and sprint-02 findings: RESOLVED
- Sprint-03 external findings: RESOLVED
- Sprint-03 Codex findings C-01..C-07: LOGGED TO TASKS (pending implementation)

## Framework State for Next Review

### What Has Been Verified
- 57 modules import cleanly
- All Pydantic schemas validate correctly (QR-02)
- State machine transitions are correct (QR-03)
- Hook chain end-to-end: veto, PII, metadata, artifact, audit, markdown (QR-04)
- Tool registry enforcement: ToolNotAllowedError, ToolNotFoundError (QR-05)
- Orchestrator happy path and revision loop (QR-06, QR-07)
- Orchestrator resume via load_envelope() (QR-08)
- Research tool trust enforcement: domain filter, authoritative marking (QR-09)
- File tools atomicity and envelope wrapping (QR-10)
- Code quality: no bare excepts, no star imports (QR-11)
- Security: PII redaction, web tool truncation, doc tool pass-through (QR-12)
- FRM workflow: 8 modules, dependency enforcement, RiskItem extraction (QR-13)
- DocumentManager bounded retrieval: read_excerpt ≤8k, read_pages ≤60k (QR-14)
- Evidence classifier: LEAD_ONLY, FindingChain validation (QR-15)

## Open Issues for Next Review Cycle (from tasks/todo.md)

**C-03 — HIGHEST PRIORITY: Evidence-chain enforcement**
EvidenceClassifier.validate_finding_chain() exists but is never called in the partner agent
path at runtime. Evidence permissibility is currently prompt-enforced only.
Files to check: agents/partner/agent.py, tools/evidence/evidence_classifier.py

**C-01 — Workflow quality split**
investigation_report and frm_risk_register use the full orchestrated pipeline.
policy_sop, training_material, client_proposal, proposal_deck are single-model generators.
Decision needed: classify as Mode B explicitly, or upgrade to orchestrated path.
Files to check: workflows/policy_sop.py, training_material.py, client_proposal.py, proposal_deck.py

**C-02 — Mode B state persistence**
Mode B workflows do not update state.json to a terminal status after completion.
Case tracker shows these cases as INTAKE_CREATED even when deliverable is written.
Files to check: workflows/client_proposal.py, policy_sop.py, training_material.py, proposal_deck.py

**C-04 — Document ingestion UI**
DocumentManager is wired into investigation and FRM workflows but there is no UI entry point
for a consultant to actually ingest documents into a case folder from the menu.
Files to check: run.py, ui/guided_intake.py, tools/document_manager.py

**PQA — Proposal + PPT QA gate not yet run**
Client proposal (Option 7) and PPT prompt pack (Option 8) were never QA-tested.
12 acceptance criteria defined in tasks/todo.md (PQA-01..12).

**PGP — Pricing gap**
If consultant skips firm profile setup, proposal generates fee section with blank rates silently.
Fix defined in tasks/todo.md (PGP-01, PGP-02).

## Instructions for Next Codex Review

Read this file and tasks/todo.md before starting.
Focus review on:
1. C-03: verify whether validate_finding_chain() is now called in partner approval path
2. C-01: verify the mode classification decision was made and applied consistently
3. C-02: verify state.json is updated to terminal status after Mode B workflows complete
4. PQA: verify proposal and PPT pack work end-to-end
5. Any regressions from sprint-03 changes to run.py, investigation_report.py, frm_risk_register.py

Smoke test is still pending (requires API keys in .env).
