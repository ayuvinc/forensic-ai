# Role Taxonomy — AK Cognitive OS v3.0
# Classification of all 20 framework commands
# Owner: Architect
# Authoritative reference for role-design-rules.md and all persona/skill additions
# Derived from: tasks/ba-logic.md BL-001 (INCORPORATED)

---

## Overview

Every command in AK Cognitive OS belongs to exactly one of six categories. Classification determines how a command is used, who invokes it, and what constraints apply to it. No command may exist outside this taxonomy. New commands must be classified before they enter the framework — see `framework/governance/role-design-rules.md`.

**Final Command Set size: 20**

---

## Category Definitions

| Category | Definition |
|---|---|
| **Delivery Persona** | Represents a human role in the SDLC. Has a WHO YOU ARE identity, CAN/CANNOT boundaries, and a HANDOFF envelope. Produces stage artifacts. Cannot be mechanically substituted. |
| **Router Persona** | Broad-domain entry point that routes to specialist sub-personas. Accepts a topic and delegates to the right specialist. Does not produce domain artifacts itself — it dispatches. |
| **Specialist Persona** | Narrow-domain expert invoked directly or via a router. Has a bounded, well-defined scope. Does not route further. |
| **Mechanical Skill** | Executes a deterministic, repeatable operation with no judgment required. Has a strict contract, fixed inputs/outputs. Persona-independent — any persona may invoke it. |
| **Advisory/Meta Skill** | Provides insight, synthesis, or meta-level guidance. Reads context, produces recommendations or summaries. Does not write deliverable artifacts. |
| **Quality Skill** | Executes a quality gate — builds, tests, sweeps, or reviews against defined criteria. Has pass/fail output. Blocks downstream work on failure. |

---

## Delivery Personas (5)

| Command | Rationale |
|---|---|
| `/architect` | Designs systems, owns task decomposition, merges branches, closes sessions. Requires judgment at every step — cannot be reduced to a mechanical operation. |
| `/ba` | Translates AK's requirements into structured business logic. Owns `tasks/ba-logic.md`. Requires domain interpretation and stakeholder alignment. |
| `/junior-dev` | Implements specs exactly to scope. Creates feature branches, runs builds. Execution is bounded by task spec but requires code-level judgment on implementation details. |
| `/qa` | Defines and owns acceptance criteria. Evaluates build quality before and after implementation. Requires quality judgment — cannot be a checklist runner. |
| `/ux` | Designs interaction behavior, user flows, states, breakpoints, and accessibility. Owns `tasks/ux-specs.md`. Requires design judgment distinct from visual styling. |

---

## Router Personas (2)

| Command | Rationale |
|---|---|
| `/researcher` | Broad research entry point covering business, legal, news, policy, and technical domains. Routes to the appropriate specialist researcher based on topic. Does not itself produce research output — it dispatches and synthesizes. |
| `/compliance` | Broad compliance entry point covering data privacy, data security, PHI handling, and PII handling. Routes to the appropriate compliance specialist. Does not itself conduct compliance review — it dispatches and coordinates. |

---

## Specialist Personas (2)

| Command | Rationale |
|---|---|
| `/designer` | Visual and brand direction specialist. Owns design tokens, component naming, and visual rules in `tasks/design-system.md`. Scoped strictly to visual/brand — interaction behavior belongs to `/ux`. |
| `/risk-manager` | Risk identification and classification specialist. Owns `tasks/risk-register.md`. Invoked by Architect after task decomposition. Narrowly scoped to risk assessment — does not make delivery decisions. |

---

## Mechanical Skills (4)

| Command | Rationale |
|---|---|
| `/session-open` | Deterministic session initialisation: reads SESSION STATE, validates CLOSED, transitions to OPEN, generates standup, writes channel.md. Fixed contract, no judgment required. |
| `/session-close` | Deterministic session closeout: validates tasks archived, transitions SESSION STATE to CLOSED, writes next-action.md, pushes to remote. Fixed contract, no judgment required. |
| `/compact-session` | Deterministic context compression: summarises session history to reduce token load. Fires automatically at context threshold. No judgment required. |
| `/audit-log` | Appends a single structured entry to `tasks/audit-log.md`. Append-only, schema-validated, deterministic. Called by every other agent at completion. |

---

## Advisory/Meta Skills (3)

| Command | Rationale |
|---|---|
| `/teach-me` | Synthesises teaching content from the current task context. Reads what was built and explains it. Does not write deliverable artifacts — produces teaching notes to `memory/teaching-log.md`. |
| `/lessons-extractor` | Reviews session history and extracts reusable lessons to `tasks/lessons.md`. Meta-level synthesis — does not produce feature output. |
| `/check-channel` | Reads `channel.md` and reports current session state, active persona, and blockers. Informational only — does not modify state. |

---

## Quality Skills (4)

| Command | Rationale |
|---|---|
| `/qa-run` | Executes acceptance criteria against built output. Produces QA_APPROVED or QA_REJECTED verdict. Blocks downstream work on rejection. |
| `/security-sweep` | Engineering review of auth, abuse surface, replay risk, rate limits, and trust boundaries. Produces PASS or unresolved HIGH findings that block release. |
| `/codex-prep` | Pre-flight gate before Codex review. Validates completeness and token efficiency of review package. Blocks Codex invocation if pre-flight fails. |
| `/codex-read` | Routes Codex verdict: APPROVED → READY_FOR_QA, CONDITIONS → architect review, REJECTED → REVISION_NEEDED. Deterministic routing based on verdict field. |

---

## Summary Table

| Command | Category | Count |
|---|---|---|
| architect, ba, junior-dev, qa, ux | Delivery Persona | 5 |
| researcher, compliance | Router Persona | 2 |
| designer, risk-manager | Specialist Persona | 2 |
| session-open, session-close, compact-session, audit-log | Mechanical Skill | 4 |
| teach-me, lessons-extractor, check-channel | Advisory/Meta Skill | 3 |
| qa-run, security-sweep, codex-prep, codex-read | Quality Skill | 4 |
| **Total** | | **20** |
