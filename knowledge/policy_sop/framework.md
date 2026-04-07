---
file: knowledge/policy_sop/framework.md
quality_tier: B
last_reviewed: 2026-04-07
reviewer: session-011
open_claims: 2
policy_type_scope: reporting_policy (whistleblower, speak-up, fraud hotline) — see POLICY TYPE APPLICABILITY below
---

# Policy / SOP Knowledge File — GoodWork Forensic AI
# KF-00 — Priority 1 knowledge file

<!-- Sources: knowledge/policy_sop/sources.md — see that file for full URLs and document titles -->

---

## HOW TO USE THIS FILE

This file is loaded by `workflows/policy_sop.py` into the Junior Analyst system prompt.
It defines content requirements for Policy/SOP deliverables.

**Claim labels used throughout this file:**
- `[LAW — instrument]` — statutory or regulatory requirement; cite the instrument
- `[BEST_PRACTICE — source]` — industry or professional standard; deviation is defensible but document it
- `[PRODUCT_RULE]` — a rule enforced by this tool; Maher can override
- `[ADVISORY]` — recommended but not required; based on professional judgment or common practice

Sections marked **MANDATORY (reporting_policy)** apply to whistleblower, speak-up, and fraud
hotline policies. See POLICY TYPE APPLICABILITY table below for other policy types.

---

## POLICY TYPE APPLICABILITY

<!-- Sources: BA-012 architect decision 2026-04-07 -->

[PRODUCT_RULE] The model infers policy type from the policy name and description at intake.
If type is ambiguous, the model asks one clarifying question before classifying.

Policy types recognised by this tool:

| Type | Examples |
|------|---------|
| `reporting_policy` | Whistleblower Policy, Speak-Up Policy, Fraud Hotline Policy |
| `compliance_policy` | Anti-Bribery & Corruption (ABC), AML, Data Protection Policy |
| `operational_policy` | Procurement Policy, IT Acceptable Use, Finance Procedures |
| `hr_policy` | Disciplinary Policy, Performance Management, Code of Conduct |

Section applicability by policy type:

| Section | reporting_policy | compliance_policy | operational_policy | hr_policy |
|---------|-----------------|------------------|--------------------|-----------|
| 1. Anonymous Complaint Handling | MANDATORY | Conditional | Not applicable | Conditional |
| 2. Retaliation Mechanism | MANDATORY | Conditional | Not applicable | Mandatory |
| 3. Evidence Chain of Custody | MANDATORY | Conditional | Conditional | Not applicable |
| 4. SLA for Closure Comms | MANDATORY | Conditional | Not applicable | Conditional |
| 5. Malicious vs Good-Faith | MANDATORY | Not applicable | Not applicable | Not applicable |
| 6. Data Protection Integration | Conditional (jurisdiction) | MANDATORY | Conditional | Conditional |
| 7. Vendor Enforcement | Conditional | MANDATORY | MANDATORY | Not applicable |
| 8. Audit Committee KPIs | Conditional | MANDATORY | Not applicable | Not applicable |

---

## CONTENT REQUIREMENTS

### 1. Anonymous Complaint Handling Protocol
**Applies to:** `reporting_policy` (mandatory); `hr_policy`, `compliance_policy` (conditional)

<!-- Sources: ISO 37001:2016 §8.9; SEBI Circular CIR/CFD/CMD1/168/2019; FCA SYSC 18 -->

[PRODUCT_RULE] Every reporting policy must specify at least one named anonymous submission mechanism — a hotline number, a third-party platform, a dedicated email address, or a sealed envelope procedure. Saying "anonymous reports are accepted" without naming the mechanism is insufficient for this tool's quality standard.

[BEST_PRACTICE — ISO 37001:2016 §8.9] Anti-bribery management systems should permit anonymous reporting. The reporting mechanism should be designed to encourage use.

[LAW — SEBI Circular CIR/CFD/CMD1/168/2019] Indian-listed entities must provide an anonymous reporting mechanism for employees and directors.

[ADVISORY — FCA SYSC 18] ADGM- and DIFC-incorporated entities regulated by the DFSA or operating under FCA-equivalent standards should align their anonymous reporting channels with FCA SYSC 18 requirements, though no UAE-onshore legal mandate requires this.

**Content checklist for this section:**
- Named mechanism for anonymous submission
- How information-poor anonymous complaints are triaged (insufficient detail → what happens?)
- Whether anonymous reporters can receive status updates and how
- Explicit commitment that no attempt is made to identify the anonymous reporter

