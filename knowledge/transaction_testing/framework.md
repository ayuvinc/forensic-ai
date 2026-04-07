---
file: knowledge/transaction_testing/framework.md
quality_tier: B
last_reviewed: 2026-04-07
reviewer: session-011
open_claims: 0
---

<!-- Sources: knowledge/transaction_testing/sources.md -->
<!-- Claim labels: [LAW] [BEST_PRACTICE] [PRODUCT_RULE] [ADVISORY] — see docs/lld/knowledge-quality-standard.md -->

# Transaction Testing Framework — GoodWork Forensic AI
# KF-01 | Gates: SL-GATE-03 (workflows/transaction_testing.py)

---

## WHAT IS TRANSACTION TESTING

[BEST_PRACTICE — ACFE Fraud Examiners Manual] Transaction testing is the systematic examination of financial records to identify exceptions, anomalies, or patterns indicative of fraud, control failures, or policy violations. It is distinct from audit sampling — it is specifically designed to find fraud indicators, not to form an opinion on financial statement accuracy.

[PRODUCT_RULE] GoodWork's Transaction Testing workflow follows a two-stage intake (BA-009):
- Stage 1: engagement context (5 branches)
- Stage 2: branch-specific questions + testing plan proposed by model
- Testing plan confirmed by Maher at SCOPE_CONFIRMED before any document ingestion

---

## FRAUD TYPOLOGY MATRIX

<!-- Sources: ACFE Fraud Examiners Manual; ACFE Report to the Nations; practitioner common practice -->

[BEST_PRACTICE — ACFE Fraud Examiners Manual] Different fraud types require different testing procedures. The fraud typology at intake drives the entire testing methodology.

### Procurement Fraud

[BEST_PRACTICE — ACFE] Primary testing procedures:

**Three-way matching:**
Compare Purchase Order → Invoice → Payment record. Any out-of-sequence combination is an exception:
- Invoice dated before PO (PO should precede invoice)
- Payment released before goods receipt confirmation
- Invoice amount exceeds PO amount without documented approval
- Multiple invoices for a single PO without explanation

**Vendor master analysis:**
- New vendors registered within 60 days before receipt of a large invoice
- Duplicate vendor registrations (same bank account, same address, similar name variants)
- Vendors with residential addresses, P.O. box only, or addresses matching employee records
- Vendors without publicly verifiable registration (company registry check)

**Split PO / split invoice testing:**
- POs just below the approval threshold (e.g. if threshold is AED 50,000, cluster of AED 45,000–49,999 POs to same vendor)
- Sequential invoices from same vendor on the same day or within 3 days

**Conflict of interest check:**
[ADVISORY] Cross-reference vendor bank account numbers, phone numbers, and addresses against the employee master. A match is a red flag requiring investigation — not proof of fraud, but warrants explanation.

### Payroll Fraud

[BEST_PRACTICE — ACFE Fraud Examiners Manual]

**Ghost employee detection:**
- Employees with no line manager recorded in HR system
- Employees with no emergency contact or next of kin on file (common in genuine ghost setups)
- Terminated employees still receiving payroll payments after exit date
- Multiple employees sharing a bank account for salary deposit
- Employees added to payroll outside the normal HR onboarding process (no offer letter, no contract in HR file)

**Rate manipulation:**
- Pay rate changes without corresponding HR approval record
- Pay rate changes effective on unusual dates (last day of month, Friday before a holiday)
- Multiple pay rate changes for same employee in short period

**Overtime analysis:**
- Employees with overtime exceeding X% of base salary (threshold: set with Maher at intake)
- Overtime patterns concentrated by department or supervisor (systemic vs individual)
- Overtime claimed on dates when the facility / office was closed

### Expense Fraud

[BEST_PRACTICE — ACFE Fraud Examiners Manual]

**Duplicate submission testing:**
- Same amount + same merchant + same or close date across multiple expense claims (within 7 days)
- Same merchant + similar amount + different claimants (possible coordination)
- Cross-period duplicates: same expense claimed in consecutive reporting periods

