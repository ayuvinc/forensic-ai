# Guardrails Design Rules

_Owner: Architect | Last updated: 2026-04-08_

---

## Rule 1 — Mode-Awareness (MANDATORY)

**Every guardrail that references external data quality MUST condition on RESEARCH_MODE.**

External data guardrails include checks on:
- Authoritative citations (regulatory_lookup, sanctions_check, company_lookup)
- Live sanctions match results
- Regulatory source verification
- Any check that requires a network call to pass

### Required pattern

```python
from config import RESEARCH_MODE

if RESEARCH_MODE == "live":
    # Hard block — external data was expected and not found
    raise NoCitationsError("...")
else:
    # knowledge_only — append disclaimer, never hard block
    output_text += "\n\n[Knowledge-only mode: ...]"
```

### Why this rule exists

BUG-10 (Session 013): the citation guard in `core/agent_base.py` raised `NoCitationsError`
in `knowledge_only` mode because research tools return stubs — the model has no way to
call authoritative tools and get real results. The guard was designed for live mode only
but fired unconditionally. This blocked the entire P7-GATE smoke test.

**Silent degradation is worse than a startup error.** If a guardrail fires in knowledge_only
mode, it produces a crash with no output — the consultant gets nothing. A disclaimer
with flagged gaps is always preferable to a crash.

### Scope

This rule applies to ALL guardrails in:
- `core/agent_base.py`
- `core/orchestrator.py`
- Any future workflow-level pre-flight checks

When adding a new guardrail: ask "does this check require external data?" If yes — add
the RESEARCH_MODE condition before the hard block.

---

## Rule 2 — Sanctions Workflow Exception

The sanctions screening workflow is a special case. In `knowledge_only` mode:

- A prominent red warning panel is displayed BEFORE workflow runs (PPH-02a)
- Consultant must explicitly confirm to proceed
- Output is clearly labelled as NOT a live sanctions clearance
- The workflow still runs (template structure is useful) but result cannot be used for compliance

This is NOT a crash — it is a user-acknowledged degraded output. The distinction matters.

---

## Rule 3 — Blocker vs Crash

Guardrails must never cause an unhandled exception in production. Every guardrail must
resolve to one of:
- **PASS** — proceed normally
- **WARN** — proceed with disclaimer appended
- **BLOCK** — return structured error to orchestrator (not raise uncaught exception)

Unhandled exceptions (crashes) are not acceptable for any core workflow. This is the
lesson from G-13/G-14 (Monte Carlo, Session 013): the revision loop exhausting caused
an uncaught termination, not a structured BLOCK. Sprint-10L Phase B (behavioral matrix)
will enforce BLOCK as the terminal state — never crash.
