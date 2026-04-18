# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
qa (write AC for P8-10b), then junior-dev (build P8-10b), then qa-run + qa (approve), then junior-dev (P8-11a), then architect (advance to P8-14 smoke test gate)

## NEXT_TASK
**P8-10b — Team page (pages/10_Team.py)**

Read/write `firm_profile/team.json`.
One `st.expander` per team member — fields: name, title, credentials, bio.
"Add Member" button appends a new blank entry.
"Remove" button per member (inside expander).
Save writes atomically (.tmp → os.replace).
Bootstrap from `streamlit_app/shared/session.py`.

BA sign-off: `tasks/ba-logic.md:76` — setup wizard collects team bios into `firm_profile/`.
UX decision: UX-D-04 approved 2026-04-16 (Option B: separate Team page, not embedded in Settings).
Deps: P8-03-SHARED.

After P8-10b (in order):
- P8-11a — Document ingestion UI (st.file_uploader inline on Investigation, FRM, DD, TT pages)
- P8-14a..f — End-to-end smoke test (manual, AK + live API key + streamlit run app.py)

## CARRY_FORWARD_CONTEXT
Session 020 built P8-09a (Case Tracker) + P8-10a (Settings):
- pages/9_Case_Tracker.py — O(1) index read, 4-tier badges, one-expander-at-a-time, 28/28 AC PASS
- pages/settings.py — atomic write, conditional T&M fields, 3s success banner, 24/24 AC PASS
- Both QA_APPROVED, both committed on feature/P8-phase8-streamlit
- ARCH-INS-01 + ARCH-INS-02 + P8-08-PAGES + P8-09a + P8-10a all QA_APPROVED

## BLOCKERS_AND_ENV_LIMITATIONS
- P8-12-EXCEL: MISSING_BA_SIGNOFF
- P8-13-TIER: MISSING_BA_SIGNOFF
- SRL-B-BA: MISSING_BA_SIGNOFF
- FRM-R-00: MISSING_BA_SIGNOFF
- feature/P8-phase8-streamlit not pushed to remote
- Manual verification (P8-00c, P8-02d, P8-05b, P8-06e, P8-14) requires live API key + streamlit run
