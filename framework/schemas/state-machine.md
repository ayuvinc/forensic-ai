# Session State Machine

validation: markdown-contract-only | machine-validated

---

## Purpose

Defines the lifecycle states and legal transitions for session management in AK Cognitive OS.
All skills that read or write SESSION STATE must conform to this contract.

---

## States

| State | Meaning |
|-------|---------|
| `CLOSED` | No active session. Safe to open a new session. |
| `OPEN` | Session in progress. Work is being done. |

There are exactly two states. No other values are valid.

---

## Transitions

| From | To | Triggered by | Precondition |
|------|----|-------------|--------------|
| `CLOSED` | `OPEN` | `/session-open` | Status == CLOSED |
| `OPEN` | `CLOSED` | `/session-close` | Status == OPEN |

No other transitions are valid. Self-transitions (OPEN→OPEN, CLOSED→CLOSED) are illegal.

---

## Single Source of Truth

SESSION STATE lives in **`tasks/todo.md`** only. The canonical block format is:

```
## SESSION STATE

Status:         CLOSED
Active task:    none
Active persona: none
Blocking issue: none
Last updated:   —
```

CLAUDE.md may reference SESSION STATE but must NOT contain a duplicate copy. Instead use:

```
Session state lives in `tasks/todo.md`. All personas read it there.
```

---

## Rules

1. `/session-open` MUST check `Status == CLOSED` before proceeding. If Status != CLOSED, emit `status: BLOCKED` with `SESSION_STATE_VIOLATION`.
2. `/session-open` MUST write `Status: OPEN` to `tasks/todo.md` after validation passes.
3. `/session-close` MUST check `Status == OPEN` before proceeding. If Status != OPEN, emit `status: BLOCKED` with `SESSION_STATE_VIOLATION`.
4. `/session-close` MUST write `Status: CLOSED` to `tasks/todo.md` as final step.
5. Both skills MUST validate the write succeeded by re-reading the state after writing.
6. No other skill or persona may write to the SESSION STATE block.

---

## Validation Checks (for validate-framework.sh)

- `session-open/claude-command.md` must contain the string `CLOSED` in a check/precondition context (expects CLOSED to open).
- `session-close/claude-command.md` must contain the string `OPEN` in a check/precondition context (expects OPEN to close).
- `session-open/claude-command.md` must NOT require `Status == OPEN` as a precondition (this was the v1.0-v1.1 bug).
- `session-close/claude-command.md` must write `Status=CLOSED` (already correct in v1.1).

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| `/session-open` finds `Status: OPEN` | BLOCKED — session already running. Close it first. |
| `/session-close` finds `Status: CLOSED` | BLOCKED — no session to close. Open one first. |
| SESSION STATE block missing from `tasks/todo.md` | BLOCKED — `MISSING_SESSION_STATE`. Run remediation. |
| SESSION STATE has invalid value (not OPEN or CLOSED) | BLOCKED — `INVALID_SESSION_STATE`. Manual fix required. |
