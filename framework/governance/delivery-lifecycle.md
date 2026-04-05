# Delivery Lifecycle — AK Cognitive OS v3.0
# Canonical 11-stage lifecycle for all projects running on this framework
# Owner: Architect
# Authoritative reference for stage-gates.md and default-workflows.md

---

## Overview

Every delivery cycle in AK Cognitive OS passes through exactly 11 stages in order. Stages define **what** happens and **who** is responsible — not how it is implemented. Each stage has a single owner persona responsible for producing its output artifacts and declaring the exit condition met.

Stages may be marked optional or skipped for specific project tiers and workflow types — see `framework/governance/default-workflows.md`. The canonical order is always: intake → discovery → scope → architecture → design → implementation → QA → security/compliance → release → lessons → framework improvement.

---

## Stage Definitions

### Stage 1 — intake

**Purpose:** Establish the problem space. Capture the raw requirement as a written problem definition so that all downstream stages work from a shared, durable statement of intent rather than a verbal or implicit description.

| Field | Value |
|---|---|
| Entry condition | AK initiates a new project or session with a requirement statement |
| Artifacts in | none |
| Artifacts out | `docs/problem-definition.md` |
| Owner persona | `/ba` |
| Exit condition | `docs/problem-definition.md` exists, AK has confirmed it reflects the intent |

---

### Stage 2 — discovery

**Purpose:** Understand the context surrounding the problem — current state, constraints, open assumptions, and initial risks — before committing to scope. Prevents scope decisions from being made without evidence.

| Field | Value |
|---|---|
| Entry condition | `docs/problem-definition.md` exists |
| Artifacts in | `docs/problem-definition.md` |
| Artifacts out | `docs/current-state.md`, `docs/assumptions.md`, `tasks/risk-register.md` (initial entries) |
| Owner persona | `/ba` (with `/researcher` support for external research) |
| Exit condition | Current state documented, assumptions listed, initial risks registered |

---

### Stage 3 — scope

**Purpose:** Define the boundaries of what will and will not be built in this delivery cycle. A frozen scope brief prevents requirements creep and gives the Architect a stable target for task decomposition.

| Field | Value |
|---|---|
| Entry condition | `docs/current-state.md` and `docs/assumptions.md` present |
| Artifacts in | `docs/problem-definition.md`, `docs/current-state.md`, `docs/assumptions.md` |
| Artifacts out | `docs/scope-brief.md`, `docs/decision-log.md` (baseline) |
| Owner persona | `/architect` (with `/ba` sign-off on business boundaries) |
| Exit condition | `docs/scope-brief.md` accepted by AK; scope is frozen for this cycle |

---

### Stage 4 — architecture

**Purpose:** Translate frozen scope into a technical delivery plan — high-level design, low-level feature specs, and a task breakdown with explicit acceptance criteria and dependency order.

| Field | Value |
|---|---|
| Entry condition | `docs/scope-brief.md` frozen; AK approval received |
| Artifacts in | `docs/scope-brief.md`, `tasks/ba-logic.md` (if business logic defined) |
| Artifacts out | `docs/hld.md`, `docs/lld/*.md`, `tasks/todo.md` (PENDING tasks with AC), `tasks/next-action.md` |
| Owner persona | `/architect` |
| Exit condition | All PENDING tasks have acceptance criteria; no open BOUNDARY_FLAGs in architecture artifacts |

---

### Stage 5 — design

**Purpose:** Define the user experience and visual direction for any user-facing work — interaction flows, component states, breakpoints, accessibility rules, and design tokens.

| Field | Value |
|---|---|
| Entry condition | `docs/hld.md` exists; delivery scope includes a user interface |
| Artifacts in | `docs/hld.md`, `docs/scope-brief.md` |
| Artifacts out | `tasks/ux-specs.md`, `tasks/design-system.md` |
| Owner persona | `/ux` (interaction and behaviour), `/designer` (visual direction) |
| Exit condition | `tasks/ux-specs.md` accepted by Architect; `tasks/design-system.md` populated with design tokens and component conventions |

---

### Stage 6 — implementation

**Purpose:** Build the scoped work exactly to spec. Each task advances from PENDING through IN_PROGRESS to READY_FOR_QA with no scope additions and no tasks left mid-flight.

| Field | Value |
|---|---|
| Entry condition | `tasks/todo.md` has PENDING tasks with complete acceptance criteria; all planning artifacts from architecture (and design, if applicable) are present |
| Artifacts in | `tasks/todo.md`, `docs/lld/*.md`, `tasks/ux-specs.md` (if UI work) |
| Artifacts out | Code/content files per task; `tasks/todo.md` updated (tasks = READY_FOR_QA) |
| Owner persona | `/junior-dev` |
| Exit condition | All scoped tasks are READY_FOR_QA; no task remains IN_PROGRESS |

