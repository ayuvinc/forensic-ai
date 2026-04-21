# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 036 (continued): Sprint-IA-01 Phase 0 → Phase A — ARCH-DOC-01 first, then build tasks**

Sprint-FE-TRIAGE Phase B complete (FE-TRIAGE-03/04/05 done). Product IA redesign approved (Session 036). BA decisions written to ba-logic.md. LLD written: docs/lld/product-ia-design.md.

**ARCH-DOC-01 blocks merge to main — not individual build tasks. Coding can start immediately.**

**Task order:**
1. `IA-00` — Seed test data script (scripts/seed_test_engagement.py) — run before testing IA-04
2. `IA-01` — Fix app.py bootstrap: add try/except + caller_file=__file__
3. `IA-02` — Navigation restructure: use st.navigation() in app.py with 5-section grouping (see docs/lld/product-ia-design.md) ← deps: IA-01
4. `IA-03` — Verify multi-workflow in 01_Engagements.py + add project_name field to ProjectState
5. `IA-04` — Workspace multi-workflow outputs ← run IA-00 seed script first
6. `IA-05` — Proposal arc v1 navigation positioning ← deps: IA-02
7. `IA-VERIFY` — Full page walk confirmation ← deps: IA-00..05
8. `ARCH-DOC-01` — HLD refresh (must complete before merge to main — not before coding)

**Branch:** `feature/sprint-fe-triage` (continuing)
**LLD:** docs/lld/product-ia-design.md (written Session 036)
**ACs:** see Sprint-IA-01 block in tasks/todo.md

## CARRY_FORWARD_CONTEXT
- FE-TRIAGE-03/04/05 complete: naming collision fixed, private Streamlit API replaced, bootstrap hardened
- FE-TRIAGE-01 (triage pass) paused — superseded by IA redesign; resume after Sprint-IA-01 for any remaining unknown crashes
- Product model: Engagement = root, two arcs (Proposal → Engagement), workflows are sub-items not top-level nav
- Streamlit version: 1.56.0 — supports st.navigation() and st.Page(title=...)

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
