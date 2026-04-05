# Artifact Map — AK Cognitive OS v3.0
# Canonical inventory of all required and recommended project artifacts
# Owner: Architect
# Source: STEP-25, tasks/framework-upgrade-plan.md + project-template/
# Authoritative reference for --audit-only gap detection (remediate-project.sh)

---

## How to Read This Table

| Column | Meaning |
|---|---|
| Artifact Name | Short name of the artifact file |
| Path | Path relative to project root — `CREATED-ON-DEMAND` means the file does not exist in project-template and is generated at runtime |
| Format | File format |
| Lifecycle Stage | Stage in which this artifact is first created — see `framework/governance/delivery-lifecycle.md` for stage definitions |
| Required / Recommended | `required` = blocking gate; `recommended` = advisory; `conditional` = required only when the stated condition is true |
| Tier | Which tier(s) require this artifact — `[TIER-TBD]` until `framework/governance/operating-tiers.md` is written (STEP-32) |

---

## Artifact Inventory

| Artifact Name | Path | Format | Lifecycle Stage | Required / Recommended | Tier |
|---|---|---|---|---|---|
| problem-definition.md | docs/problem-definition.md | Markdown | intake | required | [TIER-TBD] |
| current-state.md | docs/current-state.md | Markdown | discovery | required | [TIER-TBD] |
| assumptions.md | docs/assumptions.md | Markdown | discovery | required | [TIER-TBD] |
| risk-register.md | tasks/risk-register.md | Markdown | discovery | required | [TIER-TBD] |
| scope-brief.md | docs/scope-brief.md | Markdown | scope | required | [TIER-TBD] |
| ba-logic.md | tasks/ba-logic.md | Markdown | scope | required | [TIER-TBD] |
| decision-log.md | docs/decision-log.md | Markdown | scope | required | [TIER-TBD] |
| hld.md | docs/hld.md | Markdown | architecture | required | [TIER-TBD] |
| lld/feature-template.md | docs/lld/*.md | Markdown | architecture | required | [TIER-TBD] |
| todo.md | tasks/todo.md | Markdown | architecture | required | [TIER-TBD] |
| next-action.md | tasks/next-action.md | Markdown | architecture | required | [TIER-TBD] |
| ux-specs.md | tasks/ux-specs.md | Markdown | design | conditional (UI work) | [TIER-TBD] |
| design-system.md | tasks/design-system.md | Markdown | design | conditional (UI work) | [TIER-TBD] |
| codex-review.md | CREATED-ON-DEMAND: tasks/codex-review.md | Markdown | implementation | recommended | [TIER-TBD] |
| teaching-log.md | CREATED-ON-DEMAND: tasks/teaching-log.md | Markdown | implementation | recommended | [TIER-TBD] |
| traceability-matrix.md | docs/traceability-matrix.md | Markdown | QA | recommended | [TIER-TBD] |
| release-truth.md | docs/release-truth.md | Markdown | release | required | [TIER-TBD] |
| audit-log.md | tasks/audit-log.md | Markdown | intake | required | [TIER-TBD] |
| lessons.md | tasks/lessons.md | Markdown | lessons | required | [TIER-TBD] |
| channel.md | channel.md | Markdown | intake | required | [TIER-TBD] |
| framework-improvements.md | framework-improvements.md | Markdown | framework improvement | required | [TIER-TBD] |

**Row count: 21** (16 mandatory from STEP-25 + 5 additional project-template artifacts)

---

## Notes

- `[TIER-TBD]` values will be resolved when `framework/governance/operating-tiers.md` is written (STEP-32)
- `conditional` artifacts become `required` when their condition is true (e.g., ux-specs.md is required for any task with UI components)
- `CREATED-ON-DEMAND` artifacts have no project-template scaffold; they are created by their owner persona at the appropriate lifecycle stage
- `docs/lld/*.md` represents a directory of per-feature LLD files; the map entry covers all files matching that pattern

---

*See `framework/governance/artifact-ownership.md` for owner, reader, writer, and gate persona per artifact.*
*See `framework/governance/delivery-lifecycle.md` for stage definitions.*
*See `framework/governance/operating-tiers.md` (STEP-32) for tier-specific requirements.*
