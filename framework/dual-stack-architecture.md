# Dual-Stack Architecture
# AK Cognitive OS — v1
# Date: 2026-03-18

---

## Principle

Claude and Codex are independently capable. Together they are disproportionately better.
1 + 1 = 11, not 2.

Neither stack depends on the other to function. Both stacks speak the same interop contract.
In COMBINED mode, ownership is disjoint per phase — no duplication, no gaps.

---

## Stack Ownership

```
claude-core/                          codex-core/
─────────────────────────────────     ────────────────────────────────
Owner: Claude Code                    Owner: Codex (separate session)

Commands:  skills/ and personas/      Contracts: codex-core/reviewer-contract.md
Schemas:   schemas/                             codex-core/creator-contract.md
Templates: framework/templates/       Runbooks:  codex-core/runbooks/
                                      Validators: codex-core/validators/
```

### Claude-core owns
- All personas in `personas/` and skills in `skills/`
- `schemas/` — output-envelope, audit-log-schema, finding-schema, persona-schema, skill-schema
- `framework/templates/` — all 5 templates
- Session lifecycle: `/session-open`, `/session-close`
- Quality gates: `/regression-guard`, `/qa-run`, `/handoff-validator`
- Knowledge capture: `/audit-log`, `/lessons-extractor`, `/framework-delta-log`
- Core personas: `/architect`, `/ba`, `/ux`, `/junior-dev`, `/qa`
- Extended personas: `/researcher`, `/compliance`

### Codex-core owns
- `framework/codex-core/reviewer-contract.md` — Codex review spec
- `framework/codex-core/creator-contract.md` — Codex Creator mode spec
- `framework/codex-core/intake-spec.md` — what Codex requires before reviewing
- `framework/codex-core/runbooks/reviewer-runbook.md` — how Codex reviews
- `framework/codex-core/runbooks/creator-runbook.md` — how Codex implements fixes
- `framework/codex-core/validators/output-validator.md` — how Codex validates its own output

### Shared (interop layer)
- `framework/interop/interop-contract-v1.md` — canonical interface both stacks obey
- `framework/interop/combined-mode-runbook.md` — COMBINED mode execution
- `framework/interop/failover-policy.md` — mutual fallback rules
- `framework/governance/` — metrics, weekly delta review

---

## Execution Modes

### SOLO_CLAUDE
```
When: Codex unavailable | hotfix | simple task | AK conscious decision
Who:  Claude handles all phases
Flow: Plan → Build → /regression-guard → /qa-run → /session-close
Sign-off: Architect code review + QA_APPROVED from /qa-run
Audit label: origin: claude-core
```

### SOLO_CODEX
```
When: Code already written externally | targeted review only | AK conscious decision
Who:  Codex handles review + optional fix phases
Flow: Codex reads packet → reviews → Creator mode if needed → signs off
Sign-off: Codex APPROVED verdict
Audit label: origin: codex-core
```

### COMBINED (default, full framework)
```
When: Standard feature, bug fix, or refactor session
Ownership per phase — strictly disjoint:

  PHASE          OWNER         TOOL/PERSONA
  ─────────────────────────────────────────────────────
  Plan           Claude        /architect
  Criteria       Claude        /qa (pre-build)
  Security gate  Claude        /security-sweep
  Build          Claude        /junior-dev
  Regression     Claude        /regression-guard
  Package        Claude        /sprint-packager + /review-packet
  Intake gate    Claude        /codex-intake-check
  Review         Codex         Reviewer mode
  Fix (if S1/S2) Codex         Creator mode (if AK authorises)
  Re-regression  Claude        /regression-guard (mandatory re-entry)
  QA validate    Claude        /qa-run
  Code review    Claude        /architect
  UX review      Claude        /ux
  Sign-off       Codex         APPROVED verdict required
  Close          Claude        /session-close + /audit-log
  ─────────────────────────────────────────────────────
  Audit label: origin: combined
```

---

## Phase Ownership Map (COMBINED)

```
AK ──► Claude ──────────────────────────────────────────────►
            │ Plan+Build+Gate         Codex ──────────────►
            │                         │ Review+Sign-off
            ◄─────────────────────────┘
            │ QA+Close
            ▼
         SESSION CLOSED
```