**Round-dollar testing:**
- Expense amounts that are exactly round numbers (AED 500, AED 1,000) are statistically unlikely in genuine expense reports
- [ADVISORY] Round-dollar testing is indicative, not conclusive — some genuine expenses (taxis, tips) are round. Apply in combination with other indicators.

**Weekend and holiday spend:**
- Expenses dated on days when the office was closed and the claimant was not on authorised travel
- Cross-reference expense dates against office calendar and approved travel records

**Policy compliance:**
- Claims exceeding per-diem limits or maximum single-claim limits
- Categories explicitly prohibited by policy (alcohol, entertainment above limit, personal items)
- Approver and claimant same person (no segregation of duties)

### Cash Fraud

[BEST_PRACTICE — ACFE Fraud Examiners Manual]

**Petty cash reconciliation:**
- Opening balance + total receipts − total disbursements ≠ closing balance on any date
- Disburse amounts without supporting receipts
- Receipts without sequential numbering or with gaps in number series

**Sequencing analysis:**
- Missing receipt numbers in a series indicate possible extraction and destruction of records
- Large round disbursements without supporting third-party documentation

### Financial Statement Fraud

[BEST_PRACTICE — ACFE Fraud Examiners Manual]

**Journal entry testing:**
- Manual journal entries posted by senior financial personnel (CFO, Finance Director) — these bypass normal transactional controls
- Entries posted at unusual times (late night, weekends, last business day of the period)
- Entries to unusual account combinations (debit revenue, credit liability — atypical)
- Entries with round-dollar amounts or with vague narrations ("adjustment", "correction")

**Cut-off testing:**
- Revenue recorded in a period for goods or services not delivered until the following period
- Expenses and liabilities recorded in the following period that should be in the current period
- Shipment dates on invoices vs. delivery confirmation dates

**Revenue recognition:**
- Shipments concentrated on the last 2–3 days of the accounting period (channel stuffing indicator)
- Customer return reversals booked in the first week of the following period
- Side letters or oral arrangements with customers modifying stated terms (HUMINT boundary — scope only)

### AML / Suspicious Transaction Testing

[BEST_PRACTICE — FATF Recommendations; CBUAE AML Standards]

**Structuring detection:**
- Multiple cash transactions just below the reporting threshold (UAE: AED 55,000 / USD 15,000 equivalent) from the same customer within a short period
- Multiple sub-threshold transactions by related parties that aggregate above threshold

**Counterparty analysis:**
- Transactions with counterparties in FATF high-risk jurisdictions (current FATF list — check sources.md)
- Counterparties appearing on sanctions lists (requires sanctions check integration)

**Velocity and pattern analysis:**
- Dormant accounts reactivating with sudden high-volume transactions
- Unusual transaction frequency changes without corresponding business explanation
- Round-trip transactions (funds leave and return through different intermediaries)

---

## BENFORD'S LAW

<!-- Sources: Benford (1938); ACFE Fraud Examiners Manual; practitioner common practice -->

[BEST_PRACTICE — ACFE] Benford's Law states that in many naturally occurring numerical datasets, the leading digit follows a predictable distribution (1 appears ~30% of the time, 9 appears ~5% of the time). Significant deviation from the expected distribution may indicate data manipulation.

**When Benford's Law applies:**

| Dataset | Applicable? | Rationale |
|---------|------------|-----------|
| Invoice amounts | YES | Wide range, naturally occurring |
| Payment amounts | YES | Wide range, naturally occurring |
| Journal entry amounts | YES | Wide range; effective for detecting manipulated entries |
| Expense claim amounts | YES (with caveats) | [ADVISORY] Round-number bias in genuine expense claims reduces power of this test |
| Payroll amounts | NO | Set by contract; not naturally occurring |
| Petty cash disbursements | NO | Population typically too small (< 1,000 entries) for reliable results |
| Rent / lease payments | NO | Fixed amounts; Benford's does not apply to fixed-value series |

