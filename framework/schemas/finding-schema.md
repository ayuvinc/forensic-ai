# Finding Schema
# AK Cognitive OS
# validation: markdown-contract-only | machine-validated

---

## Purpose

Defines the canonical format for any finding produced by any persona or Codex.
All findings use S0/S1/S2 severity. No other severity levels exist in this framework.

---

## Finding Format

```
ID:              {STACK}-{sprint_id}-{seq}   # e.g. CLD-001-01 or CDX-001-01
Severity:        S0 | S1 | S2
Origin:          claude-core | codex-core
Location:        file:line | n/a
Finding:         One sentence describing the issue
Scope reviewed:  What was actually examined
Blocking?:       YES (S0) | AK_DECISION (S1) | NO (S2)
Recommended fix: One sentence
```

---

## Severity Contract

| Severity | Meaning | Merge policy | Who resolves |
|---|---|---|---|
| S0 | Critical — system is broken or unsafe | Merge BLOCKED, no exceptions | Architect + AK |
| S1 | Significant — must resolve or explicitly accept | AK_DECISION required before merge | AK decides |
| S2 | Advisory — improvement, not required | Log rationale, may defer | Builder decides |

---

## Severity Examples

| Severity | Example |
|---|---|
| S0 | Auth bypass — unauthenticated access to protected data |
| S0 | Data corruption — writes destroy existing records |
| S0 | Build fails — code does not compile |
| S1 | Missing error handling on external API calls |
| S1 | No type safety on user-supplied input |
| S2 | Variable naming inconsistent with conventions |
| S2 | Missing docstring on exported function |

---

## Compliance Findings (Compliance Persona)

Compliance findings use the same S0/S1/S2 schema with compliance-specific meanings:

| Severity | Compliance meaning | Action |
|---|---|---|
| S0 | Hard legal/regulatory violation (e.g. PHI unencrypted) | Hard block — nothing ships |
| S1 | Significant compliance gap requiring AK decision | AK decision — fix before launch or accept risk |
| S2 | Advisory — log and defer | Log + defer to next sprint |

See `personas/compliance/schema.md` for full compliance severity examples.

---

## Conflict Resolution

When Claude-core and Codex-core produce contradictory findings on the same artifact:

| Conflict type | Resolution |
|---|---|
| Tests pass (Claude) vs structural flaw (Codex) | Codex wins — tests passing ≠ correct design |
| Security finding — different severity | Higher severity wins |
| Codex APPROVED vs AK disagrees | AK wins — AK_DECISION logged |
| Codex REJECTED vs Claude review PASS | Codex wins — fresh-session independence |
| Both BLOCKED on different reasons | Both reasons logged; Architect resolves order |
| S0 from either stack | Always blocks merge — no override |

All conflicts logged to [AUDIT_LOG_PATH] with event_type: AK_DECISION or BOUNDARY_FLAG_OPENED.

---

## Validation Rules

- Missing `ID` field → finding is not trackable, reject
- Missing `Severity` → cannot apply merge policy, reject
- Severity not in [S0, S1, S2] → `SCHEMA_VIOLATION: severity`
- Missing `Blocking?` → unclear merge impact, reject
- S0 finding without BLOCKED status on enclosing envelope → contract violation
