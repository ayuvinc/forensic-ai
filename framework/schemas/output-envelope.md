# Output Envelope Schema
# AK Cognitive OS — Universal Agent Contract
# validation: markdown-contract-only | machine-validated

---

## Purpose

Every agent output from any persona or skill must match this envelope.
This is the single canonical contract — both Claude-core and Codex-core obey it.

---

## Required Output Envelope

```yaml
run_id: string           # {agent}-{session_id}-{sprint_id}-{timestamp_utc}
agent: string            # exact agent/persona name
origin: claude-core | codex-core | combined
status: PASS | FAIL | BLOCKED
timestamp_utc: ISO-8601
summary: string          # one sentence, human-readable
failures: []             # array of strings, empty if PASS
warnings: []             # non-blocking, array of strings
artifacts_written: []    # array of file paths
next_action: string      # one sentence
```

---

## Strict Validation Rules

- Missing any envelope field → BLOCKED with `SCHEMA_VIOLATION: {field}`
- `status` not in [PASS, FAIL, BLOCKED] → BLOCKED with `SCHEMA_VIOLATION: status`
- `origin` not in [claude-core, codex-core, combined] → BLOCKED with `SCHEMA_VIOLATION: origin`
- `timestamp_utc` not valid ISO-8601 → BLOCKED with `SCHEMA_VIOLATION: timestamp_utc`
- `run_id` already present in [AUDIT_LOG_PATH] → BLOCKED with `DUPLICATE_RUN_ID`
- If any required `extra_fields` field is missing → BLOCKED with `MISSING_EXTRA_FIELD`
- If any required input/artifact is missing → BLOCKED with `MISSING_INPUT`
- No silent pass on partial output

---

## Status Contract

| Status | Meaning | Can continue? |
|---|---|---|
| PASS | All checks passed, outputs written | Yes |
| FAIL | Checks ran, found failures, outputs written | No — fix required |
| BLOCKED | Could not safely start or complete | No — precondition missing |

FAIL vs BLOCKED distinction:
- FAIL: I ran and found problems (checks ran, failures documented)
- BLOCKED: I could not run because something required was missing or invalid

---

## Blocked Rule

Any missing required input or artifact must stop execution and return BLOCKED
with the exact list of missing items. Never return partial success.

---

## Origin Values

| Origin | When to use |
|---|---|
| claude-core | Output produced entirely by Claude |
| codex-core | Output produced entirely by Codex |
| combined | Output produced jointly (e.g. merged sprint artifacts) |

Never use `combined` in degraded single-stack mode.

---

## Extra Fields Convention

Each persona/skill defines its own `extra_fields` beyond this envelope.
See individual persona schema.md files for required extra fields.
Missing extra field → BLOCKED with `MISSING_EXTRA_FIELD: {field_name}`

---

## Contract Version

Referenced from: interop/interop-contract-v1.md
Current version: 1.0.0
