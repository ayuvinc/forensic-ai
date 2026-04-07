---
file: knowledge/due_diligence/sources.md
quality_tier: B
last_reviewed: 2026-04-07
reviewer: session-011
---

# Due Diligence Research Sources — GoodWork Forensic AI

<!-- Companion to knowledge/due_diligence/framework.md (KF-02) -->

---

## UAE Corporate Registries (Authoritative)

| Source | URL | What it covers |
|--------|-----|----------------|
| UAE Ministry of Economy (MOEC) | economy.gov.ae | Federal commercial registration; mainland companies |
| Dubai Department of Economy & Tourism (DED) | dubaided.gov.ae | Dubai mainland commercial licensing |
| ADGM Registration Authority | adgm.com/setting-up | ADGM entity registration, directors, shareholders |
| DIFC Registrar of Companies | difclaw.ae / difc.ae | DIFC entity registration and filings |
| Abu Dhabi Department of Economic Development | abudhabi.ae/en/business | Abu Dhabi mainland licensing |
| Ras Al Khaimah Economic Zone (RAKEZ) | rakez.com | RAK free zone entities |
| JAFZA (Jebel Ali Free Zone) | jafza.ae | JAFZA entity registration |

## GCC Corporate Registries (Authoritative)

| Source | URL | What it covers |
|--------|-----|----------------|
| Saudi Ministry of Commerce | mc.gov.sa | Saudi company registry (Qiwa / Sijil Tijari) |
| Kuwait Ministry of Commerce | moci.gov.kw | Kuwait company registry |
| Qatar Ministry of Commerce | moci.gov.qa | Qatar company registry |
| Bahrain Ministry of Industry and Commerce | moic.gov.bh | Bahrain registry (Sijilat) |
| Oman Ministry of Commerce | mocioman.gov.om | Oman company registry |

## India (Authoritative)

| Source | URL | What it covers |
|--------|-----|----------------|
| Ministry of Corporate Affairs (MCA21) | mca.gov.in | Company registration, directors, filing history, charges |
| SEBI (Securities and Exchange Board of India) | sebi.gov.in | Listed company enforcement; director disqualifications |
| RBI | rbi.org.in | Banking sector licensing; enforcement actions |
| IRDAI | irdai.gov.in | Insurance sector enforcement |

## UK (Authoritative)

| Source | URL | What it covers |
|--------|-----|----------------|
| Companies House | find-and-update.company-information.service.gov.uk | UK company registration, directors, filings, charges, insolvency |
| FCA Register | register.fca.org.uk | FCA-regulated firm and individual registration; enforcement actions |
| UK Insolvency Register | insolvencydirect.bis.gov.uk | Individual insolvency records (England & Wales) |

## International Company Research (Reference — general trust)

| Source | URL | Trust | Notes |
|--------|-----|-------|-------|
| OpenCorporates | opencorporates.com | Reference — general | Aggregates company data from multiple jurisdictions; not always current; verify against official registry |
| Orbis (Bureau van Dijk) | bvdinfo.com | Reference — licensed | Comprehensive global company data; subscription required; not accessible to this tool directly |
| Refinitiv World-Check | refinitiv.com | Reference — licensed | Comprehensive DD database; subscription required; not accessible |
| Zawya | zawya.com | Reference — general | MENA financial and company data; some content is subscription-gated |

## Regulatory Enforcement Databases (Authoritative)

| Source | URL | What it covers |
|--------|-----|----------------|
| DFSA Enforcement Actions | dfsa.ae/enforcement | DIFC-regulated entity and individual enforcement history |
| CBUAE Regulatory Actions | cb.gov.ae | UAE Central Bank enforcement on licensed institutions |
| SCA Enforcement | sca.gov.ae | UAE securities regulator enforcement |
| SEBI Orders | sebi.gov.in/enforcement/orders | India securities enforcement; searchable by firm and individual |
| FCA Enforcement | fca.org.uk/enforcement | UK FCA enforcement actions; final notices; warning notices |
| World Bank Sanctions List | worldbank.org/en/projects-operations/procurement/debarred-firms | World Bank debarred firms and individuals |

## Adverse Media Research (General trust — use for narrative, cite authoritatively)

| Source | Usage | Notes |
|--------|-------|-------|
| Tavily (general_search.py) | English + Arabic adverse media | General trust; verify against primary sources before including in report |
| Gulf News / The National / Khaleej Times | UAE English-language news | General trust; verify claims |
| Al Arabiya / Al Jazeera English | MENA news | General trust |
| Reuters / Bloomberg / Financial Times | International financial news | Generally reliable; still general trust for DD purposes |

## Licensed DD Databases (NOT accessible to this tool — noted for disclosure)

| Tool | Provider |
|------|----------|
| World-Check One | LSEG |
| Refinitiv Due Diligence | Refinitiv |
| LexisNexis Diligence | LexisNexis |
| Dun & Bradstreet Risk Analytics | D&B |
| Kroll Due Diligence | Kroll |

[PRODUCT_RULE] ARCH-GAP-01 disclaimer is injected into every DD output — mandatory regardless of screening depth.

## Research Procedure for DD Engagements

1. **Subject identification confirmed** (intake complete, DDIntakeIndividual or DDIntakeEntity validated)
2. **Name variant generation** (transliterations, aliases, former names from intake)
3. **Phase 3 first** (sanctions + PEP — use `sanctions_check.py` and `regulatory_lookup.py`)
4. **Phase 2 OSINT** (corporate registries via `company_lookup.py`; general search for background)
5. **Phase 4 adverse media** (general_search.py; Arabic search for UAE/GCC subjects)
6. **Phase 5 if entity** (corporate mapping via company_lookup.py and official registries)
7. **Adverse media interpretation** (distinguish conviction / proceedings / allegation)
8. **Risk classification** (apply explicit criteria from framework.md — no model judgment)
9. **Output with disclaimers** (ARCH-GAP-01 always; ARCH-GAP-02 if Phase 2)
