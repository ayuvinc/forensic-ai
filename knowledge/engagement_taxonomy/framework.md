---
file: knowledge/engagement_taxonomy/framework.md
quality_tier: B
last_reviewed: 2026-04-07
reviewer: session-011
open_claims: 0
taxonomy_version: 1.0
engagement_types_count: 18
---

<!-- Sources: knowledge/engagement_taxonomy/sources.md -->
<!-- Claim labels: [LAW] [BEST_PRACTICE] [PRODUCT_RULE] [ADVISORY] -->
<!-- AK-confirmed list: session 011 (2026-04-07) — BA-014 confirmations -->

# Forensic Engagement Taxonomy — GoodWork Forensic AI
# KF-NEW | Gates: SCOPE-WF-01 (workflows/engagement_scoping.py)

---

## PURPOSE

[PRODUCT_RULE] This file is the knowledge base for the Engagement Scoping Workflow (SCOPE-WF-01).
When Maher describes a client situation in plain language, the model reads this taxonomy to:
1. Identify the best-fit GoodWork service(s)
2. Propose a structured scope with standard components
3. Route to the correct workflow in run.py / app.py
4. Flag HUMINT, licensed-DB, or deferred-service limitations

**Active GoodWork service lines (AK-confirmed):**
Investigation Report (7 sub-types), FRM Risk Register, Due Diligence Individual,
Due Diligence Entity, Transaction Testing, Sanctions Screening, Policy/SOP,
Training Material, Client Proposal, ABC Programme, Engagement Scoping.

**Excluded from this taxonomy:** Insurance Fraud Investigation, standalone Asset Tracing,
Insolvency Fraud, Expert Witness (deferred), ESI/e-discovery (deferred), HUMINT (deferred).

---

## TAXONOMY ENTRY FORMAT

Each entry follows this structure:
```
### [N]. [Engagement Type Name]
Workflow: [run.py option]
Triggering scenarios: [what client situations lead here]
Standard scope components: [what is always included vs optional]
Typical deliverables: [what Maher produces]
Applicable frameworks: [ACFE/IIA/ISO/UAE regulatory standard]
Common chains: [compatible follow-on engagements per BA-011]
Exclusions: [what this type does NOT cover]
Red flags that escalate: [when to expand to another engagement type]
```

---

## INVESTIGATION REPORT — 7 SUB-TYPES

<!-- Sources: ACFE Fraud Examiners Manual; knowledge/investigation/investigation_framework.md -->

### 1. Investigation Report — Procurement Fraud

**Workflow:** Option 2 (investigation_report.py) | sub_type: procurement_fraud

**Triggering scenarios:**
- Auditors or management identify unusual vendor concentration, duplicate payments, or approvals bypassed
- Whistleblower complaint alleges kickbacks from a specific vendor or vendor group
- Internal controls review reveals split purchase orders or invoices just below approval thresholds
- A vendor fails a due diligence check and the client wants to understand historical transactions

**Standard scope components (always included):**
- Three-way matching test (PO → Invoice → Payment)
- Vendor master analysis (new vendors, duplicate registrations, employee-vendor conflicts)
- Split order / split invoice testing
- Timeline of transactions with flagged vendors
- Interview of procurement, finance, and operations personnel (scope only if HUMINT required)

**Optional components (include if evidence warrants):**
- Conflict of interest register cross-check
- Corporate registry check on vendors in flagged period
- Bank account cross-reference (vendor accounts vs employee accounts)

**Typical deliverables:**
- Investigation Report (Junior → PM → Partner pipeline)
- Evidence schedule (annexure to report)
- Case timeline

**Applicable frameworks:**
[BEST_PRACTICE — ACFE Fraud Examiners Manual] Asset misappropriation scheme classification; three-way match procedure; documentary evidence standards

**Common chains:** → Sanctions Screening (screen flagged vendors); → Client Proposal (remediation engagement); → FRM Risk Register (systemic procurement risk assessment)

**Exclusions:** Financial statement fraud testing (separate sub-type); HUMINT execution (scope only); legal determination of guilt

