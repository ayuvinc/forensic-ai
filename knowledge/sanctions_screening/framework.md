---
file: knowledge/sanctions_screening/framework.md
quality_tier: B
last_reviewed: 2026-04-07
reviewer: session-011
open_claims: 0
---

<!-- Sources: knowledge/sanctions_screening/sources.md -->
<!-- Claim labels: [LAW] [BEST_PRACTICE] [PRODUCT_RULE] [ADVISORY] — see docs/lld/knowledge-quality-standard.md -->

# Sanctions Screening Framework — GoodWork Forensic AI
# KF-04 | Gates: SL-GATE-02 (workflows/sanctions_screening.py)

---

## WHAT IS SANCTIONS SCREENING

[BEST_PRACTICE — FATF Recommendation 6] Sanctions screening is the process of checking whether
an individual, entity, or vessel appears on government-designated lists of sanctioned parties.
It is a mandatory control for financial institutions and a recommended control for all regulated
businesses with exposure to high-risk jurisdictions, counterparties, or transactions.

[PRODUCT_RULE] This tool screens against 5 official public lists only. It does not access
WorldCheck, WorldCompliance, Refinitiv, or other licensed commercial databases. Every output
must include the licensed-database disclaimer (ARCH-GAP-01).

---

## THE 5 OFFICIAL SCREENING LISTS

<!-- Sources: ofac.treas.gov, un.org/securitycouncil, sanctions.ec.europa.eu, assets.publishing.service.gov.uk, uaecabinet.ae -->

| List | Issuer | URL | What it covers |
|------|--------|-----|----------------|
| OFAC SDN List | US Department of the Treasury, Office of Foreign Assets Control | ofac.treas.gov | Specially Designated Nationals and Blocked Persons; also Sectoral Sanctions Identifications (SSI) |
| UN Consolidated List | UN Security Council | un.org/securitycouncil/sanctions/consolidated | All persons and entities subject to UN sanctions measures |
| EU Consolidated Sanctions List | European Council | sanctions.ec.europa.eu | EU restrictive measures; includes asset freezes, travel bans, arms embargoes |
| UK OFSI Consolidated List | HM Treasury, Office of Financial Sanctions Implementation | assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/ofsi | UK financial sanctions after Brexit; separate from EU list |
| UAE Local Terrorist Designation List | UAE Cabinet | uaecabinet.ae | UAE-specific designations under Cabinet Resolution No. 83 of 2023 and predecessor resolutions |

[PRODUCT_RULE] The default for all screenings is to check all 5 lists unless the client specifies otherwise at intake. Maher confirms the list selection at intake (BA-008 Q3).

[ADVISORY] The OFAC SDN list is the most frequently updated (multiple times per week). UN and EU lists update less frequently. UAE local list updates are irregular. Always use the current version at the time of screening — note the retrieval date in the output.

---

## PEP CLASSIFICATION

<!-- Sources: FATF Recommendations 12 and 22; ACFE; practitioner common practice -->

[BEST_PRACTICE — FATF Recommendation 12] Financial institutions must apply enhanced due diligence (EDD) to Politically Exposed Persons (PEPs). The FATF definition: individuals who are or have been entrusted with prominent public functions.

**PEP categories (standard industry classification):**

| Category | Examples | Risk level |
|----------|----------|-----------|
| Domestic PEP — Category 1 | Heads of state, government ministers, senior judges, central bank governors, senior military officers (general/admiral rank) | Highest |
| Foreign PEP — Category 1 | Same as above but in a foreign jurisdiction | Highest |
| Category 2 | Senior government officials (deputy minister level), state-owned enterprise executives, senior diplomats (ambassador), senior officials of international organisations | High |
| Category 3 | Local or regional government officials, family members of Category 1/2 PEPs (spouse, children, parents, siblings), close known associates of PEPs | Medium-High |
| Retired PEP | Former Category 1/2 PEPs | Declining risk: apply same risk rating for 12–24 months post-departure; review at end of period |

[ADVISORY] The FATF definition of "family members" and "close associates" is deliberately broad. Use judgment — a former president's adult child who is not publicly active may warrant less scrutiny than one who is actively involved in business or politics.

[PRODUCT_RULE] When a PEP is identified, the output must state: (1) the PEP category; (2) the current or former position; (3) the jurisdiction; (4) the risk rating; and (5) recommended next steps (EDD, sign-off, ongoing monitoring, or no further action if risk is low).

---

## SCREENING METHODOLOGY

<!-- Sources: FATF Guidance on PEPs (2013); ACFE; practitioner common practice -->

### Name Matching

[BEST_PRACTICE — practitioner standard] Effective screening requires matching against name variants — not just the exact name provided at intake:

1. **Transliteration variants** — Arabic names in particular have multiple English transliterations (Mohammed / Muhammad / Mohamed; Al-Rashidi / Al Rashidi / Rashidi)
2. **Known aliases** — captured at intake (BA-008 Q6)
3. **Former names** — maiden names, names changed after marriage or naturalisation
4. **Initials and abbreviations** — "J. Smith" may match "John Smith"

[PRODUCT_RULE] Screen under all name variants identified at intake. Document all variants used in the methodology section of the output.

### False Positive Analysis

