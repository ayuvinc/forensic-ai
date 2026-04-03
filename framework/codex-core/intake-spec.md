# Codex Intake Spec
# gate: /codex-intake-check

## Required Inputs Before Review
1. sprint-summary.md (path from project CLAUDE.md)
2. Changed-files manifest
3. Acceptance criteria map (1:1 with task IDs)
4. Regression evidence (test suite + build + lint — commands from project CLAUDE.md)
5. tasks/ux-specs.md reference if UI changed
6. Architecture constraints for type/API changes
7. Security sign-off evidence

## Intake Result Contract
```yaml
run_id: string
agent: codex-intake-check
origin: codex-core
status: PASS|FAIL|BLOCKED
timestamp_utc: ISO-8601
summary: string
failures: []
warnings: []
artifacts_written: []
next_action: string
extra_fields:
  codex_ready: true|false
  missing_items: []
```

## Rules
- If any required item is missing, return BLOCKED with exact `missing_items` list.
- No partial intake pass.
- Append one audit entry per intake attempt.