---

### Stage 7 — QA

**Purpose:** Verify built work against all acceptance criteria. Tasks are approved or returned to implementation with explicit rejection notes until all criteria pass.

| Field | Value |
|---|---|
| Entry condition | At least one task is in READY_FOR_QA state |
| Artifacts in | `tasks/todo.md` (READY_FOR_QA tasks), built artifacts |
| Artifacts out | `tasks/todo.md` (tasks = QA_APPROVED or QA_REJECTED with notes), `docs/traceability-matrix.md` |
| Owner persona | `/qa` |
| Exit condition | All scoped tasks are QA_APPROVED; no task in QA_REJECTED state |

---

### Stage 8 — security/compliance

**Purpose:** Verify the built work against security engineering requirements and regulatory obligations. A hard-stop gate on any HIGH security finding or S0 compliance violation before release is permitted.

| Field | Value |
|---|---|
| Entry condition | All scoped tasks are QA_APPROVED |
| Artifacts in | Built artifacts, `tasks/risk-register.md` |
| Artifacts out | `tasks/risk-register.md` (updated with findings), `/security-sweep` sign-off, `/compliance` sign-off |
| Owner persona | `/security-sweep` (engineering security), `/compliance` (regulatory) |
| Exit condition | No unresolved HIGH security findings; no open S0 compliance violations |

---

### Stage 9 — release

**Purpose:** Package and merge the completed work. Archive task records, stamp the release, and update the release truth document so the project's canonical state is current.

| Field | Value |
|---|---|
| Entry condition | Security/compliance stage complete; all tasks QA_APPROVED; no open BOUNDARY_FLAGs |
| Artifacts in | All QA_APPROVED task artifacts, `tasks/todo.md` |
| Artifacts out | `docs/release-truth.md` (updated), `releases/session-N.md` (archived tasks), `channel.md` (updated) |
| Owner persona | `/architect` |
| Exit condition | Changes merged to main; `docs/release-truth.md` current; `tasks/todo.md` cleared of delivered tasks |

---

### Stage 10 — lessons

**Purpose:** Extract repeatable insights from the delivery cycle — what worked, what failed, and what should change. Feeds both future session behaviour and the framework improvement backlog.

| Field | Value |
|---|---|
| Entry condition | Release stage complete |
| Artifacts in | `tasks/audit-log.md`, `tasks/lessons.md`, `channel.md` |
| Artifacts out | `tasks/lessons.md` (new entries), `framework-improvements.md` (if framework changes identified) |
| Owner persona | `/lessons-extractor` |
| Exit condition | New lesson entries written to `tasks/lessons.md`; `framework-improvements.md` updated if applicable |

---

### Stage 11 — framework improvement

**Purpose:** Apply learnings that belong to the framework itself — updated persona contracts, schema changes, hook improvements, and governance policy updates that benefit all future projects.

| Field | Value |
|---|---|
| Entry condition | Lessons stage complete; `framework-improvements.md` has unresolved entries |
| Artifacts in | `framework-improvements.md`, `tasks/lessons.md` |
| Artifacts out | Updated framework artifacts (commands, schemas, hooks, governance docs); `framework-improvements.md` entries resolved or deferred |
| Owner persona | `/architect` |
| Exit condition | All `framework-improvements.md` entries are resolved or explicitly deferred to a future session; session closes cleanly |

---

## Stage Summary Table

| # | Stage | Owner | Key Artifact Out | Required By Default |
|---|---|---|---|---|
| 1 | intake | /ba | problem-definition.md | yes |
| 2 | discovery | /ba | current-state.md, assumptions.md | yes |
| 3 | scope | /architect | scope-brief.md | yes |
| 4 | architecture | /architect | hld.md, lld/*.md, todo.md | yes |
| 5 | design | /ux, /designer | ux-specs.md, design-system.md | conditional (UI work) |
| 6 | implementation | /junior-dev | code files, todo.md updated | yes |
| 7 | QA | /qa | todo.md (QA_APPROVED), traceability-matrix.md | yes |
| 8 | security/compliance | /security-sweep, /compliance | risk-register.md updated | tier-dependent |
| 9 | release | /architect | release-truth.md, releases/session-N.md | yes |
| 10 | lessons | /lessons-extractor | lessons.md updated | yes |
| 11 | framework improvement | /architect | framework-improvements.md resolved | conditional (framework changes) |

---

*See `framework/governance/stage-gates.md` for entry/exit enforcement rules per transition.*
*See `framework/governance/default-workflows.md` for required vs optional per project type.*
