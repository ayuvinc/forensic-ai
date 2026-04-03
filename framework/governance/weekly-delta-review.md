# Weekly Framework Delta Review
# AK Cognitive OS — Governance
# Date: 2026-03-18

---

## Cadence

Every 7 days (or after 3+ sessions, whichever comes first):
1. Architect reads `framework-improvements.md` — all entries since last review
2. Architect reads `framework/governance/metrics-tracker.md` — trend in blocker_rate and rework_pct
3. Architect proposes framework changes (max 3 per review — avoid churn)
4. AK approves/defers
5. Changes implemented by Junior Dev or Codex depending on stack
6. `framework/interop/interop-contract-v1.md` version bumped if contract changes

---

## Review Template

```
## Weekly Delta Review — YYYY-MM-DD
reviewed_by: Architect
sessions_covered: N-N
framework_improvements_entries: N

### Patterns identified
1. [pattern + frequency]
2.

### Proposed changes (max 3)
1. Change: [what]
   Affects: claude-core | codex-core | interop | both
   Priority: HIGH | MEDIUM | LOW
   Approved by AK: yes | deferred

### Contract version change needed?
yes | no
If yes: bump from X.Y.Z to X.Y+1.Z (MINOR) or X+1.0.0 (MAJOR)

### Metrics trend
blocker_rate: improving | stable | degrading
rework_pct: improving | stable | degrading
escaped_defects: 0 | N (detail)
```

---

## Review Log

<!-- Architect appends one entry per weekly review -->