No phase has two owners. If a phase is ambiguous, Claude owns it.
Codex's phases: Review, Creator fix (if authorised), Final sign-off.
All other phases: Claude.

---

## Parallel Execution Lanes (Joint Power)

When tasks are independent (no shared files, no shared types), run in parallel:

```
LANE A (Claude)          LANE B (Claude)
────────────────         ────────────────
Task A-01                Task B-01
Build → Regress          Build → Regress
        │                        │
        └──────────┬─────────────┘
                   ▼
          MERGE COORDINATOR
          /sprint-packager collects both lanes
          Single review packet → Codex reviews all
          Conflict resolution if needed
                   │
                   ▼
          Codex review (COMBINED mode)
```

### Merge coordinator rules
- `/sprint-packager` waits for ALL lanes to reach GREEN before packaging
- If any lane is BLOCKED, the blocked lane is listed as `lane_status: BLOCKED`
- Codex reviews the combined packet — all tasks in one sprint
- Codex findings reference task_id — no cross-task confusion

---

## Conflict Resolution Policy

When Claude and Codex produce contradictory findings on the same artifact:

| Conflict type | Resolution |
|---|---|
| Test pass (Claude) vs structural flaw (Codex) | Codex wins — tests passing ≠ correct design |
| Security finding (Claude) vs security finding (Codex, different severity) | Higher severity wins |
| Codex APPROVED vs AK disagrees | AK wins — AK_DECISION logged |
| Codex REJECTED vs Claude architecture review PASS | Codex wins — Codex has fresh eyes |
| Both BLOCKED on different reasons | Both reasons logged, Architect resolves |
| S0 from either stack | Always blocks merge — no override |

All conflicts logged to [AUDIT_LOG_PATH] with event_type: AK_DECISION or BOUNDARY_FLAG_OPENED.

---

## Quality Metrics (tracked per stack and combined)

Metrics written to `framework/governance/metrics-tracker.md` at each session close.

| Metric | Definition | Source |
|---|---|---|
| cycle_time | TASK_CREATED → QA_APPROVED (minutes) | [AUDIT_LOG_PATH] |
| blocker_rate | BLOCKED events / total agent runs | [AUDIT_LOG_PATH] |
| escaped_defects | Bugs found after QA_APPROVED | manual, risk-register.md |
| rework_pct | Tasks with >1 Codex review cycle | sprint review files |
| codex_verdict_dist | % APPROVED / CONDITIONS / REJECTED | sprint review files |
| lane_parallelism | % sessions with parallel lanes | session notes |

Track per: `origin: claude-core`, `origin: codex-core`, `origin: combined`.

---

## Governance

### Audit labels
Every [AUDIT_LOG_PATH] entry must include `origin` field:
```
origin: claude-core | codex-core | combined
```

### Weekly framework-delta review
- Agent: `/framework-delta-log` runs at every session close
- Output: `framework-improvements.md`
- Weekly: Architect reviews improvements, proposes framework changes
- Changes: version-bumped in `framework/interop/interop-contract-v1.md`
- Both stacks must update when contract version changes

---

## File Map

```
[FRAMEWORK_ROOT]/
├── framework/
│   ├── dual-stack-architecture.md      ← THIS FILE
│   ├── schemas/ (see schemas/ at repo root)
│   ├── templates/
│   │   ├── sprint-summary.md
│   │   ├── sprint-review.md
│   │   ├── audit-entry.md
│   │   ├── task.md
│   │   └── next-action.md
│   ├── codex-core/
│   │   ├── reviewer-contract.md
│   │   ├── creator-contract.md
│   │   ├── intake-spec.md
│   │   ├── runbooks/
│   │   │   ├── reviewer-runbook.md
│   │   │   └── creator-runbook.md
│   │   └── validators/
│   │       └── output-validator.md
│   ├── interop/
│   │   ├── interop-contract-v1.md
│   │   ├── combined-mode-runbook.md
│   │   └── failover-policy.md
│   └── governance/
│       ├── metrics-tracker.md
│       └── weekly-delta-review.md
```
