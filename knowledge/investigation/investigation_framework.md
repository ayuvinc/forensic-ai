---
file: knowledge/investigation/investigation_framework.md
quality_tier: B
last_reviewed: 2026-04-07
reviewer: session-011
open_claims: 0
---

<!-- Sources: knowledge/investigation/sources.md — see that file for full URLs -->
<!-- Claim labels: [LAW] [BEST_PRACTICE] [PRODUCT_RULE] [ADVISORY] — see docs/lld/knowledge-quality-standard.md -->

# Investigation Framework Knowledge Base

## What It's For

A client suspects fraud, misconduct, or a compliance breach. They want a formal investigation report. The Consultant runs a structured investigation workflow: Junior Analyst → Project Manager → Partner, producing a defensible written report.

---

## Investigation Types

| # | Type | Description |
|---|------|-------------|
| 1 | Asset misappropriation | Procurement, payroll, expense, cash fraud |
| 2 | Financial statement fraud | Manipulated accounting records |
| 3 | Corruption / bribery / kickbacks | Illicit payments, schemes |
| 4 | AML / suspicious transactions | Anti-money laundering violations |
| 5 | Cybercrime / BEC / digital fraud | Business Email Compromise, hacking |
| 6 | Regulatory breach | Violations of specific regulations |
| 7 | Whistleblower complaint | Formal internal complaints |
| 8 | Agreed-Upon Procedures (AUP) | Strictly scoped procedures; factual findings only — no conclusions |
| 9 | Other / Custom | Investigation does not fit a predefined category; structure proposed by model, confirmed by Maher |

---

## AUP Mode — Special Rules (Type 8)

AUP engagements follow AICPA/IAASB agreed-upon procedures standards. The scope is the procedures list — nothing else is in scope.

**Intake:** Maher provides the agreed procedures list as numbered items. Each item is discrete and specific. The intake conversation confirms: (a) who agreed to these procedures (client, regulator, counsel?), (b) the subject matter (transactions, contracts, accounts), (c) the reporting period.

**Agent behavior — Junior:**
- Structure output as one section per procedure: Procedure → Work Performed → Factual Finding.
- Do not add sections outside the procedures list.
- Do not draw conclusions or implications. Report only what was observed.
- If evidence encountered is outside the procedures scope, flag as "Matter Outside Scope" — do not investigate or report findings on it.

**Agent behavior — PM:**
- Check that every procedure in the list has a corresponding section. Flag any missing procedures.
- Check that no conclusion or recommendation language has been introduced.

**Agent behavior — Partner:**
- HARD RULE: no opinion language, no "therefore", no recommendations unless a procedure explicitly calls for one.
- If any conclusion language is found, return to PM with: "AUP — conclusions not permitted. Strip and restate as observation."
- Confirm procedures list in output matches procedures list in intake exactly.

**AUP report does NOT include:**
- Executive Summary (replace with "Purpose and Scope of Procedures")
- Findings and Conclusions section
- Recommendations section
- Any implication language

---

## Custom Investigation Mode — Special Rules (Type 9)

For investigations that span categories or do not fit any predefined type.

**Intake:** Maher describes in free text: (a) the nature of the matter, (b) the subject (person, entity, process, transaction set), (c) the objectives (what questions need to be answered), (d) any known evidence already in hand.

**Pre-draft structure confirmation:** Before the Junior begins drafting, the model proposes a report structure tailored to the described matter. Maher confirms or adjusts. Draft begins only after structure is confirmed. This step is mandatory for Custom type.

**Agent behavior:** All standard investigation rules apply (evidence chain, three-agent pipeline, regulatory checks, authoritative citations). The difference is that the structural template is derived from the description, not from a predefined category template.

**Partner review for Custom type:** Coherence and defensibility are the primary criteria. Partner confirms: (a) stated objectives are addressed, (b) conclusions follow from evidence, (c) no scope creep beyond the stated matter.

---

## Report Audiences

