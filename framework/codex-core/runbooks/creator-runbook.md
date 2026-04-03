# Codex Creator Runbook

## Preconditions
- AK mode explicitly set to Reviewer+Creator.
- Findings list provided.
- No unresolved S0 in creator scope.

## Steps
1. Validate creator mode gate.
2. Map each S1/S2 condition to concrete code/test change.
3. Apply minimal-scope fixes.
4. Write sprint-delta.md (path from project CLAUDE.md) with condition_resolution_map.
5. Trigger mandatory re-entry sequence:
   - /regression-guard
   - /review-packet
   - /codex-intake-check
   - Codex re-review
6. Append audit entry.

## Failure Handling
- Missing input -> BLOCKED + `MISSING_INPUT`.
- Scope creep required -> BLOCKED + `BOUNDARY_FLAG`.
- >2 attempts -> BLOCKED + `ESCALATION_FLAG`.
