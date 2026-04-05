# Versioning Policy — AK Cognitive OS v3.0
# Rules for version bumps, stamp locations, and compatibility guarantees
# Owner: Architect
# Depends on: framework/governance/change-policy.md

---

## Overview

AK Cognitive OS uses semantic versioning: `MAJOR.MINOR.PATCH`. Version bumps are performed by the Architect, recorded in `tasks/audit-log.md`, and stamped in all authoritative locations before any project receives a new deployment.

Current version: **3.0.0**

---

## Version Stamp Locations

### Authoritative stamp

`.ak-cogos-version` — the single source of truth for the framework version. This file contains exactly one line: the version string (e.g., `3.0.0`). All other stamps must match this file after any version bump.

### Secondary stamps (must be kept in sync)

| File | Variable / Field | Update method |
|---|---|---|
| `scripts/remediate-project.sh` | `VERSION=` variable near top of file | Edit the assignment line |
| `scripts/bootstrap-project.sh` | `VERSION=` variable near top of file | Edit the assignment line |

After any version bump, the Architect MUST verify all three locations are consistent before committing.

---

## Major Version Bump (X.0.0)

A major version bump signals a **breaking change** — deployed projects may require manual migration steps after remediation.

**Bump MAJOR when:**
- The 10-field (or 12-field) output envelope schema changes in a way that is not backwards-compatible (e.g., a required field is renamed or removed, field semantics change)
- A command is removed from the Final Command Set, changing the set of available personas/skills that projects depend on
- The hook contract changes (e.g., exit code semantics change, a hook is removed, environment variable requirements change)
- The SESSION STATE schema in `tasks/todo.md` changes its required fields or status enum values

**Examples:**
- Removing `/qa-run` from the command set → MAJOR bump
- Changing the output envelope from 10 fields to 8 fields (removing `manual_action` and `override`) → MAJOR bump

**What MAJOR does NOT cover:**
- Adding new commands (that is MINOR, subject to the 20-command limit)
- Changing governance document content without altering schema contracts

---

## Minor Version Bump (x.Y.0)

A minor version bump signals **new capability** added in a backwards-compatible way. Projects on the same MAJOR version can receive a MINOR update without manual migration.

**Bump MINOR when:**
- A new governance document is added to `framework/governance/`
- A new hook script is added to `scripts/hooks/` and wired into `settings.json`
- A new command is added to the Final Command Set (within the 20-command limit)
- A new guide is added to `guides/`
- `remediate-project.sh` is updated to deploy additional files to projects

**Examples:**
- Adding `framework/governance/role-taxonomy.md` (STEP-36) → MINOR bump (but batched with Phase 10 as a group)
- Adding a new `auto-teach.sh` hook → MINOR bump
- Adding a new `/risk-manager` command → MINOR bump

**Batching:** Multiple MINOR changes delivered in the same session MAY be batched into a single MINOR bump rather than one bump per change.

---

## Patch Version Bump (x.y.Z)

A patch version bump signals a **bug fix or non-functional correction**. No new capability, no contract change.

**Bump PATCH when:**
- A bug is fixed in a hook script that caused incorrect blocking or incorrect pass-through
- A wording correction is made to a governance document that does not alter its prescribed behaviour
- A validator or framework check is corrected to match the intended rule (without changing the rule itself)
- A formatting or consistency fix is applied to a command file without changing its contract

**Examples:**
- Fixing `guard-git-push.sh` to correctly read the `QA_APPROVED` string from `tasks/todo.md` → PATCH bump
- Correcting a typo in `framework/governance/stage-gates.md` → PATCH bump

---

## Compatibility Guarantees

For projects on the same MAJOR version, the following interfaces are guaranteed to remain stable across MINOR and PATCH updates:

| Interface | Guarantee |
|---|---|
| Output envelope field names and semantics (all 12 fields) | Stable across MINOR and PATCH |
| Hook exit code contract (0 = allow, 2 = block) | Stable across MINOR and PATCH |
| SESSION STATE field names and status enum (OPEN/CLOSED) | Stable across MINOR and PATCH |
| `tasks/todo.md` task block format | Stable across MINOR and PATCH |
| `tasks/audit-log.md` entry format | Stable across MINOR and PATCH |

**Not guaranteed across MINOR updates:**
- The exact set of commands (commands may be added up to the 20-command limit)
- Governance document content (may be updated to reflect new policy)

---

## Version Bump Procedure

The Architect MUST follow this sequence for every version bump:

1. Determine the correct bump type (MAJOR / MINOR / PATCH) using the criteria above.
2. Update `.ak-cogos-version` to the new version string.
3. Update `VERSION=` in `scripts/remediate-project.sh`.
4. Update `VERSION=` in `scripts/bootstrap-project.sh`.
5. Verify all three locations are consistent.
6. Commit the version bump as a standalone commit with message format: `chore: bump version to X.Y.Z`.
7. Record the bump in `tasks/audit-log.md` with event type `AK_DECISION` and the version change noted in the summary.
8. The bump is NOT deployed to projects until the corresponding release process completes — see `framework/governance/release-policy.md`.
