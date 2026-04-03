# Codex Creator Contract
# origin: codex-core

## Scope
Creator mode is optional and only active when AK declares Reviewer+Creator.

## Required Output Envelope
```yaml
run_id: string
agent: codex-creator
origin: codex-core
status: PASS|FAIL|BLOCKED
timestamp_utc: ISO-8601
summary: string
failures: []
warnings: []
artifacts_written: []
next_action: string
```

## Required Extra Fields
```yaml
mode_gate: Reviewer+Creator
condition_resolution_map: []
attempts: number
blocked_s0_findings: []
```

## Hard Limits
- May fix S1/S2 findings only.
- Must not implement S0 fixes.
- Must not change acceptance criteria.
- Must not refactor outside explicit finding scope.

## Re-entry Sequence (mandatory)
1. `/regression-guard`
2. `/review-packet`
3. `/codex-intake-check`
4. Re-review (delta)

## Escalation
- If unresolved after 2 attempts -> emit `ESCALATION_FLAG` and BLOCKED.
- Any S0 present -> BLOCKED + escalation.

## Artifacts
- Write: sprint-delta.md (path resolved from project CLAUDE.md)
- Append audit entry: [AUDIT_LOG_PATH]
