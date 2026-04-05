# Change Policy — AK Cognitive OS v3.0
# How the framework evolves: proposals, review, escalation, and rollback
# Owner: Architect
# Depends on: framework/governance/role-design-rules.md

---

## Overview

The framework is a living system. Changes are expected — but every change must be proposed, reviewed, approved, and recorded before it is implemented. This document defines the process. No framework change proceeds without an entry in `framework-improvements.md`.

---

## What Constitutes a Framework Change

A framework change is any modification to:
- A command file in `.claude/commands/`
- A hook script in `scripts/hooks/`
- A governance document in `framework/governance/`
- `project-template/` contents (CLAUDE.md, settings.json, directory structure)
- `schemas/` contracts
- `scripts/bootstrap-project.sh` or `scripts/remediate-project.sh`
- `.ak-cogos-version`

Bug fixes to existing files that do not alter behaviour or contracts are **patches** — they still require a record in `framework-improvements.md` but do not require the full proposal process.

---

## Proposal Format

Every framework change proposal MUST include the following fields before review begins:

| Field | Required | Description |
|---|---|---|
| `change_id` | YES | Unique identifier — format: `CHG-NNN` |
| `change_description` | YES | What is changing and how, in plain language |
| `motivation` | YES | Why this change is needed — reference session, failure, or requirement |
| `affected_commands_artifacts` | YES | List every command file, hook, or governance doc affected |
| `risk_level` | YES | `LOW` / `MEDIUM` / `HIGH` — see risk criteria below |
| `proposed_by` | YES | Persona that identified the need (e.g., Architect, QA) |
| `replacement_or_migration` | If retiring a command | What replaces the retiring command or absorbs its function |

**Risk level criteria:**

| Level | Applies when |
|---|---|
| `LOW` | Change affects 1 file, no contract change, no hook behaviour change |
| `MEDIUM` | Change affects 2–4 files, or alters a hook gate condition |
| `HIGH` | Change affects 5+ files, modifies a schema contract, removes a command, or changes enforcement behaviour |

---

## Review Process

Changes proceed through review in this order — no step may be skipped:

**Step 1 — Architect review (design gate)**
The Architect reviews the proposal for technical correctness, boundary consistency, and dependency impact. The Architect MUST approve or reject before AK sees the proposal. Rejection at this step returns the proposal to the proposer for revision.

**Step 2 — AK review (scope and priority gate)**
AK reviews the Architect-approved proposal for scope fit and priority. AK decides whether this change belongs in the current sprint, a future sprint, or is rejected entirely.

**Step 3 — Record in framework-improvements.md**
After AK approval, the Architect records the approved proposal in `framework-improvements.md` with status `APPROVED`. No build work begins before this entry exists.

**Step 4 — Implementation**
Junior Dev implements to spec. Standard task workflow applies (QA AC → build → qa-run → Architect merge).

**Step 5 — Version bump**
After merge, the Architect bumps the version per `framework/governance/versioning-policy.md` and records the bump in `tasks/audit-log.md`.

---

## Escalation — Repeated Failure to Framework Change

When the same failure pattern recurs across sessions, it is a signal that the framework itself needs to change — not just the output of a single task.

**Trigger condition:** The same failure type occurs in 2 or more separate sessions without a framework-level fix between them.

When this trigger fires:
1. The Architect MUST log the pattern in `framework-improvements.md` with status `ESCALATED`.
2. The `/framework-delta-log` skill MUST be run to capture the delta between the current state and the expected state.
3. The Architect MUST write a framework change proposal (using the format above) within the same session the escalation is identified.
4. AK MUST be notified of the escalation before the session closes — it is a blocker on session-close if unaddressed.

The `/framework-delta-log` skill is the canonical mechanism for capturing what changed, what regressed, and what gap the framework failed to enforce.

---

## Rollback

If a framework change causes a regression — identified by validate-framework.sh FAIL, hook malfunction, or QA_REJECTED after a previously passing build — the following steps apply:

1. **Stop.** Do not attempt to fix forward in the same session without Architect assessment.
2. The Architect assesses whether the regression is in the change itself or in dependent components.
3. If the change is the root cause: revert the change commit and restore the previous file state.
4. Record the regression and revert in `tasks/audit-log.md` with event type `FRAMEWORK_GAP_IDENTIFIED`.
5. Update `framework-improvements.md` — mark the proposal `REVERTED` with root cause noted.
6. The change re-enters the proposal process with the regression as a documented constraint.

A reverted change MUST NOT be re-implemented without addressing the root cause that caused the regression.
