# Stage Gates — AK Cognitive OS v3.0
# Enforcement rules for each stage transition in the delivery lifecycle
# Owner: Architect
# Depends on: framework/governance/delivery-lifecycle.md

---

## Overview

A stage gate is a precondition table — it defines what must be true before work may advance from one stage to the next. Gates are either **HARD** (blocking; work cannot proceed until resolved) or **ADVISORY** (warning; work may proceed but risk is noted). Each gate entry records whether it is enforced mechanically by a hook or validator, or manually by a persona.

Enforcement column legend:
- `MECHANICAL` — enforced by a hook in `scripts/hooks/` or check in `validate-framework.sh`
- `MANUAL` — enforced by persona review; no automated check
- `[TODO: automate]` — gap identified; planned for Workstream 6 (STEP-28+)

Stage names in this document match `framework/governance/delivery-lifecycle.md` exactly.

---

## Mandatory Gate 1 — Pre-Implementation Gate

**Transition:** scope/architecture/design → implementation

**Rule:** Junior Dev may not begin writing code or content until all required planning artifacts are present and accepted.

| Check | Who Checks | Block Type | Enforcement |
|---|---|---|---|
| `docs/problem-definition.md` exists | `/junior-dev` (self-check) | HARD | MANUAL — [TODO: automate via guard-planning-artifacts.sh, STEP-28] |
| `docs/scope-brief.md` exists | `/junior-dev` (self-check) | HARD | MANUAL — [TODO: automate via guard-planning-artifacts.sh, STEP-28] |
| `docs/hld.md` exists | `/junior-dev` (self-check) | HARD | MANUAL — [TODO: automate via guard-planning-artifacts.sh, STEP-28] |
| All PENDING tasks have non-placeholder acceptance criteria | `/junior-dev` (self-check) | HARD | MANUAL |
| `tasks/ux-specs.md` complete (if UI work in scope) | `/junior-dev` (self-check) | HARD | MANUAL |
| No open BOUNDARY_FLAGs in architecture output | `/architect` | HARD | `guard-boundary-flags.sh` (MECHANICAL) |

**Failure action:** `/junior-dev` emits BLOCKED with `PRE_IMPLEMENTATION_GATE_FAILED` and names the missing artifact. Work halts until `/architect` or `/ba` resolves the gap.

---

## Mandatory Gate 2 — Pre-Release Gate

**Transition:** security/compliance → release

**Rule:** No work may be merged to main until QA, security engineering, and compliance have all signed off. The git push is mechanically blocked unless these conditions are satisfied.

| Check | Who Checks | Block Type | Enforcement |
|---|---|---|---|
| All scoped tasks are QA_APPROVED (no QA_REJECTED) | `/architect` | HARD | `guard-git-push.sh` (MECHANICAL — checks for QA_APPROVED in tasks/todo.md) |
| Active persona is Architect | `/architect` | HARD | `guard-git-push.sh` (MECHANICAL — checks ACTIVE_PERSONA env var) |
| Codex review has PASS verdict | `/architect` | HARD | `guard-git-push.sh` (MECHANICAL — checks codex-review.md for VERDICT: PASS) |
| No unresolved HIGH findings in `/security-sweep` output | `/architect` | HARD | MANUAL — [TODO: automate via guard-git-push.sh update, STEP-29] |
| No open S0 compliance violations | `/architect` | HARD | MANUAL — [TODO: automate via guard-git-push.sh update, STEP-29] |
| `tasks/risk-register.md` has no unresolved S0 risks | `/architect` | HARD | MANUAL |

**Failure action:** `guard-git-push.sh` exits 2, blocking the push. `/architect` must resolve all outstanding sign-offs before re-attempting.

---

## Mandatory Gate 3 — Pre-Closeout Gate

**Transition:** release/lessons → session close

**Rule:** A session may not be closed while work is mid-flight, BOUNDARY_FLAGs are open, or the audit trail is incomplete.

