---
file: knowledge/due_diligence/framework.md
quality_tier: B
last_reviewed: 2026-04-07
reviewer: session-011
open_claims: 0
methodology_source: FATF + ACFE + BA-006/BA-007 report structure
note: CE Creates DD reports not available as reference (AK confirmed session 011); methodology derived from FATF/ACFE standards and BA-006/007 intake structure; validate against GoodWork's actual DD reports on first live engagement
---

<!-- Sources: knowledge/due_diligence/sources.md -->
<!-- Claim labels: [LAW] [BEST_PRACTICE] [PRODUCT_RULE] [ADVISORY] -->

# Due Diligence Framework — GoodWork Forensic AI
# KF-02 | Gates: SL-GATE-01 (workflows/due_diligence.py)

---

## WHAT IS DUE DILIGENCE

[BEST_PRACTICE — FATF Recommendation 10] Customer Due Diligence (CDD) is the process of identifying and verifying a customer's identity, understanding the nature of the business relationship, and assessing the risk of financial crime. Enhanced Due Diligence (EDD) applies additional scrutiny to higher-risk customers (PEPs, high-risk jurisdictions, complex ownership structures).

[PRODUCT_RULE] GoodWork's DD service covers two subject types with separate intake questionnaires:
- Individual (BA-006): 14 questions; Phase 1 (Standard) or Phase 2 (Enhanced)
- Entity (BA-007): 14 questions; Phase 1 (Standard) or Phase 2 (Enhanced)

Both types produce a DDReport (schemas/dd.py). Phase 2 includes HUMINT scope (ARCH-GAP-02); execution is always manual.

---

## FIVE-PHASE METHODOLOGY

<!-- Sources: FATF Recommendations; ACFE Fraud Examiners Manual; BA-006/007 intake structure -->