**Red flags that escalate:**
- Evidence suggests senior management involvement → Partner escalation; consider regulatory reporting scope
- Vendor appears on sanctions list → add Sanctions Screening to scope
- Scope of loss suggests financial statement impact → add Financial Statement Fraud sub-type

---

### 2. Investigation Report — Payroll Fraud

**Workflow:** Option 2 | sub_type: payroll_fraud

**Triggering scenarios:**
- HR or Finance identifies employees receiving salaries who cannot be located or verified
- Anonymous tip alleges a supervisor is adding fictitious employees to the payroll
- External audit flags payroll costs significantly above headcount
- Merger/acquisition due diligence reveals payroll anomalies in the target

**Standard scope components:**
- Ghost employee detection (active vs HR-file cross-check; terminated employee check)
- Pay rate change analysis (changes outside normal HR process)
- Overtime analysis by employee, department, and supervisor
- Bank account cross-reference (multiple employees sharing one account)

**Typical deliverables:** Investigation Report; payroll exceptions schedule; recommended HR control improvements

**Applicable frameworks:** [BEST_PRACTICE — ACFE] Payroll fraud scheme classification; ghost employee indicators

**Common chains:** → FRM Risk Register (payroll fraud risk module); → Client Proposal (HR controls remediation)

**Exclusions:** Full payroll audit (this is a fraud investigation, not a compliance audit); benefits fraud (separate scope)

**Red flags that escalate:** Evidence of systematic ghost employee scheme involving HR and Finance → potential for corruption / collusion; add Procurement Fraud sub-type if vendor payments also involved

---

### 3. Investigation Report — Expense Fraud

**Workflow:** Option 2 | sub_type: expense_fraud

**Triggering scenarios:**
- Finance identifies duplicate expense submissions across periods
- Expense reports significantly above peer comparators for a department or individual
- Whistleblower complaint about a specific employee submitting false expenses
- Policy compliance review reveals systematic policy violations in expense claims

**Standard scope components:**
- Duplicate submission testing (same amount + merchant + close date)
- Round-dollar testing
- Weekend/holiday spend analysis
- Policy compliance check (per-diem limits, prohibited categories, approver independence)

**Typical deliverables:** Investigation Report; exceptions schedule by employee; policy gaps identified

**Applicable frameworks:** [BEST_PRACTICE — ACFE] Expense reimbursement fraud scheme classification

**Common chains:** → Policy/SOP (update expense policy); → Training Material (expense policy refresher)

**Exclusions:** Travel booking fraud (separate scope if suspected); corporate card misuse (extend scope if data available)

---

### 4. Investigation Report — Financial Statement Fraud

**Workflow:** Option 2 | sub_type: financial_statement_fraud

**Triggering scenarios:**
- Auditors identify revenue recognised in a period without delivery evidence
- Board or audit committee suspects management is manipulating earnings (pressure-based)
- Lender or investor requests independent review of financial statements before advancing funds
- Regulatory inquiry into reported financials (SCA, DFSA, SEBI)

**Standard scope components:**
- Journal entry testing (manual entries by senior personnel, period-end, unusual accounts)
- Revenue cut-off testing
- Revenue recognition analysis (shipment dates, customer return patterns)
- Management representation review

**Typical deliverables:** Investigation Report; journal entry exceptions schedule; auditor communication (if applicable)

**Applicable frameworks:** [BEST_PRACTICE — ACFE] Financial statement fraud scheme classification; [BEST_PRACTICE — IFRS / IAS 18 / IFRS 15] Revenue recognition standards relevant to jurisdiction

**Common chains:** → Client Proposal (forensic accounting support for legal proceedings); → Expert Witness (if proceedings anticipated — currently deferred)

**Exclusions:** Full financial audit (this is a forensic investigation, not an audit opinion); HUMINT execution

**Red flags that escalate:** Evidence suggests auditor involvement or awareness → legal counsel required; regulatory reporting may be mandatory (check regulator-specific obligations)

---

### 5. Investigation Report — AML / Financial Crime

**Workflow:** Option 2 | sub_type: aml_financial_crime

