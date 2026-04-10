# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Phase 8 — Streamlit Frontend Migration (continued)**

Remaining build tasks (all unblocked):
1. P8-08a..j — 10 remaining workflow pages (Investigation, Persona Review, Policy SOP, Training, Proposal, PPT Pack, Scope, DD, Sanctions, TT)
2. P8-09a — Case Tracker page
3. P8-10a — Settings page (firm profile)
4. P8-11a — Document ingestion UI (st.file_uploader additions)
5. P8-14a..f — End-to-end smoke test

Manual verification steps AK must run before next junior-dev build:
- P8-00c: `python run.py` → Option 6 → confirm state advances to DELIVERABLE_WRITTEN
- P8-02d: Same as above — confirm FRM output identical to pre-split
- P8-05b: Check cases/{id}/ after run — final_report.* in root, *.v*.json in interim/
- P8-06e: `streamlit run app.py --server.address=localhost` → FRM page → A/F/R buttons visible (not hidden)

Branch: feature/P8-phase8-streamlit (not yet pushed to remote)

## CARRY_FORWARD_CONTEXT
Session 016 completed:
- Ultraplan reviewed: 5 corrections applied against actual code
- Phase 8 task plan written: 15 tasks, 40 sub-tasks (P8-00-EXTRACT to P8-14-SMOKE)
- P8-00-EXTRACT: mark_deliverable_written() moved to tools/file_tools.py; run.py shim kept
- P8-01: streamlit>=1.32.0 added to requirements.txt
- P8-02-SPLIT: run_frm_pipeline + run_frm_finalize created; run_frm_workflow unchanged
- P8-03-SHARED: streamlit_app/shared/ (session.py, intake.py, pipeline.py) created
- P8-04-APP: app.py created with RESEARCH_MODE banner and landing screen
- P8-05-FE08 + P8-07-FE09: write_final_report() updated — interim migration + template_path fix
- P8-06-FRM: pages/6_FRM.py created — four-stage FRM page (fixes FE-07)
- All files syntax-verified and import-verified
- R-009 moved to MITIGATED; R-014..R-018 added to risk register

Stale completed items in todo.md (not yet archived — do at session open):
- Sprint-10I (BUG-09a..e) all [x]
- Sprint-10L Phase A (SRL-01..04) all [x]
- Sprint-10K (PPH-01a..b, PPH-02a, PPH-03a..b, PPH-04a) all [x]
- BUG-10 (BUG-10a) [x]

## BLOCKERS_AND_ENV_LIMITATIONS
- P8-12-EXCEL: MISSING_BA_SIGNOFF — do not start
- P8-13-TIER: MISSING_BA_SIGNOFF — do not start
- SRL-B-BA: MISSING_BA_SIGNOFF — behavioral matrix blocked
- FRM-R-00: MISSING_BA_SIGNOFF — custom risk areas blocked
- feature/P8-phase8-streamlit not pushed to remote — push before next build session
- Manual verification (P8-00c, P8-02d, P8-05b, P8-06e) requires live API key + streamlit installed
