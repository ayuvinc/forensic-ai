# Framework Quality Metrics Tracker
# AK Cognitive OS — Governance
# Date: 2026-03-18
# Updated by: /framework-delta-log at every session close

---

## Metric Definitions

| Metric | Formula | Source |
|---|---|---|
| cycle_time | QA_APPROVED timestamp − TASK_CREATED timestamp | [AUDIT_LOG_PATH] |
| blocker_rate | BLOCKED events ÷ total agent runs | [AUDIT_LOG_PATH] |
| escaped_defects | bugs found post-QA_APPROVED | risk-register.md |
| rework_pct | tasks with >1 Codex review cycle ÷ total tasks | sprint review files |
| codex_verdict_dist | count(APPROVED) / count(CONDITIONS) / count(REJECTED) | sprint review files |
| lane_parallelism | sessions with parallel lanes ÷ total sessions | session notes |

Track all metrics per: `claude-core`, `codex-core`, `combined`.

---

## Session Log

<!-- /framework-delta-log appends a new entry here at every session close -->

### Template (one entry per session)
```
## Session N — YYYY-MM-DD
mode: COMBINED | SOLO_CLAUDE | SOLO_CODEX
sprint_ids: []
tasks_completed: N
cycle_time_avg_min: N

### claude-core
blocker_rate: N/N runs
rework_pct: N%

### codex-core
verdicts: APPROVED=N CONDITIONS=N REJECTED=N
rework_pct: N%

### combined
escaped_defects: N
lane_parallelism: yes|no

### notes
[any anomalies or framework observations]
```
