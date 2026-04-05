# Operating Tiers — AK Cognitive OS v3.0
# Three-tier delivery system: MVP / Standard / High-Risk
# Owner: Architect
# Depends on: framework/governance/stage-gates.md, framework/governance/artifact-map.md

---

## Overview

The operating tier system allows projects to apply different levels of enforcement based on their risk profile, regulatory context, and delivery maturity. Every project declares its tier via a `Tier:` field in `CLAUDE.md`. Hooks and commands read this field to determine which gates are active.

**Tier field syntax** (hooks read `^Tier:` from CLAUDE.md):

```
Tier: MVP          # minimum gates — prototypes, internal tools, experiments
Tier: Standard     # default — most real-world projects
Tier: High-Risk    # regulated, high-stakes, or sensitive data projects
```

Missing `Tier:` field defaults to **Standard** enforcement — conservative by design.

---

## Tier: MVP

**Profile:** Prototypes, internal tools, weekend experiments, or non-user-facing projects where speed matters more than compliance.

### Required Artifacts

| Artifact | Required | Notes |
|---|---|---|
| `CLAUDE.md` with `Tier: MVP` | Yes | Must be present for hooks to detect tier |
| `tasks/todo.md` with SESSION STATE | Yes | Session lifecycle is non-negotiable at all tiers |
| `tasks/audit-log.md` | Yes | Audit trail is non-negotiable at all tiers |
| `docs/problem-definition.md` | No | Recommended but not enforced |
| `docs/scope-brief.md` | No | Recommended but not enforced |
| `docs/hld.md` | No | Recommended but not enforced |
| `tasks/risk-register.md` | No | Optional |
| `tasks/ba-logic.md` | No | Optional |

### Required Gates

| Gate | Required | Enforcement |
|---|---|---|
| Session OPEN/CLOSE lifecycle | **Yes** | `guard-session-state.sh` (MECHANICAL) |
| Audit log entry per agent run | **Yes** | `auto-audit-log.sh` (MECHANICAL) |
| QA acceptance criteria before build | No | Optional; encouraged |
| Planning docs before implementation | No | `guard-planning-artifacts.sh` exempts MVP |
| Codex review (PASS verdict) | No | Recommended for anything going to users |
| Security sweep | No | Recommended before any external release |
| Compliance gate | No | Exempt at MVP tier |
| Git push persona + QA_APPROVED check | **Yes** | `guard-git-push.sh` (MECHANICAL) |

### Allowed Shortcuts

- May skip planning docs (problem-definition.md, scope-brief.md, hld.md)
- May skip formal QA acceptance criteria
- May skip security-sweep and compliance gate
- May skip risk-register entries

### Release Constraints

- Git push to main still requires Architect persona and `QA_APPROVED` in tasks/todo.md (`guard-git-push.sh`)
- Codex gate is not required but `guard-git-push.sh` will block if a Codex review file exists with no `VERDICT:` line — do not create `tasks/codex-review.md` unless running a full Codex review

---

## Tier: Standard

**Profile:** The default tier for real-world projects — SaaS products, APIs, internal tools with real users, or any project where bugs have a material impact.

### Required Artifacts

| Artifact | Required | Notes |
|---|---|---|
| `CLAUDE.md` with `Tier: Standard` (or absent) | Yes | Absent Tier field defaults to Standard |
| `tasks/todo.md` with SESSION STATE | Yes | |
| `tasks/audit-log.md` | Yes | |
| `docs/problem-definition.md` | **Yes** | Required before Junior Dev writes code |
| `docs/scope-brief.md` | **Yes** | Required before Junior Dev writes code |
| `docs/hld.md` | **Yes** | Required before Junior Dev writes code |
| `tasks/ba-logic.md` | Yes | BA sign-off on business logic |
| `tasks/risk-register.md` | Yes | Must exist; entries at Architect discretion |
| `tasks/codex-review.md` | Yes | Required before git push to main |

### Required Gates

| Gate | Required | Enforcement |
|---|---|---|
| Session OPEN/CLOSE lifecycle | **Yes** | `guard-session-state.sh` (MECHANICAL) |
| Audit log entry per agent run | **Yes** | `auto-audit-log.sh` (MECHANICAL) |
| QA acceptance criteria before build | **Yes** | MANUAL (QA persona) |
| Planning docs before implementation | **Yes** | `guard-planning-artifacts.sh` (MECHANICAL) |
| Codex review — PASS verdict required | **Yes** | `guard-git-push.sh` (MECHANICAL) |
| QA_APPROVED required before git push | **Yes** | `guard-git-push.sh` (MECHANICAL) |
| Security sweep before release | **Yes** | MANUAL (Architect + security-sweep) |
| Compliance gate | No | Not required at Standard tier |