**Triggering scenarios:**
- Compliance department flags suspicious transactions for formal investigation
- Regulator requests an independent AML investigation (CBUAE, DFSA, ADGM FSRA)
- Correspondent bank requests AML due diligence on specific customer relationships
- Internal suspicious activity report (SAR) requires formal follow-up investigation

**Standard scope components:**
- Transaction pattern analysis (structuring, layering, velocity anomalies)
- Counterparty analysis (sanctions checks on counterparties)
- Customer risk profile review (PEP, high-risk jurisdiction exposure)
- SAR / STR drafting support (scope and structure; Maher reviews and files)

**Typical deliverables:** Investigation Report; SAR/STR draft (if applicable); regulatory correspondence support

**Applicable frameworks:**
[LAW — CBUAE AML/CFT Standards] For UAE licensed financial institutions
[LAW — DFSA AML Module] For DIFC-authorised entities
[BEST_PRACTICE — FATF Recommendations 20-21] Suspicious transaction reporting obligations

**Common chains:** → Sanctions Screening (screen subjects identified in investigation); → Due Diligence (deeper background on flagged counterparty)

**Exclusions:** Actual SAR filing (Maher files; tool drafts); HUMINT source enquiries

**Red flags that escalate:** Investigation reveals possible terrorist financing → mandatory reporting obligations; require legal counsel immediately

---

### 6. Investigation Report — Whistleblower Complaint

**Workflow:** Option 2 | sub_type: whistleblower_complaint

**Triggering scenarios:**
- Employee submits a formal internal complaint via the speak-up hotline or HR channel
- Anonymous tip received requiring structured investigation
- Board receives a complaint about a C-suite executive (requires independent investigation)
- External whistleblower contacts the company via a regulatory channel

**Standard scope components:**
- Complaint intake and triage (is it in scope? sufficient evidence to investigate?)
- Document review relevant to the complaint allegations
- Interview plan (scope — HUMINT boundary applies to execution)
- Findings structured around the specific allegations raised
- Reporter protection documentation (if reporter is named)

**Typical deliverables:** Investigation Report (calibrated to audience: Board / HR / Legal); interview summaries; evidence schedule

**Applicable frameworks:**
[BEST_PRACTICE — ACFE] Independent investigation standards
[ADVISORY] Board-level complaints require external investigator independence — tool flags this when the subject is a C-suite executive

**Common chains:** → Policy/SOP (update speak-up policy based on findings); → FRM Risk Register (if complaint reveals systemic risk)

**Exclusions:** Determining regulatory whistleblower protections (legal advice); HUMINT execution; formal legal proceedings

**Red flags that escalate:** Complaint involves multiple jurisdictions → regulatory reporting may apply; complaint subject is a regulatory officer → formal reporting obligations

---

### 7. Investigation Report — General / Mixed

**Workflow:** Option 2 | sub_type: general

**Triggering scenarios:**
- Client suspects misconduct but cannot classify the fraud type upfront
- Investigation spans multiple fraud types (e.g. procurement + expense simultaneously)
- Regulatory breach investigation that involves multiple financial and compliance issues

**Standard scope components:** Determined after initial document review and interview scoping; model proposes a phased approach

**Typical deliverables:** Investigation Report structured around findings, not a single typology

**Common chains:** Any compatible chain from BA-011 based on findings

**Red flags that escalate:** As specific fraud types emerge during investigation, consider switching to the relevant sub-type framework

---

## FRM RISK REGISTER

**Workflow:** Option 6 (frm_risk_register.py)

**Triggering scenarios:**
- New client onboarding requires a baseline fraud risk assessment
- Existing client has had an incident and board wants a comprehensive risk review
- Regulator requires demonstration of fraud risk governance (CBUAE, DFSA, SCA)
- Client is preparing for external audit or certification (ISO 37001, ISO 31000)
- Post-merger integration: acquirer wants target's fraud risks assessed

**Standard scope components:**
[PRODUCT_RULE] FRM follows the 8-module structure with module dependency rules:
- Module 1: Fraud Risk Governance & Policy (standalone; scoped at intake)
- Module 2: Fraud Risk Assessment / Risk Register (core; required for Modules 3 and 4)
- Module 3: Control Design (requires Module 2)
- Module 4: Investigation Protocols (requires Module 2)
- Module 5: Whistleblower Hotline Setup (standalone)
- Module 6: Employee Training & Awareness (standalone or after Module 2)
- Module 7: Monitoring & Data Analytics (standalone or after Modules 2 and 3)
- Module 8: Insurance Coverage Recommendations (standalone)

