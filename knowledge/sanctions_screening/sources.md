---
file: knowledge/sanctions_screening/sources.md
quality_tier: B
last_reviewed: 2026-04-07
reviewer: session-011
---

# Sanctions Screening Research Sources — GoodWork Forensic AI

<!-- Companion to knowledge/sanctions_screening/framework.md (KF-04) -->

---

## The 5 Official Screening Lists (Authoritative — always use current version)

| Source | URL | Update frequency | Notes |
|--------|-----|-----------------|-------|
| OFAC SDN + SSI List | ofac.treas.gov/ofac/downloads | Multiple times/week | Download CSV or XML; check retrieval date; also check OFAC's Non-SDN lists if full compliance required |
| UN Security Council Consolidated List | un.org/securitycouncil/sanctions/consolidated | Irregular — check regularly | XML and PDF formats available; covers all UN sanctions regimes |
| EU Consolidated Financial Sanctions List | sanctions.ec.europa.eu | Multiple times/week | CSV and XML download; covers all EU restrictive measures |
| UK OFSI Consolidated List | assets.publishing.service.gov.uk — search "OFSI consolidated list" | Multiple times/week | Separate from EU list post-Brexit; XLS and CSV download |
| UAE Local Terrorist Designation List | uaecabinet.ae — Cabinet Decisions section | Irregular | Available as PDF; Cabinet Resolution No. 83 of 2023 and predecessors |

## PEP and Adverse Media (Reference — not official lists)

| Source | URL | Trust | Notes |
|--------|-----|-------|-------|
| World Bank Debarred Firms | worldbank.org/en/projects-operations/procurement/debarred-firms | Reference | World Bank sanctions; not a government list but widely used |
| FATF Guidance on PEPs (2013) | fatf-gafi.org | Reference | Defines PEP categories; non-binding but industry-standard |
| OECD Country Risk Classifications | oecd.org | Reference | Country risk for export credit; useful for high-risk jurisdiction identification |
| Transparency International CPI | transparency.org/en/cpi | Reference — general | Corruption Perceptions Index; useful for jurisdiction risk context but not a sanctions source |

## Licensed Commercial Databases (NOT accessible to this tool — noted for disclosure)

| Tool | Provider | Notes |
|------|----------|-------|
| WorldCheck | LSEG (London Stock Exchange Group) | Industry standard; comprehensive PEP and sanctions coverage; subscription required |
| World-Check One | LSEG | Online platform version of WorldCheck |
| Refinitiv / Dow Jones Risk & Compliance | Refinitiv | Comprehensive; subscription required |
| LexisNexis Diligence | LexisNexis | Due diligence and sanctions screening; subscription required |
| ComplyAdvantage | ComplyAdvantage | AI-assisted screening; subscription required |

[PRODUCT_RULE] The licensed database gap must be disclosed in every output via ARCH-GAP-01 disclaimer. Do not imply the screening is comprehensive without this disclosure.

## Regulatory Framework Sources

| Source | URL | What it covers |
|--------|-----|----------------|
| FATF Recommendations | fatf-gafi.org/en/topics/fatf-recommendations | Reference | Recs 6, 12, 22 — PEP and sanctions obligations for financial institutions |
| CBUAE AML/CFT Standards | cb.gov.ae | Authoritative | UAE Central Bank AML/CFT requirements for licensed financial institutions |
| DFSA AML Rulebook | dfsa.ae/rulebook | Authoritative | DIFC firms: AML/sanctions compliance obligations |
| ADGM FSRA AML Rules | adgm.com | Authoritative | ADGM firms: AML/sanctions screening requirements |
| UAE Cabinet Resolution No. 83 of 2023 | uaecabinet.ae | Authoritative | Current UAE local terrorist designation framework |

## Research Procedure for Sanctions Screening Engagements

1. **Pre-screen**: download current versions of all 5 lists at start of engagement; record retrieval timestamp
2. **Name variant generation**: list all variants from intake + transliteration before running searches
3. **List screening**: run subject name(s) against all applicable lists using fuzzy matching
4. **False positive analysis**: for each potential match, document the match confidence scoring
5. **PEP check**: if PEP screening in scope, classify against FATF categories using authoritative sources
6. **Adverse media** (if in scope): use general_search.py; note that adverse media is not an official list — results are indicative only
7. **Output**: apply appropriate format per BA-008 Q10; inject ARCH-GAP-01 disclaimer
