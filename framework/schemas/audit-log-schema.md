# Audit Log Schema (Append-Only)
# AK Cognitive OS
# validation: markdown-contract-only | machine-validated

---

## File

Resolved at runtime from project `CLAUDE.md` override.
Reference as: `[AUDIT_LOG_PATH]`
Default path is set in your project `CLAUDE.md` under `audit_log:` override.

---

## Entry Format

```yaml
entry_id: "{agent}-{session_id}-{sprint_id}-{timestamp_utc}"
timestamp_utc: "<ISO-8601>"
actor: "<agent|persona>"
event_type: "<event>"
origin: "claude-core | codex-core | combined"
status: "PASS|FAIL|BLOCKED"
artifacts: []
summary: "<short text>"
```

Inline format (one-line):
```
[YYYY-MM-DD HH:MM UTC] | {event_type} | run_id={run_id} | origin={origin} | actor={actor} | task={task_id} | {summary} | artifact={path|none}
```

---

## Enforcement

- Append-only. Previous entries are immutable. Never edit prior entries.
- `entry_id` must be unique across the entire log.
- Missing required field blocks write.
- `event_type` must be from the exhaustive list below. No invented types.
- `origin` field mandatory on every entry.

---

## EVENT_TYPE Exhaustive List

```
SESSION_OPENED
SESSION_CLOSED
SESSION_CLOSE_ATTEMPT      # include: BLOCKED reason if applicable
TASK_CREATED
TASK_STATUS_CHANGED        # include: old_status -> new_status in summary
PERSONA_ACTIVATED
ARCHITECTURE_COMPLETE      # after architect writes task plan
BUILD_COMPLETE             # after junior-dev completes sprint work
SPRINT_PACKAGED            # after sprint-packager runs
REGRESSION_GUARD_PASSED
REGRESSION_GUARD_BLOCKED
REGRESSION_GUARD_SKIPPED   # retrospective sprint — no code changes
CODEX_INTAKE_PASSED
CODEX_INTAKE_BLOCKED
CODEX_VERDICT              # include: APPROVED|CONDITIONS|REJECTED in summary
CODEX_CREATOR_FIX          # one entry per finding fixed
VERDICT_DISPOSITION        # AK disposes Codex findings
QA_APPROVED
QA_REJECTED
AK_DECISION                # include: decision summary
BOUNDARY_FLAG_OPENED
BOUNDARY_FLAG_RESOLVED
LESSONS_ADDED
FRAMEWORK_DELTA_LOGGED
SECURITY_SWEEP_PASSED
SECURITY_SWEEP_BLOCKED
HANDOFF_VALIDATED
HANDOFF_BLOCKED
PRE_COMPACT_CHECKPOINT     # fired by pre-compact hook before context compression
FRAMEWORK_GAP_IDENTIFIED   # new gap found during re-run
COMPLIANCE_S0_BLOCKED      # compliance gate hard block
COMPLIANCE_S1_DECISION     # AK decision required on compliance finding
```

---

## Audit Event → Gate Mapping (Canonical)

| Stage gate | Correct event_type |
|---|---|
| /session-open complete | SESSION_OPENED |
| /architect complete | ARCHITECTURE_COMPLETE |
| /junior-dev complete | BUILD_COMPLETE |
| /regression-guard green | REGRESSION_GUARD_PASSED |
| /regression-guard blocked | REGRESSION_GUARD_BLOCKED |
| /regression-guard skipped (retrospective) | REGRESSION_GUARD_SKIPPED |
| /sprint-packager complete | SPRINT_PACKAGED |
| /codex-intake-check passed | CODEX_INTAKE_PASSED |
| Codex verdict received | CODEX_VERDICT |
| AK disposes findings | VERDICT_DISPOSITION |
| /session-close complete | SESSION_CLOSED |
| Compliance S0 raised | COMPLIANCE_S0_BLOCKED |
| Compliance S1 raised | COMPLIANCE_S1_DECISION |

---

## Adding New Event Types

1. Add to this list first.
2. Update interop/interop-contract-v1.md version number.
3. No agent may emit an event_type not in this list.