**Guided exercise:** Each module follows the Step 1–5 co-creation loop (BA-002, Sprint-10D)

**Typical deliverables:** FRM Risk Register (.docx + .md); Executive Summary; Regulatory Mapping Appendix

**Applicable frameworks:** [BEST_PRACTICE — ACFE / COSO ERM / ISO 37001:2016]

**Common chains:** → Policy/SOP (Module 1 findings); → Training Material (Module 6); → Client Proposal (implementation support)

**Exclusions:** Implementation of controls (scoped only); internal audit execution; regulatory filing

---

## DUE DILIGENCE — INDIVIDUAL

**Workflow:** Option [DD — new, SL-GATE-01]

**Triggering scenarios:**
- Client is onboarding a new individual in a senior or high-risk role (C-suite, board member)
- Client is entering a business partnership with an individual and wants background verification
- Investment due diligence on an individual investor, promoter, or fund manager
- Employment screening for a sensitive role (finance, compliance, operations)
- Client has received an allegation against an existing employee and wants background context

**Standard scope components (Phase 1 — Standard):**
- Sanctions screening (5 official lists)
- PEP check
- Adverse media review (English and Arabic)
- Corporate affiliation check (known companies the individual directs or owns)

**Optional components (Phase 2 — Enhanced):**
- Deeper corporate mapping (group structure, UBO analysis of affiliated entities)
- Board-ready narrative report
- HUMINT scope definition (execution is manual — ARCH-GAP-02 applies)

**Typical deliverables:** DD Report (Executive Summary → Profile → Methodology → Sanctions → PEP → Adverse Media → Conclusion); Risk Classification (LOW/MEDIUM/HIGH + CLEAR/FLAG)

**Applicable frameworks:** [BEST_PRACTICE — FATF Recommendation 12 (PEPs)] [BEST_PRACTICE — ACFE]

**Common chains:** → Investigation Report (if red flags require deeper investigation); → Sanctions Screening (dedicated deeper screen if PEP or match found); → Client Proposal

**Exclusions:** HUMINT execution (scope only); WorldCheck/WorldCompliance screening (ARCH-GAP-01); Urdu-language adverse media; legal determination of risk

---

## DUE DILIGENCE — ENTITY

**Workflow:** Option [DD — new, SL-GATE-01]

**Triggering scenarios:**
- Client is onboarding a new vendor in a high-risk category (construction, government-facing, financial services)
- Pre-acquisition or pre-investment due diligence on a target company
- JV partner screening before signing a joint venture agreement
- Regulatory requirement to screen a business counterparty

**Standard scope components (Phase 1):**
- Sanctions screening on the entity and named principals (directors, UBOs)
- Beneficial ownership analysis (above 25% threshold or as specified)
- Adverse media review
- Corporate registry check (incorporation, directors, filings)

**Optional (Phase 2 / Enhanced):**
- Group structure corporate mapping
- Regulatory compliance status review
- HUMINT scope definition (manual execution)

**Typical deliverables:** DD Report (Executive Summary → Entity Profile → Methodology → Sanctions → Beneficial Ownership → Adverse Media → Regulatory Compliance → Conclusion)

**Applicable frameworks:** [BEST_PRACTICE — FATF Recommendations 10, 12, 22]; [BEST_PRACTICE — ACFE]

**Common chains:** → Sanctions Screening (deeper screen on flagged principal); → Investigation Report (red flag escalation); → Client Proposal

**Exclusions:** Same as DD Individual; legal opinion on corporate structure

---

## TRANSACTION TESTING

**Workflow:** Option [TT — new, SL-GATE-03]

**Triggering scenarios:**
- Fraud investigation requires quantification of loss through financial data analysis
- Internal audit identifies a control gap and wants testing to determine if fraud occurred
- Regulator mandates testing of transaction monitoring effectiveness
- Pre-acquisition financial integrity review

