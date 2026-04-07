# Policy / SOP Knowledge File — GoodWork Forensic AI
# KF-00 — Priority 1 knowledge file
# Session: 011 (2026-04-07) | Origin: junior-dev build from BA-004 + lessons.md Session 009
#
# Purpose: Inject this knowledge into the policy_sop workflow system prompt to close the
# 8 quality gaps identified in the external ChatGPT review of the Whistleblower Policy
# generated in Session 009. These gaps were present in every policy/SOP generated before
# this file existed. After this file is loaded, the junior agent must include all 8 sections.

---

## HOW TO USE THIS FILE

This file is loaded by `workflows/policy_sop.py` into the Junior Analyst system prompt.
It defines mandatory content requirements for all Policy/SOP deliverables.
The Junior Analyst must treat every item marked **MANDATORY** as a required section.
Items marked **CONDITIONAL** are required only when the stated condition is true.

---

## MANDATORY CONTENT REQUIREMENTS

### 1. Anonymous Complaint Handling Protocol [MANDATORY]

Every whistleblower / speak-up / reporting policy must specify:
- The exact mechanism for anonymous submission (dedicated hotline, third-party platform,
  sealed envelope procedure — at least one method must be named specifically)
- How anonymous complaints are triaged when the investigator cannot follow up for clarification
- Whether anonymous reporters can receive status updates and, if so, how
- What happens if an anonymous complaint lacks sufficient detail to investigate
- The organisation's commitment that no attempt will be made to identify anonymous reporters

**Common failure mode:** Policies that say "anonymous reports are accepted" without describing
the mechanism or the triage procedure for information-poor anonymous reports.

**Regulatory grounding:**
- UAE: No specific requirement but ADGM/DIFC-incorporated entities should align with
  FCA Handbook (SYSC 18) which requires appropriate anonymous reporting channels
- India: SEBI Circular CIR/CFD/CMD1/168/2019 (listed entities must have anonymous reporting)
- UK GDPR / UAE PDPL: Anonymous data by definition has no data subject rights — confirm
  the mechanism truly anonymises before the report reaches the investigator
- International: ISO 37001:2016 §8.9 — reporting mechanisms should permit anonymous reports

---

### 2. Retaliation Investigation Mechanism + Disciplinary Matrix [MANDATORY]

Every policy must include:

