# Codex Reviewer Contract
# origin: codex-core

## Scope
Codex reviewer owns review output and final sign-off in COMBINED mode.

## Required Output Envelope
```yaml
run_id: string
agent: codex-reviewer
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
verdict: APPROVED|CONDITIONS|REJECTED
ak_decision_required: true|false
findings: []
codex_metrics:
  verdict: APPROVED|CONDITIONS|REJECTED
  findings_count: number
  s0_count: number
  s1_count: number
  s2_count: number
  creator_fixes_applied: number
  review_cycle: number
```

## Finding Format
```text
ID: {CDX}-{sprint}-{seq}
Severity: S0|S1|S2
Origin: codex-core
Location: file:line | n/a
Finding: <one sentence>
Scope reviewed: <one sentence>
Blocking?: YES|AK_DECISION|NO
Recommended fix: <one sentence>
```

## Severity Policy
- S0: Merge BLOCKED. Architect + AK required.
- S1: AK_DECISION required before merge.
- S2: May defer with logged rationale.

## Validation Rules
- Missing envelope field -> BLOCKED + `SCHEMA_VIOLATION`.
- Missing required extra field -> BLOCKED + `MISSING_EXTRA_FIELD`.
- Missing packet artifact from intake spec -> BLOCKED + `MISSING_INPUT`.
- `origin` must be `codex-core`.

## Artifacts
- Write: sprint-review.md (path resolved from project CLAUDE.md)
- Append audit entry: [AUDIT_LOG_PATH]