**Standard scope components:**
- Stage 1: engagement context (5 branches)
- Stage 2: fraud typology selection + testing plan proposal
- SCOPE_CONFIRMED: testing plan locked before document ingestion
- Testing procedures per fraud typology (see knowledge/transaction_testing/framework.md)

**Typical deliverables:** Testing Plan (confirmed at intake) + Transaction Testing Report with exceptions schedule

**Applicable frameworks:** [BEST_PRACTICE — ACFE]; UAE regulatory testing requirements per regulator (CBUAE/DFSA/ADGM/SCA)

**Common chains:** → Investigation Report (fraud confirmed → full investigation); → Client Proposal (remediation engagement)

**Exclusions:** Full financial audit; automated batch testing pipelines; HUMINT execution

---

## SANCTIONS SCREENING

**Workflow:** Option [Sanctions — new, SL-GATE-02]

**Triggering scenarios:**
- Client needs to screen a counterparty before a transaction or relationship
- Compliance department requires batch screening update for existing customer portfolio
- Regulator requests confirmation of sanctions screening procedures
- Investment decision requires sanctions clearance on target or its principals

**Standard scope components:**
- 5 official list screening (OFAC, UN, EU, UK OFSI, UAE Local)
- PEP check (if in scope)
- Adverse media (if in scope)
- False positive analysis on all potential matches

**Typical deliverables:** Clearance Memo or Full Screening Report (per intake Q10)

**Applicable frameworks:** [BEST_PRACTICE — FATF Recommendations 6, 12]; UAE regulatory AML standards

**Common chains:** → Due Diligence (deeper background if PEP or match found); → Investigation Report (match confirmed → escalate)

**Exclusions:** WorldCheck/WorldCompliance screening (ARCH-GAP-01); batch automated monitoring; legal sanctions determination

---

## POLICY / SOP

**Workflow:** Option 4 (policy_sop.py)

**Triggering scenarios:**
- Client lacks a formal policy in a required area (whistleblower, ABC, AML, data protection)
- Regulator or auditor has flagged policy gaps
- Existing policy is outdated and needs a refresh
- Post-investigation: findings reveal a policy gap that contributed to the fraud

**Standard scope components (reporting_policy type):**
- All 8 mandatory sections per knowledge/policy_sop/framework.md
- Jurisdiction-appropriate regulatory references
- SLAs, disciplinary matrix, vendor enforcement, metrics table
- Companion document suggestion at end of intake

**Typical deliverables:** Policy document (.docx + .md); regulatory reference appendix

**Applicable frameworks:** [BEST_PRACTICE — ISO 37001:2016]; jurisdiction-specific laws per knowledge/policy_sop/framework.md

**Common chains:** → Training Material (communicate the policy); → FRM Risk Register (Module 1 alignment)

**Exclusions:** Policy implementation; board approval process; legal review of final policy (Maher or client counsel)

---

## TRAINING MATERIAL

**Workflow:** Option 5 (training_material.py)

**Triggering scenarios:**
- Policy has been updated and staff need to be informed
- FRM identifies training gaps (Module 6)
- Client requires annual compliance training as part of regulatory requirement
- Post-incident: staff awareness training required as remediation measure

**Standard scope components:**
- Learning objectives
- Content modules calibrated to audience (staff / manager / board)
- UAE / jurisdiction-specific regulatory context
- Quiz or knowledge check questions

**Typical deliverables:** Training material (.docx + .md); facilitator notes; quiz questions

**Common chains:** → Policy/SOP (if no policy exists yet — draft policy first, then training)

**Exclusions:** Facilitation delivery; e-learning platform integration; training tracking system

---

## CLIENT PROPOSAL

**Workflow:** Option 7 (client_proposal.py)

**Triggering scenarios:**
- Prospect has described a problem and Maher wants to submit a formal proposal
- Existing client requires a proposal for a new engagement scope
- RFP response required

**Standard scope components:**
- 7-section structure: Cover, Executive Summary, Background & Understanding, Scope of Work, Methodology, Team & Credentials, Fees + T&C
- Firm credentials selected from firm_profile/ based on proposal scope
- Pricing from firm_profile/pricing_model.json (model-confirmed at intake)