**a. Retaliation definition:** A specific, non-exhaustive list of acts that constitute retaliation —
e.g. termination, demotion, reassignment, exclusion from meetings, negative performance reviews,
withdrawal of development opportunities, social ostracism. Vague language ("we do not tolerate
retaliation") without examples is insufficient.

**b. Retaliation investigation procedure:** Who investigates a retaliation complaint? The
standard: the investigator of the original complaint must not investigate the retaliation
allegation (conflict of interest). Procedure should specify:
- Who receives the retaliation complaint
- Who is appointed to investigate it (independent of original complaint investigator)
- Timeline for investigation and outcome
- Interim protective measures available to the reporter while investigation is underway

**c. Disciplinary matrix:** A table specifying consequences for substantiated retaliation:

| Severity | Examples | Consequence |
|----------|----------|-------------|
| Minor | Single exclusion from meeting | Written warning |
| Moderate | Negative review, reassignment | Final written warning or demotion |
| Serious | Termination, threat, sustained campaign | Dismissal for cause |

**Why this matters:** Courts in the UAE (DIFC), UK, and India have ruled that a policy
prohibiting retaliation without a credible investigation mechanism and defined consequences
is considered illusory and does not provide the employer a defence. A policy stating only
"retaliation is prohibited" is legally insufficient.

**Regulatory grounding:**
- UAE Labour Law (Federal Decree-Law No. 33 of 2021): Art. 47 — employer may not terminate
  an employee for filing a complaint; courts have awarded reinstatement + compensation
- India: POSH Act 2013 (applicable to gender harassment); Whistle Blowers Protection Act 2014
  (central government employees) — private sector analogue via SEBI requirements for listed entities
- ACFE Code of Ethics: investigations into retaliation must be treated with same rigour as
  original allegation

---

### 3. Evidence Handling, Forensics, and Chain of Custody [MANDATORY]

Every policy that governs investigations (whistleblower, fraud, misconduct) must include:

**a. Document preservation order:** From the moment a complaint is received, what documents
and data must be preserved? Who issues the preservation directive? What are the penalties
for destruction of evidence?

**b. Digital evidence handling:**
- Email, chat, and file system evidence must be collected by or under the supervision of a
  qualified forensic professional or external forensic firm
- Screenshots taken by non-specialists are NOT admissible as primary evidence in most
  jurisdictions — the policy should state this and prescribe when forensic collection is required
- Metadata preservation: collecting files by copy-paste destroys metadata; the policy must
  require forensic imaging or equivalent

**c. Physical evidence handling:**
- Chain of custody log: who collected it, when, from where, in whose presence
- Secure storage: locked cabinet with access log
- No original documents to be marked, annotated, or removed from evidence store

**d. Interview records:**
- All investigative interviews to be documented contemporaneously
- Interviewee to be offered opportunity to review and sign their statement
- Audio/video recording only with consent (UAE: recording without consent may constitute
  criminal breach of privacy under Federal Law No. 5 of 2012 on Combatting Cybercrimes)

**e. Evidence classification:**
- Who determines what is privileged (legal professional privilege / attorney-client privilege)?
- Privileged documents must be clearly marked; investigator must not review without counsel present

**Regulatory grounding:**
- ACFE Fraud Examiners Manual: evidence chain of custody requirements
- DIFC Courts: Rules of Court Order 24 (disclosure obligations in litigation — preserved
  documents must be producible in original form)
- UAE Federal Law on Evidence in Civil and Commercial Transactions (Federal Law No. 10 of 1992)
- India: Indian Evidence Act 1872 (electronic records — Sections 65A, 65B for admissibility)

---

### 4. SLA for Closure Communication to Whistleblower / Reporter [MANDATORY]

Every policy must specify:
- Initial acknowledgement: within how many business days of receiving the complaint
- Status update: at what intervals during a long investigation (common: every 30 days)
- Closure communication: notification to reporter when the investigation is concluded
  (even if outcome is confidential — "the matter has been investigated and appropriate
  action has been taken" is sufficient)
- Where the reporter is anonymous: mechanism for posting a general outcome notice
  (e.g. intranet update) so the reporter can know the complaint was acted on

**Why this matters:** The single most common reason whistleblowers go external (regulator,
media) rather than internal is the perception that nothing happened. A documented SLA with
actual notifications closes this gap.

**Standard SLAs (adapt to organisation size):**
- Acknowledgement: 3–5 business days
- Initial triage decision (investigate / dismiss): 10–15 business days
- Status update intervals (during investigation): 30 days
- Closure communication: within 5 business days of investigation close

---

### 5. Malicious vs Good-Faith Complaint — Legally Precise Definition [MANDATORY]

This section must be drafted with precision. Imprecision creates legal exposure.

**Good-faith reporting:**
A complaint is made in good faith if the reporter:
(a) Genuinely believed the reported conduct was improper at the time of reporting, AND
(b) Had a reasonable basis for that belief (not purely speculative or fabricated)

Good faith does NOT require the complaint to be correct or for an investigation to
confirm wrongdoing. A complaint that is investigated and found unsubstantiated is not
thereby malicious.

**Malicious complaint:**
A complaint is malicious only if the reporter:
(a) Knew the reported conduct had not occurred, OR
(b) Was reckless as to whether it had occurred, AND
(c) Made the report to cause harm to the named individual or to gain personal advantage

**Why this matters:** A policy that says "malicious complainants will face disciplinary action"
without the above precision is legally dangerous. Courts and regulators have found that
overly broad malicious-complaint clauses suppress legitimate reporting. The policy must
make clear that a report that turns out to be wrong is not automatically malicious.

**Disciplinary action for malicious complaints:**
- Applies only where malice is separately proven (the burden is on the employer, not the reporter)
- The investigation into alleged malice must be separate from the underlying complaint investigation
- Interim: no adverse action against the reporter until malice finding is final

**Regulatory grounding:**
- UK Employment Rights Act 1996 s.43B (protected disclosures) — good faith standard
- DIFC Employment Law 2019 (Art. 59) — whistleblower protections; malice standard implicit
- ACFE: malicious report discipline is permissible only if rigorously separated from
  substantive complaint outcome

---

### 6. Data Protection Integration [CONDITIONAL — when jurisdiction includes India]

**Mandatory when:** client operates in India (any entity incorporated in India, or processing
personal data of Indian residents).

**DPDP Act 2023 (Digital Personal Data Protection Act) requirements:**

**a. Complaint data as personal data:**
- Complaint submissions contain personal data of both the reporter and the named respondent
- Both are "data principals" under the DPDP Act — both have rights (access, correction, erasure)
- Tension: erasure right of respondent vs. audit trail obligation — policy must address this
  conflict explicitly (recommended: retain investigation records for 7 years regardless of
  erasure requests; legal hold overrides DPDP erasure right during active investigation)

**b. Cross-border data transfers:**
- If the investigation involves transferring data to a parent company or external firm outside India,
  the transfer must comply with DPDP Act transfer restrictions (prescribed countries to be notified)
- Policy must specify: who is the "Data Fiduciary" for complaint data; where data is stored;
  how long it is retained; what deletion procedure applies after retention period

**c. Consent:**
- The reporter's act of submitting a complaint implies consent to processing for investigation purposes
- The named respondent's consent cannot be obtained without revealing the complaint —
  policy must cite the lawful basis for processing respondent's data without consent
  (DPDP Act: legitimate purpose for compliance with applicable law)

**d. Privacy notice:**
- A short privacy notice must be displayed at the point of complaint submission
- Content: what data is collected, why, how long it is retained, who processes it, rights available

**Also consider for all jurisdictions:**
- UAE PDPL (Federal Decree-Law No. 45 of 2021): same data subject rights framework
- DIFC Data Protection Law 2020 (DIFC Law No. 5 of 2020): applies to DIFC-incorporated entities
- GDPR (if EU data subjects involved): strict consent + transfer requirements

---

### 7. Vendor and Third-Party Enforcement Mechanism [MANDATORY]

The policy must address:

**a. Scope of coverage:**
- Which third parties are covered? (suppliers, contractors, agents, JV partners, distributors)
- Coverage must be stated explicitly — a policy that covers employees but is silent on vendors
  provides no contractual basis for enforcement against vendors

**b. Contractual basis:**
- Vendor contracts must contain a clause requiring compliance with the firm's whistleblower /
  anti-fraud policy (or equivalent standards)
- New vendor onboarding: policy compliance clause must be in the standard agreement
- Existing vendors: policy update trigger — when contracts renew, clause is added

**c. Reporting mechanism for third parties:**
- Vendors and contractors must have a way to report concerns about the firm or other vendors
- Dedicated channel (same as internal) or a specific external-facing channel
- The policy must state that third-party reporters have the same protection from retaliation
  as internal employees (to the extent the firm can enforce this)

**d. Consequence for vendors:**
- What happens if a vendor is implicated in a substantiated complaint?
- Typical: immediate suspension pending investigation; termination of contract if substantiated
- Policy should also address what happens if the vendor itself reports misconduct — protection
  from retaliatory contract termination must be explicit

**Regulatory grounding:**
- UK Bribery Act 2010: "adequate procedures" defence requires supply chain controls
- UAE Federal Law No. 4 of 2012 (Anti-Corruption Law): applicable to private sector dealings
- ISO 37001:2016 §6.1.2 — due diligence on business associates is a core requirement
- ACFE Report to the Nations: 20% of fraud schemes involve collusion with third parties

---

### 8. Metrics and KPI Reporting Framework for Audit Committee [MANDATORY]

Every policy that governs investigations must specify a reporting framework:

**a. Metrics to be reported (minimum set):**

| Metric | Frequency | Notes |
|--------|-----------|-------|
| Total complaints received | Quarterly | By category (fraud, misconduct, harassment, safety, other) |
| Anonymous vs named | Quarterly | Tracks reporter confidence in the system |
| Complaints investigated vs. dismissed at triage | Quarterly | High dismissal rate = policy credibility risk |
| Cases open > 60 days | Quarterly | Tracks investigation velocity |
| Cases closed with substantiation | Quarterly | And outcome type: dismissal, warning, process change |
| Retaliation complaints received | Quarterly | Red flag metric — should be near zero |
| Time from complaint to closure (median, 90th pctl) | Annually | Against SLA targets |
| Reporters who received closure communication | Annually | SLA compliance |

**b. Reporting mechanism:**
- Who prepares the report? (typically: Chief Compliance Officer, HR Director, or Ethics Officer)
- Who reviews? (Audit Committee and/or Board — not just management)
- Format: written report, not verbal only
- Restricted distribution: report is restricted to Audit Committee + CEO + Board;
  line management receives only aggregate data

**c. Trend analysis:**
- Year-over-year comparison is required — a single-period snapshot is insufficient
- Material decline in complaint volume: could indicate suppression (chilling effect) —
  must be explained and investigated, not celebrated
- Spike in a category: triggers a thematic review of root causes

**d. No data = a finding:**
- If no complaints were received in a period, the report must still be submitted stating this
- Zero complaints in a large organisation over a full year is a red flag, not a success metric —
  the report should note whether zero-report quarters warrant a culture review

**Regulatory grounding:**
- ACFE Report to the Nations 2024: hotline reporting linked to 50% reduction in fraud losses
- UK Financial Conduct Authority (FCA): SYSC 18 — firms must report whistleblowing data
  to Board; FCA also receives annual whistleblowing champion report
- SEBI (India): listed entities must disclose complaints data in Annual Report
- ISO 37001:2016 §9.1 — monitoring and measurement; top management review requirements

---

## ZERO-INFORMATION MODE

When Maher provides minimal intake (jurisdiction, organisation type, rough size):

1. Generate all 8 mandatory sections above with jurisdiction-appropriate regulatory references
2. Populate tables with the standard SLAs and metrics above as starting content
3. Mark each section with `[BASELINE — review and adapt to client]`
4. Generate an `open_questions` list of what Maher needs from the client to personalise:
   - Existing reporting mechanism (hotline, email, in-person)?
   - Current vendor contract template?
   - Any prior complaints or investigations on record?
   - Named Ethics Officer / Compliance Officer?
   - Regulatory filings the client already makes (SEBI, FCA, etc.)?

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

## SOURCES FILE

See `knowledge/policy_sop/sources.md` for full citation list. This framework file contains
abbreviated references; sources.md contains full URLs, document titles, and retrieval guidance.
