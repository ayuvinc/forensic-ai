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
