# Role Design Rules — AK Cognitive OS v3.0
# Rules for adding, changing, and retiring framework commands
# Owner: Architect
# Depends on: framework/governance/role-taxonomy.md

---

## Overview

These rules govern how the framework's command set evolves. Every proposed addition, modification, or retirement of a command MUST be evaluated against the criteria in this document before it enters the framework. The classification authority is `framework/governance/role-taxonomy.md`.

---

## Rule 1 — Persona vs Skill Decision

Before adding any new command, the Architect MUST answer the following questions to determine the correct type:

| Question | If YES | If NO |
|---|---|---|
| Does this command require human judgment, domain expertise, or design decisions that vary by context? | MUST be a persona | Proceed to next question |
| Does this command execute a deterministic, repeatable operation with a fixed contract and predictable output? | MUST be a mechanical skill | Proceed to next question |
| Does this command produce insight, synthesis, or meta-level guidance without writing deliverable artifacts? | MUST be an advisory/meta skill | MUST be a quality skill |

Additional constraints:
- A command MUST NOT be classified as a persona if its output can be fully specified by a schema with no judgment required.
- A command MUST NOT be classified as a mechanical skill if the result varies based on context, stakeholder intent, or design goals.
- A command that both produces deliverable artifacts AND runs quality gates MUST be split into two commands.

---

## Rule 2 — Router vs Specialist Decision

When adding a persona that covers a broad domain, the Architect MUST determine whether it is a router or a specialist:

| Condition | Classification |
|---|---|
| The domain has 3 or more distinct sub-specializations, each requiring meaningfully different expertise | MUST be a router persona with explicit sub-persona dispatch table |
| The domain is narrow, well-bounded, and does not require further routing | MUST be a specialist persona |
| A router already exists for the domain | MUST add as a sub-persona; MUST NOT add a second router for the same domain |

Router constraints:
- A router persona MUST document its dispatch table explicitly (which topics route to which sub-persona).
- A router persona MUST NOT produce domain artifacts itself — it routes and synthesises only.
- A router persona MUST have a default sub-persona for unrecognised topics.

Specialist constraints:
- A specialist persona MUST declare its scope boundary in a BOUNDARY_FLAG block.
- A specialist persona MUST NOT expand its scope without Architect approval and a corresponding update to `role-taxonomy.md`.

---

## Rule 3 — Maximum Command Set Size

- The framework MUST NOT exceed 20 commands in the Final Command Set at any time.
- Adding a new command MUST be accompanied by retiring an existing command, OR by AK written approval to exceed the limit.
- Proposed additions MUST identify which command they replace or why an exception applies.
- The current command set is listed in `framework/governance/role-taxonomy.md` — that file is the authoritative count.

---

## Rule 4 — Deprecation Rules

When retiring a command from the framework, the Architect MUST follow this sequence:

**Step 1 — Identify dependents.**
Search all command files for references to the retiring command. Document every command that invokes or references it.

**Step 2 — Provide a replacement or migration path.**
The retiring command MUST either:
- Be replaced by a new command that covers the same function, OR
- Have its function absorbed into an existing command with an explicit note in that command's SKILL.md or `claude-command.md`

There is no sunset period — commands are either active or retired. A command cannot be "deprecated but still active."

**Step 3 — Update all dependents.**
Every command file that referenced the retired command MUST be updated to reference its replacement before the retirement is committed.

**Step 4 — Remove the command file.**
Delete `.claude/commands/<command>.md` from the framework source and from all deployed projects via `scripts/remediate-project.sh`.

**Step 5 — Update role-taxonomy.md.**
Remove the entry from `framework/governance/role-taxonomy.md` and update the count.

**Step 6 — Log in framework-improvements.md.**
Record the retirement decision with rationale in `framework-improvements.md`.

---

## Rule 5 — Classification Must Be Declared Before Build

- No new command file may be created without a classification entry in `framework/governance/role-taxonomy.md`.
- Classification MUST be approved by the Architect.
- Classification MUST be recorded in the same commit that adds the command file — not retroactively.

---

## Rule 6 — Boundary Consistency

- Every new persona command MUST include a BOUNDARY_FLAG block listing CAN and CANNOT behaviours.
- No CAN or CANNOT statement in a new command MUST contradict an existing CAN or CANNOT statement in another command.
- Conflicts between command boundaries MUST be resolved by the Architect before the command enters PENDING status.
- `framework/governance/role-taxonomy.md` is the tie-breaker for boundary disputes — the classification defines the scope.