**Typical deliverables:** Proposal (.docx + .md)

**Common chains:** → Proposal Deck (Option 8 — PPT prompt pack); offered at end of proposal workflow

**Exclusions:** Contract negotiation; legal review of T&C; client signature management

---

## ABC PROGRAMME

**Workflow:** Option 4 (policy_sop.py) for standalone ABC policy; Option 6 (frm_risk_register.py, Module 1) for FRM-bundled ABC

**Note (AK-confirmed, session 011):** ABC Programme can be delivered standalone (client needs an ABC policy and programme only) or as part of FRM Module 1 (Governance & Policy). Both delivery paths are valid.

**Triggering scenarios:**
- Client needs to establish an Anti-Bribery & Corruption programme (UK Bribery Act compliance, ISO 37001, regulatory requirement)
- Client's procurement or sales function has high-risk counterparties requiring ABC controls
- Post-acquisition: acquirer requires target to implement ABC programme
- FRM engagement identifies ABC control gaps (Module 1 output)

**Standard scope components:**
- ABC Policy document (equivalent to Policy/SOP output)
- Risk assessment (which functions and counterparties carry ABC risk)
- Gifts and hospitality register design
- Third-party due diligence procedure
- Training material for ABC-exposed staff

**Typical deliverables:** ABC Policy (.docx); ABC risk assessment; gifts/hospitality register template; third-party DD checklist

**Applicable frameworks:**
[LAW — UK Bribery Act 2010, §7] Adequate procedures defence
[BEST_PRACTICE — ISO 37001:2016] Anti-bribery management system standard
[LAW — UAE Federal Law No. 4 of 2012] UAE anti-corruption law (private sector)

**Common chains:** → FRM Risk Register (Module 1 alignment); → Training Material; → Due Diligence (third-party DD for high-risk counterparties)

**Exclusions:** Internal audit of ABC programme effectiveness; legal advice on specific transactions; government licensing obligations

---

## ENGAGEMENT SCOPING (STANDALONE)

**Workflow:** Option 0 (engagement_scoping.py — BA-010)

**Triggering scenarios:**
- Client situation is described in plain language and Maher cannot immediately identify the right service
- Client needs a hybrid or novel engagement not covered by standard service lines
- Maher wants to confirm scope and exclusions before committing to a specific service line
- Client brief covers multiple possible engagement types

**Standard scope components:**
- 5-step conversational flow (BA-010): situational intake → scope recommendation → refinement → confirmation
- Scope document: engagement type(s), scope components, deliverables, sequencing, exclusions, caveats

**Typical deliverables:** Confirmed Scope document (.md); routing to appropriate workflow (if standard service); custom scope document (if novel/hybrid)

**Common chains:** Routes to whichever engagement type is confirmed at Step 5

**Exclusions:** Replacement of the 10-item menu (Engagement Scoping is an additional entry point — 30% of cases)

---

## DISAMBIGUATION GUIDE

Use this guide when a client situation could map to multiple engagement types:

| Situation | Most likely type | Ask this to confirm |
|-----------|-----------------|---------------------|
| "We think our vendor is overcharging" | Procurement Fraud Investigation | Is there evidence of collusion / kickbacks? If yes: Procurement Fraud. If no evidence yet: Transaction Testing first. |
| "We want to know if this person is safe to work with" | DD — Individual | Is this for onboarding (standard Phase 1) or something more serious (Enhanced Phase 2)? |
| "We need a fraud risk assessment" | FRM Risk Register | What modules? Full 8 or specific modules? Which industry and jurisdiction? |
| "We need to check if this company is sanctioned" | Sanctions Screening | Is it just sanctions or also PEP + adverse media? Phase 1 or Phase 2? |
| "We had a whistleblower complaint" | Investigation Report — Whistleblower | What are the specific allegations? Need to scope before investigating. |
| "We need an anti-bribery policy" | ABC Programme or Policy/SOP | Standalone ABC only or as part of a broader FRM engagement? |
| "We suspect financial manipulation" | Financial Statement Fraud Investigation or AML | Is it earnings manipulation (internal) or suspicious customer transactions (AML)? |