| Check | Who Checks | Block Type | Enforcement |
|---|---|---|---|
| No open BOUNDARY_FLAG entries in any artifact | `/session-close` | HARD | `guard-boundary-flags.sh` (MECHANICAL) |
| No tasks in IN_PROGRESS or READY_FOR_QA state | `/session-close` | HARD | `session-integrity-check.sh` (MECHANICAL) |
| SESSION STATE is OPEN (close is valid) | `/session-close` | HARD | `guard-session-state.sh` (MECHANICAL) |
| All delivered tasks archived to `releases/session-N.md` | `/architect` | HARD | MANUAL |
| `tasks/codex-review.md` has no unprocessed verdicts | `/session-close` | ADVISORY | MANUAL — [TODO: automate via session-integrity-check.sh update, STEP-30] |

**Failure action:** `/session-close` emits BLOCKED with the specific violation. Work must be completed or explicitly deferred before close proceeds.

---

## Additional Gates (All Stage Transitions)

The three mandatory gates above are the hard enforcement points. The following gates apply to all other transitions and are currently manual.

### Gate: intake → discovery

| Check | Who Checks | Block Type | Enforcement |
|---|---|---|---|
| `docs/problem-definition.md` exists | `/ba` | ADVISORY | MANUAL |
| Problem definition accepted by AK | `/ba` | HARD | MANUAL |

---

### Gate: discovery → scope

| Check | Who Checks | Block Type | Enforcement |
|---|---|---|---|
| `docs/current-state.md` exists | `/architect` | ADVISORY | MANUAL |
| `docs/assumptions.md` exists | `/architect` | ADVISORY | MANUAL |
| Initial `tasks/risk-register.md` entries written | `/architect` | ADVISORY | MANUAL |

---

### Gate: scope → architecture

| Check | Who Checks | Block Type | Enforcement |
|---|---|---|---|
| `docs/scope-brief.md` exists and AK has accepted it | `/architect` | HARD | MANUAL |
| `docs/decision-log.md` baseline exists | `/architect` | ADVISORY | MANUAL |

---

### Gate: architecture → design

| Check | Who Checks | Block Type | Enforcement |
|---|---|---|---|
| `docs/hld.md` complete | `/ux` | HARD | MANUAL |
| `tasks/todo.md` has PENDING tasks with acceptance criteria | `/ux` | HARD | MANUAL |
| Delivery scope confirmed to include a user interface | `/ux` | HARD | MANUAL — skip design stage if no UI |

---

### Gate: implementation → QA

| Check | Who Checks | Block Type | Enforcement |
|---|---|---|---|
| All scoped tasks are READY_FOR_QA | `/qa` | HARD | MANUAL |
| No tasks in IN_PROGRESS state | `/qa` | HARD | MANUAL |
| Build passes (lint, compile, tests) | `/qa` | HARD | MANUAL |

---

### Gate: QA → security/compliance

| Check | Who Checks | Block Type | Enforcement |
|---|---|---|---|
| All scoped tasks are QA_APPROVED | `/architect` | HARD | MANUAL |
| No tasks in QA_REJECTED state | `/architect` | HARD | MANUAL |

---

### Gate: release → lessons

| Check | Who Checks | Block Type | Enforcement |
|---|---|---|---|
| Changes merged to main | `/lessons-extractor` | HARD | MANUAL |
| `docs/release-truth.md` updated | `/lessons-extractor` | ADVISORY | MANUAL |

---

### Gate: lessons → framework improvement

| Check | Who Checks | Block Type | Enforcement |
|---|---|---|---|
| New entries added to `tasks/lessons.md` | `/architect` | ADVISORY | MANUAL |
| `framework-improvements.md` reviewed for unresolved entries | `/architect` | ADVISORY | MANUAL |

---

## Enforcement Gap Summary

| Gap | Planned Automation | Plan Step |
|---|---|---|
| Planning artifacts present before implementation | `guard-planning-artifacts.sh` (PreToolUse Write) | STEP-28 |
| Security sweep sign-off blocks git push | `guard-git-push.sh` update | STEP-29 |
| Compliance sign-off blocks git push | `guard-git-push.sh` update | STEP-29 |
| Unprocessed Codex verdict blocks session close | `session-integrity-check.sh` update | STEP-30 |

---

*See `framework/governance/delivery-lifecycle.md` for full stage definitions.*
*See `framework/governance/default-workflows.md` for which gates are hard vs soft per project type.*
