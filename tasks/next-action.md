# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
AK (manual smoke test — P8-14a..f requires live API key + streamlit run app.py)

## NEXT_TASK
**P8-14 — End-to-end Streamlit smoke test (MANUAL — AK only)**

All automated Phase 8 tasks are QA_APPROVED and committed on feature/P8-phase8-streamlit.
Run the following in order. Each requires: `source venv/bin/activate && RESEARCH_MODE=live streamlit run app.py`

- P8-14a: Browser opens at localhost:8501; sidebar shows all pages (Scope, Investigation, Persona Review, Policy SOP, Training, FRM, Proposal, PPT Pack, Case Tracker, Settings, Team, DD, Sanctions, TT)
- P8-14b: FRM page: intake → pipeline → review 3+ risk items (A/F/R selectboxes visible, not hidden) → finalize → verify `cases/{id}/final_report.en.md` written
- P8-14c: Case Tracker: new FRM case appears with DELIVERABLE_WRITTEN status (green badge)
- P8-14d: Investigation page: intake → pipeline → download output
- P8-14e: Interim folder: `ls cases/{id}/` root has only `final_report.*`, `state.json`, `audit_log.jsonl`, `citations_index.json`; `ls cases/{id}/interim/` has `*.v*.json`
- P8-14f: CLI regression: `python run.py` → Rich menu renders → Option 6 completes → no crash

After P8-14 passes:
- Merge feature/P8-phase8-streamlit → main
- /ba session for P8-12-EXCEL and P8-13-TIER (FRM Excel output + two-tier risk structure)
- ARCH-INS-03 (circuit breaker) — deferred to pre-production

## CARRY_FORWARD_CONTEXT
Session 020 built and QA_APPROVED:
- P8-09a: pages/9_Case_Tracker.py — O(1) index read, 4-tier badges (commit 8908fcb)
- P8-10a: pages/settings.py — atomic write, conditional T&M fields (commit 62126e6)
- P8-10b: pages/10_Team.py — stable _id CRUD, atomic write (commit f85153e)
- P8-11a: document ingestion UI across 4 pages — registration on Run click, per-file isolation

P8-11a adds to:
- pages/2_Investigation.py — file_uploader + dm passed to run_investigation_workflow
- pages/6_FRM.py — new "confirm" stage; dm passed to run_frm_pipeline
- pages/11_Due_Diligence.py — file_uploader; registration only (no dm to workflow)
- pages/13_Transaction_Testing.py — file_uploader; registration only (no dm to workflow)

## BLOCKERS_AND_ENV_LIMITATIONS
- P8-12-EXCEL: MISSING_BA_SIGNOFF
- P8-13-TIER: MISSING_BA_SIGNOFF
- SRL-B-BA: MISSING_BA_SIGNOFF
- FRM-R-00: MISSING_BA_SIGNOFF
- feature/P8-phase8-streamlit not pushed to remote (merge to main after P8-14 passes)
- P8-14 entirely manual — requires live API key (ANTHROPIC_API_KEY) + `streamlit run app.py`
- P8-00c, P8-02d, P8-05b, P8-06e: also manual verification deferred to P8-14 run