[ADVISORY] Anonymous data by definition carries no data subject rights (UAE PDPL, DPDP Act). Verify that the submission mechanism genuinely anonymises before the report reaches the investigator — pseudonymous is not the same as anonymous.

---

### 2. Retaliation Investigation Mechanism + Disciplinary Matrix
**Applies to:** `reporting_policy`, `hr_policy` (mandatory); `compliance_policy` (conditional)

<!-- Sources: Federal Decree-Law No. 33 of 2021; POSH Act 2013; ACFE Professional Standards -->

**a. Retaliation definition**

[PRODUCT_RULE] The policy must define retaliation with a specific, non-exhaustive list of acts — not just a general statement. Examples to include: termination, demotion, reassignment, exclusion from meetings, negative performance reviews, withdrawal of development opportunities, social ostracism. A general prohibition without examples is weaker than a defined list.

[ADVISORY] In practice, vague retaliation clauses are harder to enforce and harder for employees to recognise as protections. Specificity serves both the employer (clear standard) and the employee (knows what is prohibited).

**b. Retaliation investigation procedure**

[PRODUCT_RULE] The policy must state who investigates a retaliation complaint and confirm that this person is independent from the investigator of the original complaint.

[ADVISORY] Common standard: retaliation investigations are handled by HR, Legal, or an external investigator, separate from the underlying complaint. Investigate the retaliation allegation with the same methodology as the original complaint.

**c. Disciplinary matrix**

