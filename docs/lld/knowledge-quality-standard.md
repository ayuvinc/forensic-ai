---
Status: active
Source: architect-decision + codex-review
Last confirmed: 2026-04-07
Owner: Architect
---

# Knowledge File Quality Standard

## Why This Exists

Codex review (2026-04-07) found that `knowledge/policy_sop/framework.md` mixed four different
types of claims without labelling them — legal requirements, best practice recommendations,
forensic preferences, and product rules for the AI workflow. Without labels, the model cannot
distinguish "this is law" from "this is how we like to do it."

This standard applies to all knowledge files in `knowledge/`. Files written before this standard
was defined (frm_framework.md, investigation_framework.md) require a light remediation pass
to add provenance metadata — no rewrites needed.

---

## Required Structure for Every Knowledge File

### 1. Header block (mandatory)

```markdown
---
file: knowledge/{domain}/framework.md
quality_tier: A | B | C
last_reviewed: YYYY-MM-DD
reviewer: [session ID]
open_claims: N  (number of claims flagged as needing citation)
---
```

**Quality tiers:**
- **A** — all substantive claims labeled; authoritative sources cited inline for [LAW] claims; review date within 12 months
- **B** — most claims labeled; some [LAW] claims lack inline citation but source is in sources.md; review within 18 months
- **C** — claim labeling incomplete or missing; known risky claims present; needs remediation before use

Target: all knowledge files reach tier B before any workflow uses them; tier A before production use.

---

### 2. Claim labeling (mandatory for substantive claims)

Every substantive claim — any statement that a model might present to a client as fact — must
be prefixed with one of four tags:

| Tag | Meaning | Citation required? |
|-----|---------|-------------------|
| `[LAW]` | Statutory or regulatory requirement in a specific jurisdiction. Violation has legal consequence. | Yes — cite the instrument (Act, Article, Regulation) |
| `[BEST_PRACTICE]` | Industry or professional standard. Authoritative source exists. Deviation is defensible but should be documented. | Yes — cite ACFE, IIA, ISO, or equivalent |
| `[PRODUCT_RULE]` | A rule enforced by this tool for consistency or quality. Not a legal requirement. Maher can override. | No — state the rationale briefly |
| `[ADVISORY]` | Recommended but not required. Source is professional judgment or common practice. | No — but note the basis if non-obvious |

**Example (correct labeling):**

```markdown
[LAW — UAE Labour Law Art. 47] Employer may not terminate an employee for filing a complaint
with the Ministry of Human Resources.

[BEST_PRACTICE — ACFE Fraud Examiners Manual] Chain of custody logs should record who collected
the evidence, when, from where, and in whose presence.

[PRODUCT_RULE] Every policy/SOP deliverable must include a data protection section — not a
legal requirement for all policy types, but a quality gate enforced by this tool.

[ADVISORY] Anonymous complaint acknowledgement within 3–5 business days is considered good
practice in mid-size organisations; larger organisations may need shorter SLAs.
```

---

### 3. Prohibited language (without citation)

The following words and phrases must not appear in knowledge files without an inline [LAW] citation:

- "must" / "must not" — unless followed by a citation
- "legally required" / "legally insufficient" / "legally dangerous"
- "courts have ruled" / "courts have found" — requires specific case citation or authoritative source
- "inadmissible" — evidence admissibility is jurisdiction and context specific; do not state categorically
- "automatically" — rarely true in law; avoid
- "always" / "never" — rarely true; qualify with jurisdiction or context

**Substitutes when no citation is available:**

| Prohibited | Acceptable substitute |
|---|---|
| "must include X" | "[PRODUCT_RULE] Include X" or "[BEST_PRACTICE — Source] X is recommended" |
| "courts have ruled X is insufficient" | "[ADVISORY] X alone is generally considered insufficient by practitioners; specific court authority not cited" |
| "X is inadmissible" | "[ADVISORY] X may face admissibility challenges; forensic collection procedures are preferred" |

---

### 4. Separation of claim types within a section

Do not mix [LAW] and [ADVISORY] claims in the same paragraph without visual separation.
Structure: state the legal requirement first (if any), then best practice, then product rule.

Example — correct structure:
```markdown
**Interview documentation:**

[LAW — UAE Federal Law No. 5 of 2012, Art. 21] Recording individuals without consent
may constitute a privacy offence carrying criminal penalties.

[BEST_PRACTICE — ACFE] All investigative interviews should be documented contemporaneously.
Interviewee should be offered opportunity to review and sign their statement.

[PRODUCT_RULE] This tool generates an interview summary template for Maher's use.
The template does not record the interview — Maher writes the summary.
```

---

### 5. Provenance metadata (mandatory per file)

At the top of each major section, add a brief provenance note:
```markdown
<!-- Sources: [source name(s)] — see knowledge/{domain}/sources.md for full list -->
```

This allows a reviewer to quickly identify which sources underpin a section without
reading the full sources.md.

---

## Remediation Plan for Existing Files

### knowledge/policy_sop/framework.md — KQ-01 (tier C → B)

Issues found by Codex:
1. "must", "legally insufficient", "courts have ruled" used without citation
2. No claim-type labels
3. Mixes legal obligation, best practice, and product rules without separation
4. More detailed and forceful than other knowledge files

Remediation required:
- Add [LAW], [BEST_PRACTICE], [PRODUCT_RULE], [ADVISORY] labels to all substantive claims
- Replace "must" with appropriate tag or "should" where no citation exists
- Replace "courts have ruled" with specific citations or soften to [ADVISORY]
- Remove "legally insufficient" where no specific authority is cited; replace with advisory language
- Add provenance metadata per section
- Add header block with quality_tier: B after remediation

### knowledge/frm/frm_framework.md — KQ-02 (tier B — light remediation)

Issues: no claim-type labels; file is more spec-oriented than knowledge-oriented (mixes
product design decisions with framework knowledge). No rewrite needed — add header block
and a note on each section clarifying what is framework knowledge vs product design.

### knowledge/investigation/investigation_framework.md — KQ-02 (tier B — light remediation)

Issues: no claim-type labels; otherwise good quality. Add header block and spot-check for
any absolute claims that should be softened.

---

## Standard for New Knowledge Files

All knowledge files written after this standard was established (KF-NEW, KF-01, KF-02, KF-04)
must be written at tier B from the first draft:

1. Header block present
2. All substantive claims labeled
3. Prohibited language absent
4. Provenance metadata per section
5. Sources file exists before the framework file is marked complete

Tier A is not required at first draft — it requires an external review cycle.

---

## Responsibility

| Role | Responsibility |
|------|---------------|
| Junior Dev | Writes knowledge files to this standard from the first draft |
| Architect | Reviews new files for claim labeling before they gate any workflow build |
| BA | Flags unverified [LAW] claims as open questions in ba-logic.md |
| AK | Confirms or corrects [LAW] claims that touch GoodWork-specific practice |
