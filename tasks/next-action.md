# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 037: Sprint-IA-01 — Build Phase A + B (coding begins)**

All architectural work for Sprint-IA-01 is complete. Docs are current. BA decisions BA-IA-01..08 all confirmed. LLD written.

**Task order:**
1. `IA-00` — `scripts/seed_test_engagement.py` — creates test ProjectState with 3 workflow runs; run before testing IA-04
2. `IA-01` — `app.py` bootstrap fix: add try/except + `caller_file=__file__` (same pattern already applied to all 16 pages in FE-TRIAGE-05)
3. `IA-02` — Navigation restructure: replace pages/ convention with `st.navigation()` in app.py, 5 sections per `docs/lld/product-ia-design.md` ← deps: IA-01
4. `IA-03` — Verify multi-workflow in `01_Engagements.py`; add `project_name` field to ProjectState ← no deps
5. `IA-04` — Workspace multi-workflow outputs in `16_Workspace.py` ← run IA-00 first
6. `IA-05` — Reposition Proposal arc in `st.navigation()` config ← deps: IA-02
7. `IA-VERIFY` — Full page walk ← deps: IA-00..05
8. `ARCH-DOC-01` (already done) — gates merge to main, not build

**Branch:** `feature/sprint-fe-triage` (continuing)
**LLD authority:** `docs/lld/product-ia-design.md`
**ACs:** Sprint-IA-01 block in `tasks/todo.md`

## COMMAND
```
/session-open session_id=037
```
Then:
```
/junior-dev Sprint-IA-01 Phase A+B — execute IA-00, IA-01, IA-02, IA-03, IA-04, IA-05, IA-VERIFY in order on branch feature/sprint-fe-triage. Full task specs in Sprint-IA-01 block of tasks/todo.md. LLD at docs/lld/product-ia-design.md.
```

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
Sprint-FE-TRIAGE-03/04/05: 100% ██████████ DONE — on feature/sprint-fe-triage
Sprint-IA-01 docs (ARCH):  100% ██████████ DONE — hld, README, brief, scope, LLD, packaging all current
Sprint-IA-01 code:           0% ░░░░░░░░░░ NEXT — Session 037
Sprint-IA-02 (hybrid intake):  0% ░░░░░░░░░░ AFTER Sprint-IA-01
```

**OVERALL: ~93% complete by task count (~99% by functional value)**

## CARRY_FORWARD_CONTEXT
Session 036 completed:
- ARCH-DOC-01: docs/hld.md fully rewritten (two-arc model, 40+ components, Partner never blocks)
- ARCH-DOC-02: README.md fully rewritten (Streamlit entry point, two-arc, all service lines)
- ARCH-DOC-03: GoodWork_AI_Framework_Brief.md + scope-brief.md fully updated
- docs/lld/product-ia-design.md: new LLD for Sprint-IA-01 navigation redesign
- docs/product-packaging.md: new — 6 shipping models documented (commercial + technical)
- BA-IA-04..08: project_name, min workstream, AUP type 8, Custom type 9, hybrid intake, Partner disclaimers
- knowledge/investigation: AUP and Custom investigation types fully documented
- architect.md: STRUCTURAL CHANGE PROTOCOL + doc freshness gate enforced
- session-close.md: STALE_PROJECT_DOCS gate including product-packaging.md
- FE-TRIAGE-03/04/05 already committed: naming fix, private API replaced, bootstrap hardened

## BLOCKERS_AND_ENV_LIMITATIONS
- Sprint-IA-01 build requires `streamlit run app.py` — `RESEARCH_MODE=knowledge_only` is fine, no API calls needed for navigation work
- sentence-transformers not installed in dev env — EMB tests use code-inspection path
- FE-TRIAGE-01 (triage pass) paused — resume after Sprint-IA-01 for any remaining unknown crashes
