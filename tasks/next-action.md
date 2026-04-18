# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
junior-dev (build P8-10a), then qa-run + qa (approve), then junior-dev (P8-10b), then junior-dev (P8-11a), then architect (advance to P8-14 smoke test gate)

## NEXT_TASK
**P8-10a — Settings page (pages/settings.py)**

Read/write `firm_profile/firm.json` via existing setup_wizard functions.
`st.text_input` per field + Save button. Load at startup; write on save.
Depends on: P8-03-SHARED (bootstrap).

UX-005 spec (APPROVED): two-column layout (label 40% / input 60%), fields: Firm Name,
Logo Path, Default Currency (select), Pricing Model (select), T&M Day Rate, T&M Hour Rate.
Pricing fields visible only when Pricing Model = T&M.
Save button: primary (#D50032), enabled only when Firm Name non-empty.
Success: st.success("Firm profile saved.") for 3s, return to default.
Error on file read: st.warning (missing profile — empty fields, not broken).
Error on save: st.error + "Try Again" button.
Mobile (375px): two-column collapses to single column — labels above inputs.

After P8-10a (in order):
- P8-10b — Team page (pages/10_Team.py — UX-D-04 approved)
- P8-11a — Document ingestion UI (inline on Investigation, FRM, DD, TT)
- P8-14a..f — End-to-end smoke test (manual, AK)

## CARRY_FORWARD_CONTEXT
Session 020 built P8-09a (Case Tracker page):
- pages/9_Case_Tracker.py created — O(1) index read, 4-tier status badges,
  one-expander-at-a-time via selectbox, PIPELINE_ERROR guidance, Case ID truncated at 16 chars
- 28/28 AC criteria passed, QA_APPROVED
- All ARCH-INS-01 + ARCH-INS-02 + P8-08-PAGES + P8-09a now QA_APPROVED
- Branch: feature/P8-phase8-streamlit (all Phase 8 work)

## BLOCKERS_AND_ENV_LIMITATIONS
- P8-12-EXCEL: MISSING_BA_SIGNOFF
- P8-13-TIER: MISSING_BA_SIGNOFF
- SRL-B-BA: MISSING_BA_SIGNOFF
- FRM-R-00: MISSING_BA_SIGNOFF
- feature/P8-phase8-streamlit not pushed to remote
- Manual verification (P8-00c, P8-02d, P8-05b, P8-06e, P8-14) requires live API key + streamlit run
