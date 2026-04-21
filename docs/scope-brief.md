---
Status: active
Source: user-confirmed
Last confirmed with user: 2026-04-21
Owner: Product
Open questions: 0
---

# Scope Brief

## Must-Have

Features that must ship for the product to have value for Maher:

- [x] FRM Risk Register — full 8-module guided exercise, co-created with Maher, regulatory-mapped, partner-reviewed
- [x] Investigation Report — 9 types (types 1–7 standard, type 8 AUP, type 9 Custom/Other), 4 audience versions, evidence chain enforced, 3-agent pipeline
- [x] Policy / SOP Generator — jurisdiction-aware, regulatory defaults, knowledge file backed
- [x] Client Proposal — 7-section, firm-branded, team credentials, pricing from firm_profile
- [x] Case persistence — multi-session case work, resume from last state, no data loss
- [x] Audit trail — append-only audit_log.jsonl, every agent run and decision recorded
- [x] Bilingual output — English primary, Arabic on request
- [x] Due Diligence workflow — standard and enhanced depth, individual and entity branches
- [x] Sanctions Screening workflow — OFAC, UN, EU lists, intake questionnaire
- [x] Transaction Testing workflow — risk-based, random, full population modes
- [x] Streamlit browser UI — 18 pages, project/engagement model, two-arc navigation
- [x] Semantic embeddings — document similarity and knowledge retrieval
- [x] Template manager — .docx GW_ style support, fallback chain
- [x] Activity logger — structured timestamped activity log per session
- [x] Engagement Scoping Workflow — problem-first scoping for ambiguous engagements
- [x] Workpaper generator — interim workpaper generation during active engagement
- [x] Evidence chat — conversational document review and evidence extraction
- [ ] Expert Witness Report — full pipeline workflow; model routing exists, page and knowledge file pending
- [ ] Hybrid intake — structured dropdowns + remarks-triggered conversation; replaces fully conversational intake across all workflows (Sprint-IA-02)
- [ ] Product IA redesign — two-arc navigation (Sprint-IA-01), project/engagement model enforced in UI
- [ ] Historical knowledge library — firm_profile/historical_registers/ and historical_reports/; sanitised ingestion

## Should-Have

Features important but can ship in a fast-follow release:

- [ ] AUP investigation mode — intake captures procedures list; no-conclusions enforcement on agent output (type 8 designed, Sprint-IA-02)
- [ ] Custom / Other investigation type — free-text description, structure-confirmed by Maher before drafting (type 9 designed, Sprint-IA-02)
- [ ] FRM guided exercise redesign — Step 1–5 co-creation loop, per-risk approve/edit/skip (Sprint-10D)
- [ ] Workflow chaining — compatible follow-on workflows on same project (11 valid chains)
- [ ] Privilege mode flag — investigation intake question: under legal professional privilege? Affects report language and structure
- [ ] Conflict of interest check — pre-engagement gate; generates conflict memo
- [ ] AML Program Review — distinct from sanctions screening; program design, review, enhancement
- [ ] Regulatory Response Report — client response to DFSA/CBUAE/SEC inquiry

## Cut-for-Now

Features deferred from v1:

- [ ] Fraud Audit as standalone service line — covered by investigation_report.py for v1
- [ ] ESI / e-discovery service line — eDiscovery platform dependency
- [ ] HUMINT service line — most complex; ethics-sensitive; built when specific engagement requires it
- [ ] WorldCheck / WorldCompliance integration — licensed DB; not accessible
- [ ] Urdu-language adverse media search — sub-contractor dependency
- [ ] Multi-user / team access
- [ ] Cloud sync or remote access
- [ ] Dispute Advisory / Damages Calculation — requires actuarial/financial model inputs outside tool scope
- [ ] Insurance / Business Interruption Claims — niche; add when Maher requests

## Explicit Out-of-Scope

- HUMINT execution — tool scopes requirements; execution is always manual
- Legal advice or formal risk determination
- Automated regulatory filing or client communication
- Batch screening pipelines (WorldCheck-grade)
- Statistical sampling computation (advisory guidance only)

## Delivery Target

| Field | Value |
|---|---|
| Target | Maher — pilot and personal production use; white-label distribution to market |
| Success metric | Maher produces a complete first draft of any standard deliverable in under 30 minutes active time |
| Primary deadline | Quality gates over speed — no hard date |

## Constraints and Dependencies

| Constraint | Impact |
|---|---|
| ANTHROPIC_API_KEY required | No fallback without it |
| TAVILY_API_KEY required | Research tools degraded without it; free tier = 1,000 searches/month |
| WorldCheck / WorldCompliance NOT accessible | DD and Sanctions outputs carry licensed-DB disclaimer; manual screening required |
| HUMINT always manual | Every enhanced DD and complex sanctions scope flags HUMINT as manual execution |
| knowledge/engagement_taxonomy/ required | Engagement scoping workflow references this for framework guidance |
| CE Creates reports as seed data | Historical DD library starts empty until Maher imports via HRL-01 import wizard |