[BEST_PRACTICE — ACFE] A potential name match must be assessed for false positive probability before flagging. Do not report a match without this analysis.

**Match confidence framework:**

| Factor | Weight |
|--------|--------|
| Name similarity (exact vs near-match) | High |
| Date of birth match (if available) | High |
| Nationality / country of birth match | Medium |
| Known alias match | High |
| Passport / ID number match (if available) | Definitive |
| Address or other identifier match | Medium |

**Match confidence outcomes:**

| Outcome | Definition | Action in output |
|---------|-----------|-----------------|
| Confirmed match | Name + at least 2 corroborating identifiers match | Report as confirmed; escalate |
| Inconclusive match | Name similar but insufficient corroborating data | Report as inconclusive; recommend further information |
| False positive | Same or similar name but identifiers clearly inconsistent | Document; do not flag; explain the exclusion |

[ADVISORY] A common name (e.g. Mohammed Ahmed in the UAE/GCC market) will produce many potential matches. The false positive analysis must be thorough — failure to document it leaves the screening output open to challenge.

---

## OUTPUT FORMATS

<!-- Sources: BA-008 Q10; practitioner common practice -->

[PRODUCT_RULE] Output format is selected at intake (BA-008 Q10). Each format has a different level of narrative:

| Format | When used | Narrative depth |
|--------|-----------|-----------------|
| Internal clearance memo | Routine onboarding / vendor clearance | Brief: subject, lists checked, result, conclusion |
| Full screening report | Regulatory submission, investment decision | Detailed: methodology, match analysis, false positive exclusions, risk rating |
| Regulatory filing | Regulator-mandated submission | Formal: follows regulator's prescribed format; includes certification |
| Screening spreadsheet | Batch input (multiple subjects) | Tabular: one row per subject; result, confidence, recommended action |

---

## RISK RATING AND CLEARANCE

[PRODUCT_RULE] Every sanctions screening output must produce:
1. A risk rating: **LOW / MEDIUM / HIGH**
2. A clearance status: **CLEAR** or **FLAG**

**CLEAR vs FLAG definition:**

| Status | Definition |
|--------|-----------|
| CLEAR | No confirmed match on any of the 5 lists; no confirmed PEP (or confirmed PEP with acceptable risk after EDD) |
| FLAG | Confirmed match on any list, OR confirmed unmitigated PEP risk, OR inconclusive match requiring further investigation before proceeding |

[ADVISORY — BA-016 open question note] AK confirmed (session 011) that CLEAR/FLAG is determined holistically across sanctions + PEP + adverse media combined where the scope includes adverse media. For sanctions-only screening without adverse media, CLEAR = no list match.

---

## MANDATORY DISCLAIMERS

[PRODUCT_RULE] Two disclaimers are injected into every sanctions screening output by the workflow. They are non-negotiable and cannot be removed.

**ARCH-GAP-01 — Licensed Database Disclaimer:**
> This screening was conducted using publicly available official lists (OFAC SDN, UN Consolidated, EU Consolidated, UK OFSI, UAE Local Designation List). It does not include screening against WorldCheck, WorldCompliance, Refinitiv, Dow Jones Risk & Compliance, or other commercial database services. For acquisition-grade, regulatory-grade, or comprehensive sanctions compliance purposes, commercial database screening is recommended in addition to official list screening.

**ARCH-GAP-02 — HUMINT Limitation (only when Phase 2 / Enhanced screening selected):**
> This scope includes components that require discreet source enquiries (HUMINT). This tool cannot perform HUMINT. Execution requires qualified human investigators with appropriate jurisdictional access. This section defines the HUMINT scope; delivery is manual.

---

## RECURRING MONITORING

[ADVISORY] Sanctions lists are updated frequently. A one-time screen is a point-in-time clearance only. For ongoing relationships (customers, vendors, employees), recurring monitoring is recommended.

[PRODUCT_RULE] This tool does not support automated recurring checks. Maher must re-run the workflow manually. At intake, if recurring monitoring is requested (BA-008 Q7), the output includes a recommended monitoring frequency and a calendar note for Maher.

---

## ZERO-INFORMATION MODE

[PRODUCT_RULE] If minimal intake is provided:
- Pre-load all 5 lists as the default screening scope
- Leave subject profile fields blank — do not fabricate any identity data
- Generate a structured output template ready for subject details to be inserted
- Label the output `[AWAITING SUBJECT DATA — do not use for clearance decisions]`

---

## EDGE CASES

| Scenario | Handling |
|----------|---------|
| Common name / high false-positive risk | Screen all lists; document every potential match with false positive analysis; note in methodology that name frequency makes definitive exclusion difficult |
| Arabic name with no English transliteration provided | Transliterate using standard romanisation; screen under all reasonable variants; document methodology |
| Subject has multiple nationalities | Screen under all nationalities; note that each nationality adds potential exposure |
| Batch request (multiple subjects) | Tool processes one at a time; note at intake; manual workflow for batch |
| Confirmed match found | Output match details + false positive analysis + escalation recommendation; does not constitute formal determination of sanctions violation — legal counsel required |
| Inconclusive match | State inconclusive; recommend obtaining additional identifying information (DOB, passport number, address); do not proceed to CLEAR without resolution |
