# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
AK (P8-14 manual smoke test → merge → begin P9-01 + Sprint-EMB)

## NEXT_TASK
**Session 022: P8-14 smoke test, then build begins**

Architect has written the full P9 design to tasks/todo.md and tasks/ba-logic.md.
AK must review and approve before any build begins:

1. Review BA-P9-01 through BA-P9-06 in tasks/ba-logic.md — confirm all 6 decisions are correct
2. Review P9 task plan in tasks/todo.md (P9-01 through P9-09) — confirm scope and sequence
3. Complete P8-14 manual smoke test (see checklist below) with live API key

**P8-14 manual smoke test (still pending full clean run):**
Run: `source venv/bin/activate && RESEARCH_MODE=live streamlit run app.py`
- P8-14a: Browser opens; sidebar shows all 14 pages
- P8-14b: FRM page → intake → pipeline → review A/F/R → finalize → verify `cases/{id}/F_Final/final_report.en.md` written
  (Note: artifact path is now E_Drafts/ and F_Final/ for new P9 projects; legacy UUID cases still use root)
  For this smoke test, test as a legacy case (no active_project) — path should be `cases/{id}/final_report.en.md`
- P8-14c: Case Tracker shows new FRM case with DELIVERABLE_WRITTEN (green badge)
- P8-14d: Investigation page → intake → pipeline → download
- P8-14e: `ls cases/{id}/` root: final_report.*, state.json, audit_log.jsonl, citations_index.json; `ls cases/{id}/interim/` has *.v*.json
- P8-14f: CLI regression: `python run.py` → Option 6 → no crash

After P8-14 passes:
- Merge feature/P8-phase8-streamlit → main
- Begin P9-01 (junior-dev)

## COMPLETION STATUS

```
Phase 1 (Foundation):          100%  ██████████ DONE
Phase 2 (Agents):               100%  ██████████ DONE
Phase 3 (FRM workflow):         100%  ██████████ DONE
Phase 4 (Remaining workflows):  100%  ██████████ DONE
Phase 5 (Personas + UI):         85%  █████████░ CLI UI done; Streamlit in progress
Phase 6 (Bilingual):             60%  ██████░░░░ EN done; AR pending
Phase 7 (Blank framework):       20%  ██░░░░░░░░ P7-GATE passed; packaging tasks pending
Phase 8 (Streamlit):             92%  █████████░ All pages built + QA; P8-14 smoke test pending
Phase 9 (Engagement framework):   0%  ░░░░░░░░░░ Designed; not yet built
Phase 10 (New service lines):    40%  ████░░░░░░ DD/Sanctions/TT workflows built; knowledge files in progress
Phase 11 (Precision intake):      0%  ░░░░░░░░░░ Not started
Phase 12 (Knowledge files):      55%  █████░░░░░ FRM/Investigation/DD/Sanctions/TT KFs done; 4 pending
Phase 13 (FRM guided exercise):   0%  ░░░░░░░░░░ Designed; not started
```

**OVERALL: ~61% complete**

## CARRY_FORWARD_CONTEXT
Session 021 built:
- P8-14 smoke test run: 4 bugs found and fixed
  - `streamlit_app/shared/intake.py`: missing `created_at` + form key collision (commit 36f0cc5)
  - `streamlit_app/shared/session.py`: wrong audit hook import → PosixPath/dict TypeError (commit 36f0cc5)
  - `agents/junior_analyst/agent.py`: citation confidence normalization before validate_schema (commit 36f0cc5)
- Manual report generated from case 20260418-0C0A8D artifacts (52,302 chars, 24 findings, 3 modules)
- Phase 9 framework designed with AK — full design in tasks/ba-logic.md (BA-P9-01..06)
- P9 tasks decomposed and written to tasks/todo.md (P9-01 through P9-09)
- R-019 and R-020 added to tasks/risk-register.md

## BLOCKERS_AND_ENV_LIMITATIONS
- P8-14: requires AK + live ANTHROPIC_API_KEY + `streamlit run app.py`
- P8-12-EXCEL: MISSING_BA_SIGNOFF
- P8-13-TIER: MISSING_BA_SIGNOFF
- SRL-B-BA: MISSING_BA_SIGNOFF
- FRM-R-00: MISSING_BA_SIGNOFF
- feature/P8-phase8-streamlit not merged to main — blocked on P8-14
- P9 tasks: GATED on P8-14 + AK architecture approval
