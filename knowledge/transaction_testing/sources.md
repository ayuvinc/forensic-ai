---
file: knowledge/transaction_testing/sources.md
quality_tier: B
last_reviewed: 2026-04-07
reviewer: session-011
---

# Transaction Testing Research Sources — GoodWork Forensic AI

<!-- Companion to knowledge/transaction_testing/framework.md (KF-01) -->

---

## Professional Standards (Reference — subscription/purchase required)

| Source | Access | What it covers |
|--------|--------|----------------|
| ACFE Fraud Examiners Manual | acfe.com (member access) | Transaction testing procedures for all fraud types; evidence standards; Benford's Law application |
| ACFE Report to the Nations (annual) | acfe.com/report | Fraud typology prevalence; industry benchmarks; median loss by scheme type |
| IIA IPPF (International Standards for the Professional Practice of Internal Auditing) | theiia.org (member access) | Sampling standards; audit evidence; testing methodology for internal auditors |

## UAE Regulatory Sources (Authoritative)

| Source | URL | What it covers |
|--------|-----|----------------|
| CBUAE | cb.gov.ae/en/banking-sector/regulations | Chapter 11 AML/CFT Standards; transaction monitoring requirements for licensed banks and exchange houses |
| DFSA Rulebook — AML Module | dfsa.ae/rulebook | AML compliance and transaction monitoring for DIFC-authorised firms |
| ADGM FSRA AML Rules | adgm.com/laws-regulations/rules | AML testing obligations for ADGM-authorised firms |
| SCA | sca.gov.ae/en/legislation | Market integrity rules; SCA Resolution No. 11 of 2021 (market manipulation testing) |

## FATF and International Standards (Reference)

| Source | URL | What it covers |
|--------|-----|----------------|
| FATF Recommendations | fatf-gafi.org/en/topics/fatf-recommendations | Rec. 6 (PEPs), Rec. 10–13 (customer due diligence), Rec. 20 (suspicious transaction reporting); AML methodology |
| FATF Guidance on AML/CFT in the Securities Sector | fatf-gafi.org | AML testing for securities firms |
| FATF High-Risk Jurisdictions (current list) | fatf-gafi.org/en/topics/high-risk-jurisdictions | Updated bi-annually; check current list for counterparty jurisdiction analysis |
| Egmont Group (Financial Intelligence Units) | egmontgroup.org | Typology reports on AML schemes; useful for AML testing pattern design |

## Statistical Methodology (Reference)

| Source | Notes |
|--------|-------|
| Benford, F. (1938) "The Law of Anomalous Numbers", Proceedings of the American Philosophical Society | Original Benford's Law paper; cited as methodological foundation |
| Nigrini, M. (2012) "Benford's Law: Applications for Forensic Accounting, Auditing, and Fraud Detection" | John Wiley & Sons; practical application guide for forensic accountants |

## Research Procedure for Transaction Testing Engagements

1. **Fraud typology confirmation** — confirm with Maher at intake; shapes entire methodology
2. **Regulatory context check** — if client is a regulated entity, check applicable regulator's testing requirements before proposing the plan (use `regulatory_lookup.py`)
3. **Data format review** — before finalising the testing plan, confirm what data formats the client can provide; adjust procedures accordingly
4. **Benchmark** — for large or unusual fraud typologies, search ACFE Report to the Nations for industry loss data and frequency to contextualise findings
5. **Regulatory filing** — if the output is a regulatory submission, check the specific regulator's prescribed reporting format