[ADVISORY — derived from FATF/ACFE standards; validate against GoodWork's actual DD practice on first live engagement]

### Phase 1 — Subject Identification and Scope Confirmation

[PRODUCT_RULE] Before any research begins:
- Confirm subject identity: individual (BA-006) or entity (BA-007)
- Confirm screening level: Standard Phase 1 or Enhanced Phase 2
- Confirm which screening lists apply (intake Q9)
- Confirm operating jurisdictions (drives source selection)
- Confirm deliverable format (intake Q14)
- Confirm awareness status (intake Q13 / Q14)

[ADVISORY] If the subject is aware the DD is being conducted (intake Q13 = True), the report tone shifts: it is a background verification (lower stakes language) rather than a covert background investigation. If the subject is unaware, treat all research sources as confidential.

### Phase 2 — Open-Source Intelligence Gathering (OSINT)

[BEST_PRACTICE — ACFE] OSINT covers publicly available information: corporate registries, court records, regulatory databases, news and media, social media (where appropriate), and public filings.

**OSINT sources by category:**

| Category | Sources (in priority order) |
|----------|-----------------------------|
| Corporate registries | MOEC, DED, ADGM, DIFC (UAE); Companies House (UK); MCA21 (India); jurisdiction registry as appropriate |
| Regulatory databases | SCA, DFSA, CBUAE (UAE regulators); SEBI, RBI, IRDAI (India); relevant regulator for operating jurisdiction |
| Court records | DIFC Courts (public judgments); Abu Dhabi courts (limited public access); ADGM Courts; jurisdiction-specific |
| News and media | General search (Tavily — general_search.py); Arabic-language search for UAE/GCC subjects |
| Sanctions lists | All 5 official lists (ofac.treas.gov, un.org, sanctions.ec.europa.eu, UK OFSI, UAE Cabinet) |
| Company financial filings | Zawya, official exchange filings (where applicable for listed entities) |

[PRODUCT_RULE] OSINT research uses both `general_search.py` (Tavily — any source) and `regulatory_lookup.py` (authoritative sources only). Regulatory claims in the output cite only authoritative sources; OSINT narrative may reference general sources with appropriate caveats.

### Phase 3 — Sanctions and PEP Screening

[BEST_PRACTICE — FATF Recommendations 6 and 12] This is the highest-integrity phase — findings here directly drive the risk classification.

**Screening procedure:**
1. Generate all name variants (transliterations, aliases, known former names) before running searches
2. Screen against all 5 official lists: OFAC SDN, UN Consolidated, EU Consolidated, UK OFSI, UAE Local
3. Classify any PEP found against the 4-category framework (knowledge/sanctions_screening/framework.md)
4. Apply false positive analysis to every potential match before reporting
5. Record: retrieval date, lists checked, variants used, results, false positive exclusions

[PRODUCT_RULE] Phase 3 findings are always included in every DD report regardless of whether Phase 1 or Phase 2 was selected at intake. The licensed database disclaimer (ARCH-GAP-01) is mandatory.

### Phase 4 — Adverse Media and Regulatory Record Review

[BEST_PRACTICE — ACFE] Adverse media review covers: criminal proceedings, civil litigation, regulatory enforcement, bankruptcy/insolvency, fraud allegations, corruption investigations, reputational incidents.

**Adverse media scope:**

| Coverage area | Sources |
|---------------|---------|
| Criminal proceedings | Court records where available; news search |
| Regulatory enforcement | Regulator enforcement databases (DFSA, CBUAE, SCA, SEBI, FCA, etc.) |
| Bankruptcy / insolvency | Corporate registry filings; court records |
| Fraud / corruption allegations | News search; Transparency International; enforcement databases |
| Civil litigation | DIFC Courts public judgments; jurisdiction court records |

[ADVISORY] English-language adverse media search is the primary source. Arabic-language search is applied for UAE/GCC subjects (Tavily — Arabic query). Urdu-language adverse media for Pakistani subjects requires a sub-contractor — flag this limitation in the methodology section.

**Adverse media interpretation:**

| Finding | Risk weight |
|---------|-------------|
| Conviction or regulatory sanction | High — direct evidence; cite source |
| Ongoing proceedings (alleged, charged, indicted) | Medium-High — note status; conviction not established |
| News allegation without proceedings | Medium — note source reliability; contested claims are not findings |
| Acquittal or case dismissed | Low — note that subject was cleared |
| No adverse media found | Neutral — note scope of search; absence of media is not clearance |

[PRODUCT_RULE] Adverse media findings must distinguish between: (1) established fact (conviction, regulatory order); (2) ongoing proceedings; (3) allegation. Do not conflate these in the output.

### Phase 5 — Corporate Mapping and Beneficial Ownership Analysis (Entity DD only)

[BEST_PRACTICE — FATF Recommendation 24] Understanding beneficial ownership is a core component of entity due diligence. Opaque corporate structures are a common money laundering red flag.

**Corporate mapping procedure:**
1. Identify all directors and shareholders from official corporate registry
2. Identify UBOs (Ultimate Beneficial Owners) above the threshold specified at intake (default: 25%)
3. Map any group structure (parent companies, subsidiaries, sister entities)
4. Screen all identified principals through Phase 3 (sanctions + PEP) individually
5. Document the ownership chain in the report

[ADVISORY] UAE corporate registry data (MOEC, DED) may not always reflect current UBO information — trust the registry but note where ownership data could not be independently verified. Where UBO data is unavailable from official sources, note this explicitly in the methodology.

---

## RISK CLASSIFICATION

<!-- Sources: FATF Recommendations; practitioner common practice -->

[PRODUCT_RULE] Every DD report produces:
1. A risk rating: **LOW / MEDIUM / HIGH**
2. A clearance status: **CLEAR** or **FLAG**

**Explicit criteria (not model judgment):**

| Rating | Criteria |
|--------|---------|
| LOW | No sanctions match (all 5 lists), no confirmed PEP, no adverse media, no regulatory action found |
| MEDIUM | Inconclusive sanctions match (requires more information); confirmed Category 3 PEP with mitigated risk; limited adverse media (allegation only, no proceedings); some corporate opacity but explainable |
| HIGH | Confirmed sanctions match on any list; confirmed Category 1 or 2 PEP with unmitigated risk; active regulatory enforcement action; significant adverse media (conviction, ongoing criminal proceedings, credible fraud allegation) |

| Status | Criteria |
|--------|---------|
| CLEAR | Rating is LOW; no further action recommended before proceeding with the relationship |
| FLAG | Rating is MEDIUM or HIGH; escalation recommended before proceeding; further information or EDD required |

[ADVISORY] MEDIUM + CLEAR is not a valid combination. Any MEDIUM rating produces FLAG — the client must make an informed decision with the full findings before proceeding.

---

## REPORT STRUCTURE

<!-- Sources: BA-006/007 report structure; FATF/ACFE standard -->

[PRODUCT_RULE] The report follows different structures for Individual and Entity subjects:

**Individual DD Report:**
1. Executive Summary
2. Subject Profile (identity, affiliations, background — factual only, no interpretation)
3. Methodology & Sources (phases completed, lists checked, variants searched, retrieval dates)
4. Sanctions Results (each list, matches found, false positive analysis)
5. PEP Results (category, risk assessment)
6. Adverse Media (findings by category, source reliability note)
7. Conclusion & Risk Classification (LOW/MEDIUM/HIGH + CLEAR/FLAG + recommendation)

**Entity DD Report:**
1. Executive Summary
2. Entity Profile (registration, structure, business activity)
3. Methodology & Sources
4. Sanctions Results (entity + named principals screened)
5. Beneficial Ownership Analysis (corporate map, UBO identification, principal screenings)
6. Adverse Media
7. Regulatory Compliance Status (any regulatory actions, filings, enforcement on record)
8. Conclusion & Risk Classification

---

## MANDATORY DISCLAIMERS

[PRODUCT_RULE] Two disclaimers are injected into every DD output:

**ARCH-GAP-01 — Licensed Database Disclaimer (all DD outputs):**
> This due diligence was conducted using publicly available official sanctions lists (OFAC SDN, UN Consolidated, EU Consolidated, UK OFSI, UAE Local) and open-source research. It does not include screening against WorldCheck, WorldCompliance, Refinitiv, Dow Jones Risk & Compliance, or other commercial database services. For acquisition-grade or regulatory-grade due diligence, commercial database screening is recommended.

**ARCH-GAP-02 — HUMINT Limitation (Phase 2 / Enhanced DD only):**
> This scope includes components requiring discreet source enquiries (HUMINT). This tool cannot perform HUMINT. Execution requires qualified human investigators with appropriate jurisdictional access. This section defines the HUMINT scope; delivery is manual.

---

## ZERO-INFORMATION MODE

[PRODUCT_RULE] If no documents are available at intake:
- Generate the report structure template with all sections pre-labelled
- Pre-populate Phase 3 (sanctions results) as PENDING with the lists to be checked
- Label the output `[DRAFT — awaiting subject data and research completion]`
- Generate a data requirements checklist for Maher:
  - What identifying information is needed before screening can proceed
  - Which corporate registry to check for entity subjects
  - Whether the client can provide a passport copy / corporate documents to aid verification

---

## EDGE CASES

| Scenario | Handling |
|----------|---------|
| Common name (high false positive risk) | Screen all lists; document every potential match with false positive analysis; note in methodology that name frequency increases false positive probability |
| Name in Arabic only | Transliterate; screen under all variants; document methodology |
| Subject has multiple nationalities | Screen under all; each nationality adds potential list exposure |
| No corporate registry records found for entity | Note explicitly; do not treat as clearance; flag as possible opacity |
| Passport number not provided (individual) | Proceed; note in methodology that match accuracy is reduced without DOB or passport number |
| Phase 2 selected but HUMINT required | Include HUMINT scope in the report; inject ARCH-GAP-02; note that execution is manual |
| Urdu-language adverse media needed | Note limitation; flag as sub-contractor dependency; proceed with English/Arabic search |