### Allowed Shortcuts

- May skip compliance gate (no formal compliance persona required)
- May skip risk-register entries for low-risk tasks at Architect discretion

### Release Constraints

- Git push to main requires: Architect persona + QA_APPROVED in todo.md + Codex PASS verdict
- Security sweep findings must be reviewed; unresolved HIGH findings should block release (MANUAL at Standard; MECHANICAL at High-Risk)

---

## Tier: High-Risk

**Profile:** Regulated, high-stakes, or sensitive-data projects — healthcare, finance, legal, HR systems, or any project where a failure has regulatory, financial, or safety consequences.

### Required Artifacts

| Artifact | Required | Notes |
|---|---|---|
| `CLAUDE.md` with `Tier: High-Risk` | Yes | |
| `tasks/todo.md` with SESSION STATE | Yes | |
| `tasks/audit-log.md` | Yes | |
| `docs/problem-definition.md` | **Yes** | Required at all stages |
| `docs/scope-brief.md` | **Yes** | Required at all stages |
| `docs/hld.md` | **Yes** | Required at all stages |
| `tasks/ba-logic.md` | **Yes** | Required; BA sign-off mandatory |
| `tasks/risk-register.md` | **Yes** | Required and reviewed at every session |
| `tasks/codex-review.md` | **Yes** | Required before git push |
| Compliance review output | **Yes** | Required before release; compliance persona must run |

### Required Gates

| Gate | Required | Enforcement |
|---|---|---|
| Session OPEN/CLOSE lifecycle | **Yes** | `guard-session-state.sh` (MECHANICAL) |
| Audit log entry per agent run | **Yes** | `auto-audit-log.sh` (MECHANICAL) |
| QA acceptance criteria before build | **Yes** | MANUAL (QA persona) |
| Planning docs before implementation | **Yes** | `guard-planning-artifacts.sh` (MECHANICAL) |
| Codex review — PASS verdict required | **Yes** | `guard-git-push.sh` (MECHANICAL) |
| QA_APPROVED required before git push | **Yes** | `guard-git-push.sh` (MECHANICAL) |
| Security sweep before release | **Yes** | MANUAL — unresolved HIGH findings are hard blocks |
| **Compliance gate — every stage** | **Yes** | MANUAL — `/compliance` persona must sign off per stage |
| **Risk register reviewed — every session** | **Yes** | MANUAL — Architect must review risk-register.md at session open |
| **S0 risk entries block session close** | **Yes** | `session-integrity-check.sh` (MECHANICAL) |

### Allowed Shortcuts

None. All gates are mandatory. Shortcuts that are "allowed" at MVP or Standard are not available at High-Risk.

### Release Constraints

- All Standard release constraints apply
- Compliance gate sign-off required before merge (no exceptions)
- S0 risk entries in risk-register.md block session close via `session-integrity-check.sh`
- Unresolved HIGH security findings are hard blocks (not advisory)

---

## MVP Exemption Scope — Important

The following are **NOT** exempt at MVP tier. They are non-negotiable across all tiers:

| Always enforced | Hook | Tiers |
|---|---|---|
| Session OPEN/CLOSE lifecycle | `guard-session-state.sh` | MVP + Standard + High-Risk |
| Audit log entry per agent run | `auto-audit-log.sh` | MVP + Standard + High-Risk |
| Git push requires Architect + QA_APPROVED | `guard-git-push.sh` | MVP + Standard + High-Risk |
| Persona boundary enforcement | `guard-persona-boundaries.sh` | MVP + Standard + High-Risk |

The MVP tier exempts ONLY: (1) the planning docs gate (`guard-planning-artifacts.sh`) and (2) the compliance gate. All mechanical hooks remain active.

---

## Changing Tier Mid-Project

Edit the `Tier:` field in `CLAUDE.md` and run `bash scripts/remediate-project.sh <path>` to redeploy settings.

**Downgrade rules:**
- Standard → MVP: Architect discretion; acceptable if project scope narrows
- High-Risk → Standard: **Requires AK explicit approval** — a regulatory or risk change must justify the downgrade
- Any tier → High-Risk: Upgrade at any time; apply missing gates immediately

---

*See `framework/governance/stage-gates.md` for full gate definitions.*
*See `framework/governance/artifact-map.md` for full artifact list.*
*See `guides/14-risk-tier-selection.md` for tier selection guidance.*
