# Interop Contract — v1
# AK Cognitive OS
# Date: 2026-03-18
# Version: 1.0.0

---

## Purpose

This is the single canonical interface specification that both claude-core and codex-core
must obey. Any output produced by either stack must be consumable by the other without
translation errors.

---

## Required Output Envelope

Every agent output, review output, and creator output from EITHER stack must match:

```yaml
run_id: string           # {agent|codex}-{session_id}-{sprint_id}-{timestamp_utc}
agent: string            # exact agent/role name
origin: claude-core | codex-core | combined
status: PASS | FAIL | BLOCKED
timestamp_utc: ISO-8601
summary: string          # one sentence, human-readable
failures: []             # array of strings, empty if PASS
warnings: []             # non-blocking, array of strings
artifacts_written: []    # array of file paths
next_action: string      # one sentence
```

### Validation rules (both stacks enforce)
- Missing any envelope field → BLOCKED with `SCHEMA_VIOLATION: {field}`
- `status` not in [PASS, FAIL, BLOCKED] → BLOCKED with `SCHEMA_VIOLATION: status`
- `origin` not in [claude-core, codex-core, combined] → BLOCKED with `SCHEMA_VIOLATION: origin`
- `timestamp_utc` not valid ISO-8601 → BLOCKED with `SCHEMA_VIOLATION: timestamp_utc`
- `run_id` already present in [AUDIT_LOG_PATH] → BLOCKED with `DUPLICATE_RUN_ID`

---

## Status Contract

| Status | Meaning | Can continue? |
|---|---|---|
| PASS | All checks passed, outputs written | Yes |
| FAIL | Checks ran, found failures, outputs written | No — fix required |
| BLOCKED | Could not safely start or complete | No — precondition missing |

FAIL vs BLOCKED distinction:
- FAIL: I ran and found problems (tests failed, criteria unmet)
- BLOCKED: I could not run because something required was missing/invalid

---

## Severity Contract (Codex findings + Claude findings)

| Severity | Meaning | Merge policy | Who resolves |
|---|---|---|---|
| S0 | Critical — correct or the system is broken | Merge BLOCKED, no exceptions | Architect + AK |
| S1 | Significant — must be resolved or explicitly accepted | AK_DECISION required | AK decides |
| S2 | Advisory — improvement, not required | Log rationale, may defer | Builder decides |

Both stacks must use S0/S1/S2. No other severity levels.

---

## Finding Format (both stacks)

Any finding produced by either stack:

```
ID:              {STACK}-{NNN}-{seq}   # e.g. RVW-001-01 or CLD-001-01
Severity:        S0 | S1 | S2
Origin:          claude-core | codex-core
Location:        file:line (if applicable, else "n/a")
Finding:         One sentence describing the issue
Scope reviewed:  What was actually examined
Blocking?:       YES (S0) | AK_DECISION (S1) | NO (S2)
Recommended fix: One sentence
```

---

## Audit Entry Format (both stacks)

Every agent and Codex action appends one entry to [AUDIT_LOG_PATH]:

```
[YYYY-MM-DD HH:MM UTC] | {event_type} | run_id={run_id} | origin={origin} | actor={actor} | task={task_id} | {summary} | artifact={path|none}
```

Rules:
- Append-only. Never edit prior entries.
- `entry_id` = `run_id` — must be unique.
- `event_type` must be from the exhaustive list in `schemas/audit-log-schema.md`.
- `origin` field mandatory on every entry.

---

## Path Contract

Both stacks resolve paths via project `CLAUDE.md` overrides before using defaults.

Default paths:
```
todo:                   tasks/todo.md
lessons:                tasks/lessons.md
next_action:            tasks/next-action.md
risk_register:          tasks/risk-register.md
ba_logic:               tasks/ba-logic.md
ux_specs:               tasks/ux-specs.md
channel:                channel.md
audit_log:              [AUDIT_LOG_PATH]
framework_improvements: framework-improvements.md
sprint_reviews:         [SPRINT_REVIEWS_PATH]
regression_artifacts:   [REGRESSION_ARTIFACTS_PATH]
```

---

## Compatibility Tests

Before any stack update, run these checks to verify interop:

### Test 1 — Envelope compatibility
```
Given: any agent/codex output
Check: parse as required_output_envelope
Pass if: all fields present, correct types, origin set
Fail if: any field missing or wrong type
```

### Test 2 — Status consumption
```
Given: status field from either stack
Check: consuming stack reads PASS|FAIL|BLOCKED correctly
Pass if: no translation step needed
Fail if: consuming stack requires mapping or transformation
```

### Test 3 — Finding consumption
```
Given: finding from either stack
Check: consuming stack reads ID, Severity, Origin, Finding, Blocking?
Pass if: fields present and parseable without transformation
Fail if: any field requires translation
```

### Test 4 — Audit entry consumption
```
Given: audit entry from either stack
Check: [AUDIT_LOG_PATH] can be read by either stack's log reader
Pass if: entry format identical regardless of origin
Fail if: entries require stack-specific parsing
```

### Test 5 — Severity policy agreement
```
Given: S0 finding from either stack
Check: consuming stack treats it as merge-blocking
Pass if: merge is blocked regardless of which stack produced S0
Fail if: severity interpretation differs by stack
```

---

## Contract Versioning

- Current version: 1.0.0
- Version format: MAJOR.MINOR.PATCH
- MAJOR: breaking change to envelope or status contract
- MINOR: new optional fields, new event types
- PATCH: clarifications, no structural change
- Both stacks must update when MAJOR or MINOR bumps
- Version referenced in every agent's schema validation
