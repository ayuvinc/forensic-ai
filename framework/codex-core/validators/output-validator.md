# Codex Output Validator
# validates codex-core outputs against interop-contract-v1

## Required Envelope Check
Fields required on every output:
- run_id
- agent
- origin (must be codex-core or combined when explicitly merged)
- status (PASS|FAIL|BLOCKED)
- timestamp_utc (ISO-8601)
- summary
- failures[]
- warnings[]
- artifacts_written[]
- next_action

Reject conditions:
- Missing field -> BLOCKED + `SCHEMA_VIOLATION:<field>`
- Invalid status/origin -> BLOCKED + `SCHEMA_VIOLATION:<field>`
- Duplicate run_id in audit log -> BLOCKED + `DUPLICATE_RUN_ID`

## Compatibility Tests
1. Envelope compatibility
- Input: any codex output
- Pass: all envelope fields parse with interop schema

2. Status consumption
- Input: PASS/FAIL/BLOCKED
- Pass: no translation needed by claude-core consumer

3. Finding consumption
- Input: standard finding block
- Pass: ID, Severity, Origin, Blocking?, Recommended fix parse directly

4. Audit entry consumption
- Input: audit line with origin=codex-core
- Pass: claude-core log reader parses without stack-specific logic

5. Severity policy agreement
- Input: S0 finding
- Pass: merge marked BLOCKED consistently

## Test Record Template
```yaml
test_run_id: <string>
timestamp_utc: <ISO-8601>
origin: codex-core
results:
  envelope_compatibility: PASS|FAIL
  status_consumption: PASS|FAIL
  finding_consumption: PASS|FAIL
  audit_entry_consumption: PASS|FAIL
  severity_policy_agreement: PASS|FAIL
summary: <one line>
next_action: <one line>
```
