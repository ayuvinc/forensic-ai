---
Status: confirmed
Source: user-confirmed
Last confirmed with user: 2026-04-06
Owner: Product
Open questions: 0
---

# Scope Brief

## Must-Have

Features that must ship for the product to have value for Maher:

- [x] FRM Risk Register — full 8-module guided exercise, co-created with Maher, regulatory-mapped, partner-reviewed
- [x] Investigation Report — 7 investigation types, 4 audience versions, evidence chain enforced, 3-agent pipeline
- [x] Policy / SOP Generator — jurisdiction-aware, regulatory defaults, knowledge file backed
- [x] Client Proposal — 7-section, firm-branded, team credentials, pricing from firm_profile
- [x] Case persistence — multi-session case work, resume from last state, no data loss
- [x] Audit trail — append-only audit_log.jsonl, every agent run and decision recorded
- [x] Bilingual output — English primary, Arabic on request
- [ ] Due Diligence workflow — individual and entity branches, 5-phase methodology, real GoodWork report template
- [ ] Sanctions Screening workflow — 5 official lists, PEP, intake questionnaire (BA-008)
- [ ] Historical knowledge library — firm_profile/historical_registers/ and historical_reports/; sanitised ingestion; FROM_SIMILAR_ENGAGEMENT drafts
- [ ] Engagement Scoping Workflow — problem-first dynamic scoping for ambiguous engagements (30% of cases)
- [ ] Streamlit frontend — replaces terminal UI; browser-based; file upload; download buttons

## Should-Have

Features that are important but can ship in a fast-follow release:

- [ ] Transaction Testing workflow — 2-stage scoping, fraud typology branching, testing plan generator
- [ ] Workflow chaining — compatible follow-on workflows on same case_id (11 valid chains)
- [ ] knowledge/engagement_taxonomy/ — full forensic engagement taxonomy (18+ types); gates engagement scoping workflow
- [ ] Persona Review — CFO, Lawyer, UAE Regulator, Insurance Adjuster challenge reports
- [ ] Proposal Deck (PPT prompt pack) — storyboard + per-slide prompts
- [ ] knowledge/due_diligence/ and knowledge/sanctions_screening/ — knowledge files for new service lines
- [ ] FRM guided exercise redesign — Step 1–5 co-creation loop replacing one-shot generation

## Cut-for-Now

Features deferred from v1:

- [ ] Fraud Audit as a standalone service line (SL-03) — covered sufficiently by investigation_report.py for now
- [ ] ESI / e-discovery service line (SL-05)
- [ ] Expert Witness Support service line (SL-06) — build when a specific engagement requires it
- [ ] HUMINT service line (SL-07) — most complex, most ethics-sensitive
- [ ] WorldCheck / WorldCompliance integration — licensed DB access; not accessible to tool
- [ ] Urdu-language research — sub-contractor dependency
- [ ] Multi-user / team access
- [ ] Cloud sync or remote access

## Explicit Out-of-Scope

- HUMINT execution (tool scopes requirements; execution is always manual)
- Legal advice or formal risk determination
- Automated regulatory filing or client communication
- Batch screening pipelines (WorldCheck-grade)
- The "Decision Quality Enforcement Platform" B2B SaaS concept (separate product)

## Delivery Target

| Field | Value |
|-------|-------|
| Target | Maher — pilot / personal production use |
| Success metric | Maher produces a complete first draft of any standard deliverable in < 30 minutes active time |
| Primary deadline | Maher live use — no hard date; quality gates over speed |

## Constraints and Dependencies

| Constraint | Impact |
|-----------|--------|
| ANTHROPIC_API_KEY required | No fallback without it; smoke test requires live key |
| TAVILY_API_KEY required | Research tools degraded without it; free tier = 1000 searches/month |
| WorldCheck/WorldCompliance NOT accessible | DD and Sanctions outputs carry licensed-DB disclaimer; manual screening required |
| HUMINT always manual | Every enhanced DD and complex sanctions scope flags HUMINT as manual execution |
| Streamlit gated on FE-01..FE-06 | Phase 8 (frontend) cannot start until FE tasks complete |
| knowledge/engagement_taxonomy/ required | Engagement scoping workflow blocked until KF-NEW created |
| CE Creates reports as seed data | Historical DD library starts empty until Maher imports via HRL-01 import wizard |