| # | Audience | Standard | Focus |
|---|----------|----------|-------|
| 1 | Internal — Board / HR / Management | Internal investigation standard | Findings + action recommendations |
| 2 | Regulator — CBUAE / DFSA / SCA | Regulatory reporting requirements | Regulatory mapping + citations |
| 3 | Legal proceedings — Court / Arbitration | Expert witness standard | Detailed methodology, evidence chain, defensible conclusions |
| 4 | Multiple audiences | Combined | All of the above |

---

## Evidence Types

Materials investigators work with:
- Transaction records
- Invoices and contracts
- Interview transcripts
- Emails and communications
- Screenshots and digital evidence
- Bank statements
- Expense reports
- MOMs (Minutes of Meetings)
- Company documents and corporate filings

---

## Three-Agent Pipeline

```
Junior Analyst  → researches: industry fraud patterns, regulatory requirements,
                  sanctions checks on named entities, company ownership lookups
                  → produces draft: findings, evidence, methodology, open questions

Project Manager → reviews draft: checks for gaps, missing citations, weak sections
                  → either approves or sends back to Junior with must-fix list

Partner         → final review: regulatory sign-off, escalation check, approval
```

---

## Investigation Opening Conversation Flow

```
Consultant: What is the case name and client?
> Al Noor Construction — procurement fraud suspicion

Consultant: What type of investigation is this?
  1. Asset misappropriation (procurement, payroll, expense, cash)
  2. Financial statement fraud
  3. Corruption / bribery / kickbacks
  4. AML / suspicious transactions
  5. Cybercrime / BEC / digital fraud
  6. Regulatory breach
  7. Whistleblower complaint
> 1 — procurement fraud

Consultant: Who is the audience for the final report?
  1. Internal — board / HR / management (disciplinary action)
  2. Regulator — CBUAE / DFSA / SCA (regulatory submission)
  3. Legal proceedings — court / arbitration (expert report)
  4. Multiple audiences
> 1

Consultant: What materials do you have?
  Upload or describe: transaction records, invoices, contracts,
  interview transcripts, emails, screenshots, MOM...
> [user uploads vendor invoices Excel + interview notes]
```

---

## Junior Analyst Research Tasks (per investigation)

1. Industry fraud patterns for the case type + sector
2. Regulatory requirements triggered by the case type
3. Sanctions checks on all named individuals and entities
4. Company ownership / corporate registry lookups on involved entities
5. Regulatory implications — what reporting obligations apply

---

## Investigation Report Structure

Standard sections in a final investigation report:

1. **Executive Summary** — key findings, conclusion, recommendations
2. **Scope & Methodology** — what was investigated, how, limitations
3. **Background** — client context, timeline, parties involved
4. **Findings** — numbered findings with evidence, risk rating
5. **Regulatory Implications** — applicable rules, breach assessment, reporting obligations
6. **Recommendations** — remediation actions, control improvements
7. **Appendices** — evidence index, citations, interview schedule

---

## UAE Regulatory Context for Investigations

| Regulator | Scope in Investigations |
|-----------|------------------------|
| CBUAE | AML investigations — licensed banks and financial institutions |
| DFSA | DIFC-regulated entities — AML and market misconduct |
| SCA | Capital markets fraud, insider trading, market manipulation |
| ADGM / FSRA | ADGM-licensed firms — financial crime and misconduct |

Different investigation types trigger different regulatory reporting obligations. The Partner agent validates regulatory sign-off before approval.

---

## Methodology Notes

- **Evidence chain of custody** — all evidence must be documented from source to report
- **Limitations disclosure** — report must state what was NOT reviewed and why
- **Attribution standard** — findings based on balance of probabilities (civil) or beyond reasonable doubt (criminal referral)
- **Regulatory citations** — only authoritative sources (CBUAE, DFSA, SCA, ADGM) may be cited in regulatory implications section; general web sources flagged as "general" not "authoritative"

---

## Case Output Files

```
cases/{case_id}/
├── state.json                    # Current case status
├── audit_log.jsonl               # Every decision, timestamped
├── citations_index.json          # All sources cited
├── junior_output.v1.json         # JuniorDraft schema
├── pm_review.v1.json             # RevisionRequest or approval
├── partner_approval.v1.json      # ApprovalDecision schema
├── final_report.en.md            # Full report in English
└── final_report.ar.md            # Arabic version
```
