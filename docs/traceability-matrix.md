# Traceability Matrix — GoodWork Forensic AI

> STUB — populate as /ba, /architect, and QA sessions produce outputs.

---

## Format

| Task ID | Scope Item | HLD Reference | LLD Reference | Test / QR Check |
|---------|------------|---------------|---------------|-----------------|

---

## Populated Entries

| Task ID | Scope Item | HLD Reference | LLD Reference | Test / QR Check |
|---------|------------|---------------|---------------|-----------------|
| P1-05 | State machine transitions | hld.md#state-machine | — | QR-03 PASS |
| P1-06/07 | Hook chain (pre + post) | hld.md#hook-chain | — | QR-04 PASS |
| P1-08 | Tool registry dispatch | hld.md#key-integrations | — | QR-05 PASS |
| P1-09 | Agent base guardrails | hld.md#agent-pipeline | — | QR-01 PASS (import) |
| P1-10 | Orchestrator pipeline + resume | hld.md#agent-pipeline | — | QR-06, QR-07, QR-08 PASS |
| P1-11..14 | Research tools (4) | hld.md#key-integrations | — | QR-09 PASS |
| P1-15 | File tools atomicity | hld.md#file-conventions | — | QR-10 PASS |
| P2-02..04 | Three-agent pipeline | hld.md#agent-pipeline | — | QR-01 PASS (structural) |
| P3-01 | FRM Risk Register workflow | hld.md#agent-pipeline | — | QR-13 PASS |
| C-03a/b/c | Evidence chain enforcement | hld.md#hook-chain | — | QR-16 PASS (7/7) |

## Gaps
<!-- Tasks without traceability to scope, HLD, or tests — flag for /ba or /architect session -->

- All workflows (P4-01..09): scope item not yet defined in scope-brief.md
- All personas (P5-01..04): scope item not yet defined
- UI layer (P5-05): UX spec stub only; no traceability to confirmed requirements
- C-04 (document ingestion): coded but not mapped to any scope item
- C-06a–e (integration tests): not yet written; matrix will be populated when tests are added
