# Sprint-10L — Mode-Aware Review Chain: Full Design

_Derived from Monte Carlo simulation (Session 013) — 100 + 1000 iterations_

> **Implementation status (updated 2026-04-24):**
> Sprint-10L Phase A (SRL-01) built and merged — PM prompts are mode-aware.
> Sprint-10L Phase B (full behavioral matrix, component #6 Partner) was **deferred** and is
> **superseded for the Partner agent** by BA-IA-08 + BA-IA-10 (confirmed 2026-04-24,
> PARTNER-FIX-01): Partner is a sign-off agent only — `approved` is always `true`,
> `revision_requested` is always `false`, regardless of REVIEW_MODE or document level.
> The behavioral matrix in this LLD applies to the **PM agent only**. Partner behavior is
> governed by `agents/partner/prompts.py` and `agents/partner/agent.py` exclusively.

---

## Problem

The PM and Partner review agents use binary approve/reject logic.
In knowledge_only mode they correctly reject generic drafts → revision loop hits
MAX_REVISION_ROUNDS → crash. This caused 63% of all crashes in 100-iteration simulation.

---

## Behavioral Matrix

Review strictness = f(Environment, Phase, DocLevel, Authority)

### REVIEW_MODE (Environment axis)

| Mode | Description | PM/Partner behaviour |
|------|-------------|---------------------|
| `DEMO` | Showcasing capability | Auto-approve. Append demo disclaimer. Never block. |
| `DEV` | Building/testing | PASS_WITH_NOTES only. Log gaps. Never REVISION_REQUIRED. |
| `CLIENT_DRAFT` | Working document | CONDITIONAL allowed. REVISION_REQUIRED only if docs present. |
| `CLIENT_FINAL` | Delivery ready | Full enforcement. All verdict options available. |

Set via `.env`: `REVIEW_MODE=CLIENT_DRAFT`

---

### Documentation Level (DocLevel axis)

| Level | Meaning | Review implication |
|-------|---------|-------------------|
| `D0` | No documents — model knowledge only | REVISION_REQUIRED not available. PASS_WITH_NOTES max. |
| `D1` | Engagement letter only | **Treat as D0 for review** — scope defined but no evidence. Do not be stricter than D0. |
| `D2` | Partial documents uploaded | CONDITIONAL available. REVISION_REQUIRED for contradictions only. |
| `D3` | Full evidence base | Full enforcement. |

**Key finding from simulation:** D1 crashes MORE than D0 (35 vs 24 in 1000 runs).
Reason: D1 gives the system just enough scope to be strict, but no evidence to satisfy it.
D1 must be treated identically to D0 for review purposes until D2 threshold is reached.

---

### Engagement Phase axis

| Phase | Review multiplier | Implication |
|-------|-----------------|-------------|
| `INTAKE` | 0.30 | Structure only. Almost nothing should block. |
| `MID` | 0.60 | Building evidence. Flag gaps, don't block. |
| `FINAL` | 1.00 | Full review. **Cannot be overridden by any other parameter.** |

---

### Authority Level axis

| Level | Workflows | Review multiplier |
|-------|-----------|-----------------|
| `LOW` | Proposal, Training | 0.50 |
| `MED` | FRM, Investigation draft, TT, Policy | 0.75 |
| `HIGH` | Investigation final, DD | 1.00 |
| `LEGAL` | Court-bound, Sanctions | 1.30 (stricter than normal) |

---

## Verdict Spectrum

Replaces binary approve/reject. **PM selects from this set** (Partner always uses PASS — see implementation note above):

| Verdict | Meaning | Loop? | Available when |
|---------|---------|-------|----------------|
| `PASS` | Approved. Proceed. | No | Always |
| `PASS_WITH_NOTES` | Approved. Gaps logged in open_questions[]. | No | Always |
| `CONDITIONAL` | Approved for this phase. Named items must resolve before FINAL. | No | CLIENT_DRAFT+ |
| `REVISION_REQUIRED` | Send back to Junior. Specific must_fix[] items only. | Yes | D2+, MED+, non-DEMO |
| `BLOCK` | Cannot proceed. Escalate to consultant. Not a loop. | No | Any — replaces crash |

---

## Universal Blockers (enforced at orchestrator level, before agents run)

These fire for ALL workflows, ALL states:

| # | Blocker | Condition | Action |
|---|---------|-----------|--------|
| 1 | Empty primary output | findings/risks/items list is empty | BLOCK |
| 2 | Phase-authority mismatch | LEGAL authority at INTAKE phase | BLOCK |
| 3 | Jurisdiction unresolved | Operating jurisdiction not set | BLOCK |
| 4 | Schema validation failure | Pydantic rejects agent output | Fix upstream |
| 5 | Revision loop exhausted | MAX_REVISION_ROUNDS hit | BLOCK + escalate (not crash) |
| 6 | Engagement letter absent | D0 + authority HIGH or LEGAL | BLOCK at intake |

---

## Workflow-Specific Blockers

### FRM
| Gate | Condition | Authority required to block |
|------|-----------|----------------------------|
| G-A | Module dependency violation (Module 3 without Module 2) | Any |
| G-B | Empty risk register | Any |
| G-C | Risk rating inconsistency | MED+ |
| G-D | Missing risk owner | CLIENT_FINAL only |
| G-E | Wrong regulator for jurisdiction | MED+ |

### Investigation
| Gate | Condition | Authority required to block |
|------|-----------|----------------------------|
| G-A | Empty findings list | Any |
| G-B | Timeline not chronological | MED+ |
| G-C | Finding not linked to evidence | HIGH+ |
| G-D | Recommendation without finding | MED+ |
| G-E | Regulatory cite missing | HIGH+ (open_question for LOW/MED) |

### Due Diligence
| Gate | Condition | Authority required to block |
|------|-----------|----------------------------|
| G-A | Subject not identified | Any |
| G-B | Ownership chain incomplete (no UBO) | MED+ |
| G-C | Adverse media section absent | MED+ |
| G-D | PEP check absent | MED+ |
| G-E | Sanctions not checked | Always — BLOCK regardless of mode |

### Sanctions Screening
| Gate | Condition | Action |
|------|-----------|--------|
| G-A | Live screen not conducted (RESEARCH_MODE != live) | BLOCK — escalate, never loop |
| G-B | Not all lists screened | BLOCK |
| G-C | Potential match not escalated | BLOCK |
| G-D | Result presented as clearance | BLOCK + rewrite disclaimer |
| G-E | Entity name variants not checked | CONDITIONAL |

### Transaction Testing
| Gate | Condition | Authority required to block |
|------|-----------|----------------------------|
| G-A | Population not defined | Any — intake gate (block before run) |
| G-B | Sampling methodology absent | MED+ |
| G-C | Exception not documented | Any |
| G-D | Test objective mismatch | MED+ |
| G-E | No conclusion on exceptions | CLIENT_FINAL only |

### Policy/SOP
| Gate | Condition | Authority required to block |
|------|-----------|----------------------------|
| G-A | No regulatory basis cited | MED+ |
| G-B | Owner not assigned | CLIENT_FINAL only |
| G-C | Review cycle absent | CLIENT_FINAL only |
| G-D | No enforcement mechanism | CLIENT_FINAL only |
| G-E | Jurisdiction gap | HIGH+ |

### Proposal
| Gate | Condition | Action |
|------|-----------|--------|
| G-A | Scope too vague | REVISION_REQUIRED always |
| G-B | Fee not anchored to scope | REVISION_REQUIRED always |
| G-C | Team not relevant to scope | CONDITIONAL |
| G-D | Methodology section absent | CONDITIONAL |
| G-E | T&C missing | CONDITIONAL |

---

## Worst State Combinations (from 1000-iteration simulation)

| Combination | Crashes | Interpretation |
|-------------|---------|---------------|
| CLIENT_DRAFT + FINAL + D0 + MED | 6 | Trying to finalize with zero evidence — process failure |
| CLIENT_DRAFT + FINAL + D2 + HIGH | 6 | Evidence partial but authority demands full — gap |
| CLIENT_DRAFT + MID + D1 + HIGH | 5 | Engagement letter only, high authority, mid-run — pressure gap |
| CLIENT_DRAFT + FINAL + D2 + MED | 5 | Most common real scenario — partial evidence + final phase |

---

## Monte Carlo Results Summary (1000 iterations)

**With behavioral matrix applied:**
- Overall crash rate: 2-4% per workflow (down from 60% without matrix)
- Trust breach (< 0.60): iteration 6, recovers to 1.0 by end
- Highest crash rate: Transaction Testing (3.5%) — intake quality issue (PQ-01 urgent)
- MED authority has most absolute crashes (53/111) — most common real-work authority level

**Without behavioral matrix (current code):**
- Overall crash rate: 60%
- Trust breach: iteration 3, never recovers
- Nash equilibrium: Maher avoids live mode permanently

---

## Sprint-10L Build Components

| # | Component | Files | Priority |
|---|-----------|-------|----------|
| 1 | `REVIEW_MODE` config flag | config.py | P1 |
| 2 | Verdict spectrum data types | schemas/artifacts.py | P1 |
| 3 | Behavioral matrix function | core/orchestrator.py | P1 |
| 4 | Universal blocker checks | core/orchestrator.py | P1 |
| 5 | PM prompt + agent: mode-aware criteria | agents/project_manager/ | P1 |
| 6 | Partner prompt + agent: mode-aware criteria | agents/partner/ | SUPERSEDED — Partner is always sign-off (PARTNER-FIX-01, 2026-04-24) |
| 7 | D0/D1 equivalence enforcement | core/orchestrator.py | P1 |
| 8 | Sanctions/DD: G-A = BLOCK not loop | workflows/sanctions_screening.py, due_diligence.py | P1 |
| 9 | TT + Investigation intake completeness gate | workflows/transaction_testing.py, investigation_report.py | P2 |
| 10 | FINAL phase multiplier lock (no override) | core/orchestrator.py | P1 |

**~10 files. Plan mode required. Architect must approve before build.**
