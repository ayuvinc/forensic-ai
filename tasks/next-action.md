# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 036 (continued): Sprint-FE-TRIAGE — begin Phase B structural fixes**

Sprint-FE-TRIAGE plan approved (Session 036). Task decomposition complete.

**Immediate tasks (no FE-TRIAGE-01 dependency):**

1. `FE-TRIAGE-03` — Rename `pages/01_Scope.py` to `pages/01b_Scope.py`. Verify sidebar shows both pages.
2. `FE-TRIAGE-04` — Replace private Streamlit API in `streamlit_app/shared/session.py:156-179`. Add `caller_file` param to `bootstrap()`, update all 17 call sites.

**After FE-TRIAGE-04 complete:**
3. `FE-TRIAGE-05` — Wrap `bootstrap()` call sites in try/except with degraded-mode error panel.

**After Phase B complete:**
4. `FE-TRIAGE-01` — Triage pass: run `streamlit run app.py`, walk pages 00→16, populate `tasks/fe-triage-table.md`.

**Branch:** `feature/sprint-fe-triage`
**ACs:** see Sprint-FE-TRIAGE block in tasks/todo.md

## COMPLETION STATUS

```
Phase 1-8 + Sprints A-G:   100% ██████████ DONE — all merged
Phase H + Phase I (P9):    100% ██████████ DONE — merged c8ee66f
Sprint-RD:                 100% ██████████ RD-00..06 all done
P9 (Engagement Framework): 100% ██████████ P9-01..09 all done
Sprint-WF:                 100% ██████████ DONE — merged 3b498cc
Sprint-FR:                 100% ██████████ DONE — merged 3b498cc
Sprint-AIC:                100% ██████████ DONE — merged 4315d2a
Sprint-EMB:                100% ██████████ DONE — merged eee13f2
Sprint-FE:                 100% ██████████ DONE — merged a526bab
Sprint-WORK-02/03:         100% ██████████ DONE — merged 34bdcb1
Sprint-CONV-02:            100% ██████████ DONE — merged 4315d2a
KL-02 / ACT-02 / ACT-03:  100% ██████████ DONE — merged dfe9d65
Sprint-TPL (TPL-01..05):   100% ██████████ DONE — merged Session 035
Sprint-FE-TRIAGE:            0% ░░░░░░░░░░ NEXT (~2026-05-05)
```

**OVERALL: ~93% complete by task count (~99% by functional value)**

## CARRY_FORWARD_CONTEXT
Session 035 built TPL-05:
- Wired TemplateManager into write_final_report (replaced dead firm.json["templates"] lookup)
- Added template_resolved audit event (fallback: false = workflow base; fallback: true = generic/absent)
- BaseReportBuilder now prefers GW_ styles (GW_Heading1/2, GW_Body, GW_Title) when template defines them
- Smoke test at scripts/smoke_test_tpl05.py — all 7 ACs pass
- Session also planned Sprint-FE-TRIAGE after AK reported crashes on pages 00/01/16

## BLOCKERS_AND_ENV_LIMITATIONS
- FE-TRIAGE requires streamlit run app.py (RESEARCH_MODE=knowledge_only is fine — no API calls needed for triage)
- sentence-transformers not installed in dev env — EMB tests use code-inspection path
