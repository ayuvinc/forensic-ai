# Codex Reviewer Runbook

## Mode
- COMBINED: default
- SOLO_CODEX: degraded failover only

## Steps (COMBINED)
1. Validate intake against `framework/codex-core/intake-spec.md`.
2. Review sprint summary, changed files, criteria map, UX constraints, security notes.
3. Produce findings using standard format (S0/S1/S2).
4. Emit verdict: APPROVED|CONDITIONS|REJECTED.
5. Set `ak_decision_required=true` if any S1.
6. Write sprint-review.md (path from project CLAUDE.md).
7. Append audit entry with `origin=codex-core`.

## Steps (SOLO_CODEX degraded)
1. Build manual sprint summary from available context.
2. Mark test state as `MANUAL_REQUIRED`.
3. Produce review verdict with findings.
4. Write tasks/next-action.md scaffold.
5. Append audit entry with `origin=codex-core`.

## Output Guardrails
- Always emit required envelope.
- Always include `codex_metrics` block.
- Never downgrade S0.
