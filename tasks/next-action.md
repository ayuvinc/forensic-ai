# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
qa (write AC for P8-09a), then junior-dev (build), then qa-run + qa (approve), then architect (commit + advance)

## NEXT_TASK
**P8-09a — Case Tracker page (pages/9_Case_Tracker.py)**

Reads `cases/index.json` (written by ARCH-INS-02 write_state()) — O(1) load.
Build: `st.dataframe()` of cases with click-to-expand: deliverables, audit_log link, download final_report.
Depends on: P8-03-SHARED (bootstrap), ARCH-INS-02 (index.json).

After P8-09a (in order):
6. P8-10a — Settings page (firm_profile/firm.json read/write)
7. P8-10b — Team page (pages/10_Team.py — UX-D-04 approved)
8. P8-11a — Document ingestion UI (inline on Investigation, FRM, DD, TT)
9. P8-14a..f — End-to-end smoke test (manual, AK)

Post Phase 8 (separate sprint):
- ARCH-INS-03 — circuit breaker for Tavily/Anthropic

## CARRY_FORWARD_CONTEXT
Session 017 (continued — design + UX):
- GoodWork logo fetched from thegoodwork.online, saved to assets/logo.png
- app.py updated — logo in sidebar (180px) and landing (280px)
- .streamlit/config.toml created — light theme, #D50032 primary, #F5F2F0 secondary, #282827 text
- tasks/design-system.md written — full brand system extracted from site (Montserrat, red palette, warm neutrals, semantic colors, tokens, custom CSS)
- Montserrat loaded via Google Fonts in session.py bootstrap CSS injection
- tasks/ux-specs.md written — 6 specs (UX-001..006), all states, mobile 375px
- 4 UX decisions reviewed and APPROVED by AK:
  - D-01: Intake collapses to expander during run
  - D-02: Case tracker uses row expander
  - D-03: Start New Case keeps firm name, clears client data
  - D-04: Team bios get separate page (P8-10b added)
- All commits on branch: feature/P8-phase8-streamlit

## BLOCKERS_AND_ENV_LIMITATIONS
- P8-12-EXCEL: MISSING_BA_SIGNOFF
- P8-13-TIER: MISSING_BA_SIGNOFF
- SRL-B-BA: MISSING_BA_SIGNOFF
- FRM-R-00: MISSING_BA_SIGNOFF
- feature/P8-phase8-streamlit not pushed to remote
- Manual verification (P8-00c, P8-02d, P8-05b, P8-06e, P8-14) requires live API key + streamlit
