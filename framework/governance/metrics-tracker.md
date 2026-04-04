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

## Session 001 — 2026-03-29
mode: SOLO_CLAUDE
sprint_ids: [sprint-01]
tasks_completed: 18

### claude-core
blocker_rate: 0/1 runs
rework_pct: 0%

### codex-core
verdicts: N/A (SOLO_CLAUDE mode)

### combined
escaped_defects: 0
lane_parallelism: no

### notes
Phase 1 foundation built in one pass. 18 files: config, schemas, core, hooks, tool_registry, agent_base, orchestrator, research tools, file_tools. No blockers.

---

## Session 002 — 2026-03-29
mode: SOLO_CLAUDE
sprint_ids: [sprint-02]
tasks_completed: 52

### claude-core
blocker_rate: 0/1 runs
rework_pct: 8% (4 inline fixes applied during QA)

### codex-core
verdicts: N/A (SOLO_CLAUDE mode)

### combined
escaped_defects: 1 (BUG-01: ToolRegistry.call() name→tool_name, found in QR-05)
lane_parallelism: no

### notes
Phases 2–6 built: ~49 modules (agents, workflows, personas, UI, run.py). 4 inline fixes during QA pass. BUG-01 found and fixed in same session. External Codex review yielded C-01..C-07 findings.

---

## Session 003 — 2026-03-29
mode: SOLO_CLAUDE
sprint_ids: [sprint-02 QA gate]
tasks_completed: 15

### claude-core
blocker_rate: 0/1 runs
rework_pct: 0%

### codex-core
verdicts: N/A (SOLO_CLAUDE mode)

### combined
escaped_defects: 0
lane_parallelism: no

### notes
QR-01..15 all PASS. Static analysis + structural validation. BUG-01 fix applied in QR-05. C-01..C-07 documented in todo.md. No new code — QA-only session.

---

## Session 004 — 2026-04-02
mode: SOLO_CLAUDE
sprint_ids: [sprint-03 C-03 remediation]
tasks_completed: 7

### claude-core
blocker_rate: 0/1 runs
rework_pct: 0%

### codex-core
verdicts: N/A (SOLO_CLAUDE mode)

### combined
escaped_defects: 0
lane_parallelism: no

### notes
C-03 evidence chain enforcement moved from prompt-instruction to runtime code. QR-16 added: 7/7 sub-checks PASS. F-EXT-01/02/03 partial fixes for C-02/C-04/C-05. 4 files modified.

---

## Session 005 — 2026-04-04
mode: SOLO_CLAUDE
sprint_ids: [sprint-04 P0]
tasks_completed: 9

### claude-core
blocker_rate: 1/3 runs (architect ran once with version misidentification — 1 pass discarded)
rework_pct: 33% (1 of 3 architect passes discarded due to v1.2 vs v2.0 confusion)

### codex-core
verdicts: N/A (SOLO_CLAUDE mode)

### combined
escaped_defects: 0
lane_parallelism: no

### notes
AK-CogOS v2.0 P0 remediation. 9 artifacts created/updated. Key lesson: clarify remediation target version before architect runs — wrong version caused one full design pass to be discarded. P1-P3 tasks explicitly deferred by AK.

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