[PRODUCT_RULE] Include a consequence table for substantiated retaliation. Suggested starting point (Maher adapts to client's existing HR framework):

| Severity | Examples | Consequence |
|----------|----------|-------------|
| Minor | Single exclusion from meeting | Written warning |
| Moderate | Negative review, reassignment | Final written warning or demotion |
| Serious | Termination, threat, sustained campaign | Dismissal for cause |

**Why this matters**

[ADVISORY] Practitioners and employment lawyers commonly advise that a policy prohibiting retaliation without a credible investigation mechanism and defined consequences is difficult to enforce and may not provide the employer a meaningful defence in dispute resolution. This is practical guidance, not a statement of case law — specific court authority is not cited here.

[LAW — Federal Decree-Law No. 33 of 2021, Art. 47] UAE onshore: an employer may not terminate an employee for filing a complaint with the Ministry of Human Resources and Emiratisation. Courts have awarded reinstatement and compensation in substantiated cases.

[LAW — POSH Act 2013] India: applies to gender-based harassment complaints; retaliation against complainants is prohibited. Private sector analogue for other complaint types: SEBI requirements for listed entities.

[BEST_PRACTICE — ACFE Professional Standards] Investigations into retaliation should be treated with the same rigour and independence as the original allegation.

---

### 3. Evidence Handling, Forensics, and Chain of Custody
**Applies to:** `reporting_policy` (mandatory); `compliance_policy`, `operational_policy` (conditional)

<!-- Sources: ACFE Fraud Examiners Manual; Federal Law No. 10 of 1992; Indian Evidence Act 1872; Federal Law No. 5 of 2012 -->

**a. Document preservation**

[PRODUCT_RULE] The policy must specify: (1) what triggers a preservation directive; (2) who issues it; (3) which documents and data are covered; (4) consequences for destruction after notice.

[ADVISORY] Common trigger: a complaint is received, or a formal investigation is opened. Preservation notices typically cover all documents related to the subject matter, including email, file systems, messaging platforms, and financial records from the relevant period.

**b. Digital evidence handling**

[BEST_PRACTICE — ACFE Fraud Examiners Manual] Digital evidence should be collected by or under the supervision of a qualified forensic professional. Unmanaged collection risks destroying metadata and may affect the usefulness of the evidence in proceedings.

[ADVISORY] Screenshots taken by non-specialists may face challenges in formal proceedings because they do not preserve file metadata and are relatively easy to alter. Where evidence integrity matters, forensic imaging or equivalent procedures are preferred. This is practical guidance — admissibility rules vary by jurisdiction and proceeding type.

[ADVISORY] Collecting files by copy-paste destroys modification timestamps. If evidence may be needed in proceedings, use write-blocking tools and document the collection process.

**c. Physical evidence**

[BEST_PRACTICE — ACFE Fraud Examiners Manual] Chain of custody log: record who collected the item, when, from where, and in whose presence. Store originals securely; use copies for working purposes.

**d. Interview records**

[BEST_PRACTICE — ACFE Fraud Examiners Manual] Document investigative interviews contemporaneously. Offer the interviewee the opportunity to review and sign their summary statement.

[LAW — Federal Law No. 5 of 2012 (UAE Cybercrime Law), Art. 21] Recording a person without their knowledge or consent may constitute a privacy offence in the UAE. Obtain explicit consent before audio or video recording any interview.

**e. Privilege**

[ADVISORY] Determine at the outset of an investigation whether legal professional privilege applies to any documents. Privileged documents should be clearly marked and kept separate; the investigator should not review them without counsel present. Privilege rules vary by jurisdiction and proceeding type — seek legal advice if proceedings are anticipated.

[LAW — Federal Law No. 10 of 1992 (UAE Evidence Law)] Governs admissibility of documentary evidence in civil and commercial transactions.

[LAW — Indian Evidence Act 1872, §§65A-65B] Conditions for admissibility of electronic records in Indian courts, including certification requirements.

[LAW — DIFC Courts Rules of Court, Order 24] Disclosure obligations: preserved documents must be producible in original form.

---

### 4. SLA for Closure Communication to Whistleblower / Reporter
**Applies to:** `reporting_policy` (mandatory); `hr_policy`, `compliance_policy` (conditional)

<!-- Sources: FCA SYSC 18; practitioner common practice -->

[PRODUCT_RULE] Every reporting policy drafted by this tool must specify SLA timelines for acknowledgement, status updates, and closure. A policy that describes a process without SLAs cannot be monitored for compliance.

[ADVISORY — practitioner common practice] The following SLAs are commonly used in mid-size organisations. Adjust based on client size, regulatory context, and investigative capacity:

- **Acknowledgement:** 3–5 business days from receipt
- **Triage decision** (investigate or dismiss with rationale): 10–15 business days
- **Status updates during investigation:** every 30 days
- **Closure communication:** within 5 business days of investigation close

[ADVISORY] For anonymous reporters: a general outcome notice (e.g. intranet update, periodic bulletin) allows the reporter to know the complaint was acted on without identifying them.

[ADVISORY] The most common reason whistleblowers go external (regulator, media) is the perception that nothing happened internally. SLA compliance and closure communication directly address this risk — this is practitioner observation, not empirically cited research.

[LAW — FCA SYSC 18] UK FCA-regulated firms must have procedures for handling whistleblowing disclosures, including timely acknowledgement. Specific SLA days are not mandated by the FCA — the standard is "appropriate."

---

### 5. Malicious vs Good-Faith Complaint — Precise Definition
**Applies to:** `reporting_policy` (mandatory only)

<!-- Sources: UK Employment Rights Act 1996 s.43B; DIFC Employment Law 2019 Art. 59 -->

[PRODUCT_RULE] Any reporting policy that includes disciplinary consequences for malicious complaints must define both "good faith" and "malicious" with precision. Imprecise definitions risk suppressing legitimate reporting and may create enforcement difficulties.

**Good-faith reporting**

[LAW — UK Employment Rights Act 1996 s.43B (PIDA)] A disclosure is protected if the worker reasonably believed the information disclosed was substantially true and was made in the public interest. The disclosure does not need to be correct — reasonable belief is the standard.

[ADVISORY — derived from PIDA standard, widely adopted in policy practice] A complaint is made in good faith if the reporter: (a) genuinely believed the reported conduct was improper at the time of reporting, AND (b) had a reasonable basis for that belief. An unsubstantiated complaint is not automatically malicious.

**Malicious complaint**

[ADVISORY] A complaint is malicious only if the reporter: (a) knew the reported conduct had not occurred, OR was reckless as to whether it had, AND (b) made the report to cause harm or gain personal advantage. The burden of establishing malice sits with the employer.

[ADVISORY] Overly broad malicious-complaint clauses — ones that do not clearly separate "wrong" from "malicious" — risk creating a chilling effect on legitimate reporting and may attract regulatory or legal scrutiny in jurisdictions with whistleblower protection frameworks. This is practitioner guidance; specific case authority is not cited here. (open_claim: 1 of 2)

**Disciplinary action for malicious complaints**

[PRODUCT_RULE] The policy must state that: (1) malice must be separately proven; (2) the investigation into alleged malice is conducted separately from the original complaint investigation; (3) no adverse action is taken against the reporter while the malice determination is pending.

[LAW — DIFC Employment Law 2019, Art. 59] DIFC-incorporated entities: whistleblower protections apply; the malice standard is implicit in the protection framework.

[BEST_PRACTICE — ACFE] Malicious report discipline is permissible only where malice is separately established through a rigorous, independent process — not inferred from an unsubstantiated complaint outcome.

---

### 6. Data Protection Integration
**Applies to:** conditional on jurisdiction (see table); `compliance_policy` (mandatory)

<!-- Sources: DPDP Act 2023; Federal Decree-Law No. 45 of 2021; DIFC Law No. 5 of 2020; UK GDPR -->

[PRODUCT_RULE] This section is generated when: (a) client operates in India, (b) client is DIFC/ADGM-incorporated, or (c) client processes EU data subject personal data. The model identifies the applicable sub-sections from intake jurisdiction data.

**India — DPDP Act 2023**

[LAW — Digital Personal Data Protection Act 2023, §§4-8] Personal data may be processed only for a lawful purpose, with consent or on a legitimate basis. Individuals have rights to access, correction, and erasure of their personal data.

[LAW — DPDP Act 2023, §9] A "Data Fiduciary" (the entity processing data) must implement reasonable security safeguards. The policy must name who is the Data Fiduciary for complaint data.

[ADVISORY] Tension: a respondent's erasure right vs. the organisation's audit trail obligation. Recommended approach: maintain investigation records for 7 years regardless of erasure requests; a legal hold overrides the erasure right during an active investigation. Verify this with legal counsel — the DPDP Act's interaction with evidentiary retention requirements is not yet settled by regulation or case law. (open_claim: 2 of 2)

[LAW — DPDP Act 2023, §5] Cross-border personal data transfers are subject to restrictions on prescribed countries (list to be notified by the Central Government). If investigation data is transferred to a parent company or external firm outside India, confirm compliance with current prescribed country list.

**UAE — PDPL**

[LAW — Federal Decree-Law No. 45 of 2021 (PDPL)] Data subjects have rights of access, correction, and erasure. The same audit trail vs. erasure tension applies; retain investigation records under a legal hold and document the basis.

**DIFC**

[LAW — DIFC Data Protection Law 2020 (DIFC Law No. 5 of 2020)] Applies to DIFC-incorporated entities. Data controller obligations, data subject rights, and transfer restrictions apply.

**UK / EU**

[LAW — UK GDPR / EU GDPR] Strict consent and transfer requirements. Lawful basis for processing respondent data without consent: legitimate interests or compliance with a legal obligation (document the basis).

**Privacy notice**

[PRODUCT_RULE] A short privacy notice must be included in the policy (or referenced as a separate document) for the point of complaint submission. Minimum content: what data is collected, why, retention period, who processes it, data subject rights, how to exercise them.

---

### 7. Vendor and Third-Party Enforcement Mechanism
**Applies to:** `compliance_policy`, `operational_policy` (mandatory); `reporting_policy` (conditional)

<!-- Sources: UK Bribery Act 2010; ISO 37001:2016 §6.1.2; UAE Federal Law No. 4 of 2012 -->

**Scope of coverage**

[PRODUCT_RULE] The policy must explicitly state which third parties are covered (suppliers, contractors, agents, JV partners, distributors). A policy silent on vendors provides no contractual basis for enforcement against them.

**Contractual basis**

[BEST_PRACTICE — ISO 37001:2016 §6.1.2] Due diligence on business associates, including contractual anti-bribery obligations, is a core requirement of an anti-bribery management system. The same principle extends to fraud reporting and compliance policies.

[LAW — UK Bribery Act 2010, §7] The "adequate procedures" defence requires that the organisation has taken proportionate steps to prevent bribery throughout its supply chain. Vendor contract clauses are a standard component.

[ADVISORY — ACFE Report to the Nations] Approximately 20% of fraud schemes involve collusion with third parties. Vendor coverage is not merely a compliance exercise — it addresses a material fraud risk. (Source: ACFE Report to the Nations — specific year edition cited in sources.md.)

**Reporting mechanism for third parties**

[PRODUCT_RULE] The policy must state that third parties (vendors, contractors) have a way to report concerns and receive equivalent protection from retaliation as internal employees, to the extent the firm can contractually enforce this.

**Consequence for vendors**

[ADVISORY] Standard practice: suspend a vendor pending investigation of a substantiated complaint; terminate the contract if the complaint is substantiated. The policy should also protect vendors who themselves report misconduct from retaliatory contract termination.

[LAW — UAE Federal Law No. 4 of 2012 (Anti-Corruption Law), Art. 10] Applicable to private sector dealings involving public officials; relevant when vendor relationships involve government counterparties.

---

### 8. Metrics and KPI Reporting Framework for Audit Committee
**Applies to:** `compliance_policy` (mandatory); `reporting_policy` (conditional); `operational_policy` (not applicable)

<!-- Sources: ISO 37001:2016 §9.1; FCA SYSC 18; SEBI Listing Obligations 2015 -->

[PRODUCT_RULE] Every policy that governs investigations must specify who prepares the metrics report, who receives it, and at what frequency. A policy without a reporting framework cannot be audited for effectiveness.

**Minimum metrics set**

| Metric | Frequency | Notes |
|--------|-----------|-------|
| Total complaints received | Quarterly | By category (fraud, misconduct, harassment, safety, other) |
| Anonymous vs named split | Quarterly | Tracks reporter confidence in the system |
| Investigated vs dismissed at triage | Quarterly | High dismissal rate = policy credibility risk |
| Cases open > 60 days | Quarterly | Tracks investigation velocity |
| Cases closed with substantiation | Quarterly | Include outcome type: dismissal, warning, process change |
| Retaliation complaints received | Quarterly | Red flag metric — should be near zero |
| Median + 90th percentile time to closure | Annually | Measure against SLA targets |
| % reporters who received closure communication | Annually | SLA compliance |

[BEST_PRACTICE — ISO 37001:2016 §9.1] Top management must review the anti-bribery management system at planned intervals, including performance data. The same principle applies to any compliance framework.

[LAW — FCA SYSC 18.4] UK FCA-regulated firms: the whistleblowing champion must report to the Board annually on the operation of the firm's whistleblowing arrangements. The FCA receives a separate annual return.

[LAW — SEBI Listing Obligations and Disclosure Requirements Regulations 2015, Regulation 22] Listed entities in India must establish a vigil mechanism and disclose in the Annual Report the number of complaints received and disposed of.

**Reporting structure**

[PRODUCT_RULE] Report is prepared by: CCO, HR Director, or Ethics Officer. Recipients: Audit Committee + CEO + Board. Format: written. Line management receives aggregate data only — individual case details are restricted.

**Trend interpretation**

[ADVISORY] Year-over-year comparison is required — a single-period snapshot cannot identify trends. A material decline in complaint volume should be investigated (possible chilling effect), not treated as a success metric. A spike in a category should trigger a thematic root cause review.

[ADVISORY — ACFE Report to the Nations 2024] Organisations with hotlines report fraud losses approximately 50% lower than those without. The specific percentage varies by edition — verify against the current year report before citing to a client. (Cited in sources.md.)

---

## ZERO-INFORMATION MODE

<!-- Sources: BA-004 (zero-info content floor definition) -->

[PRODUCT_RULE] When Maher provides minimal intake (jurisdiction, organisation type, rough size only), the model:
1. Generates all applicable mandatory sections with jurisdiction-appropriate regulatory references
2. Populates tables with the standard SLAs and metrics above as starting content
3. Labels each section `[BASELINE — review and adapt to client]`
4. Generates an `open_questions` list for Maher to gather from the client:
   - Existing reporting mechanism (hotline, email, in-person)?
   - Current vendor contract template?
   - Any prior complaints or investigations on record?
   - Named Ethics Officer / Compliance Officer?
   - Regulatory filings already being made (SEBI, FCA, etc.)?

---

## REGULATORY REFERENCE TABLE

| Jurisdiction | Key Instruments | Regulator |
|---|---|---|
| UAE (onshore) | Federal Decree-Law 33/2021 (Labour), Federal Law 4/2012 (Anti-Corruption), Federal Law 45/2021 (PDPL) | MoHRE, Attorney General |
| DIFC | DIFC Employment Law 2019, DIFC Data Protection Law 2020 (Law 5/2020) | DIFC Courts, Commissioner of Data Protection |
| ADGM | ADGM Employment Regulations 2019, ADGM Data Protection Regulations 2021 | ADGM Courts, Registration Authority |
| India | POSH Act 2013, Whistle Blowers Protection Act 2014, SEBI Circular 2019, DPDP Act 2023 | SEBI (listed entities), IRDAI (insurance), RBI (banking) |
| UK | Employment Rights Act 1996 (PIDA), UK Bribery Act 2010, UK GDPR | FCA, ICO |
| International | ISO 37001:2016 (ABC), ACFE Professional Standards, OECD Anti-Bribery Convention | N/A — voluntary standards |

---

## OPEN CLAIMS (2)

1. **Section 5** — "overly broad malicious-complaint clauses risk attracting regulatory or legal scrutiny" — labelled [ADVISORY]; specific case authority not cited. Acceptable at tier B. Requires specific case citation to reach tier A.
2. **Section 6 / DPDP Act** — interaction between DPDP erasure right and evidentiary retention is not settled by regulation or case law as of 2026. Verify with legal counsel before advising a client. Flagged [ADVISORY].

---

## SOURCES FILE

See `knowledge/policy_sop/sources.md` for full citation list with URLs, document titles, and retrieval guidance.