[ADVISORY] Benford's Law requires a minimum dataset of approximately 1,000 entries for reliable results. Below that threshold, the test lacks statistical power. Note this in the testing plan.

[PRODUCT_RULE] When Benford's Law is applicable for the stated fraud typology, include it in the proposed testing plan. When it is not applicable, note this explicitly with the rationale — do not silently omit it.

---

## SAMPLING STANDARDS

<!-- Sources: ACFE; IIA IPPF; practitioner common practice -->

[ADVISORY — practitioner standard] The following sampling guidance is advisory. Maher decides the final sample size based on engagement scope, budget, and evidentiary standard required.

| Population size | Recommended approach |
|----------------|---------------------|
| < 1,000 records | Full population testing preferred |
| 1,000 – 10,000 | Full population if computationally feasible; otherwise statistical sampling |
| > 10,000 | Statistical random sample (95% confidence, ±5% margin of error) as base; supplement with judgmental sample on high-risk items |

[ADVISORY] Judgmental sampling — targeting high-risk periods, high-risk vendors, high-risk employees — should always supplement statistical sampling, not replace it. A statistical sample proves coverage; a judgmental sample finds the most likely fraud.

[PRODUCT_RULE] The testing plan proposed at Stage 3 of the intake must state: (1) population size if known; (2) whether full population or sampling; (3) rationale for sampling approach if not full population. Maher confirms or adjusts before SCOPE_CONFIRMED.

---

## UAE REGULATORY CONTEXT

<!-- Sources: cb.gov.ae; dfsa.ae; adgm.com; sca.gov.ae -->

[LAW — CBUAE AML/CFT Standards, Ch. 11] Licensed financial institutions in the UAE are required to conduct Transaction Monitoring as part of their AML compliance programme. Regulatory-mandated transaction testing for banks follows CBUAE prescribed methodology.

[LAW — DFSA Rulebook, AML Module] DIFC-authorised firms: transaction monitoring obligations under DFSA AML rules. Testing of transaction monitoring systems is a required part of the compliance framework review.

[LAW — ADGM FSRA AML Rules] ADGM-authorised firms: equivalent AML testing obligations under FSRA rules.

[LAW — SCA Resolution No. 11 of 2021 (Market Integrity)] SCA-regulated entities: transaction testing may be required as part of market manipulation investigations or regulatory examinations.

[PRODUCT_RULE] When the engagement context is "regulatory" (Branch E), the testing methodology must align with the prescribing regulator's requirements. The proposed testing plan notes the regulator, the prescribed methodology (if available), and the reporting deadline.

---

## ZERO-INFORMATION MODE

[PRODUCT_RULE] If Maher provides only the fraud typology at intake with no data available yet:
- Generate the full testing plan for the stated fraud typology using ACFE methodology above
- Leave all data-dependent fields blank (population size, date range, sample size)
- Label the plan `[DRAFT TESTING PLAN — awaiting data for finalisation]`
- Generate a data requirements checklist:
  - What data files are needed (general ledger, vendor master, payroll file, bank statements, etc.)
  - What format is preferred (Excel, CSV, PDF, system export)
  - What date range is required
  - What access permissions are needed (read-only is sufficient)

---

## EDGE CASES

| Scenario | Handling |
|----------|---------|
| Multiple fraud typologies | Propose a combined plan covering all typologies; Maher deselects components before SCOPE_CONFIRMED |
| Data in unexpected format | Testing plan notes data format requirements; flag if Maher's data does not match; do not test what cannot be read |
| Population too small for Benford's | Note in plan; substitute full population review or alternative tests |
| Regulatory engagement with prescribed methodology | Use regulator's prescribed methodology as primary; supplement with ACFE procedures where gaps exist |
| Maher wants to define the testing scope himself | Model still proposes a plan; Maher replaces or modifies; final plan must be confirmed at SCOPE_CONFIRMED before documents are ingested |
