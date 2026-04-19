# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 024: junior-dev begins Sprint-TPL + Sprint-UX-FIXES (Phase A+B)**

Phase 9 schemas designed. Sprint-TPL, Sprint-WORK, Sprint-CONV, Sprint-UX-FIXES, Sprint-P9-UI all decomposed and written to todo.md. 25 tasks total.

**Phase A — Start immediately, no deps (run in parallel):**

1. **EMB-00** — add `sentence-transformers>=2.7.0` and `chromadb>=0.4.0` to `requirements.txt`
2. **P9-01-SLUG + P9-01-SESSION + P9-01-STATE + P9-01-AC** — `schemas/project.py` all three schemas + smoke tests
3. **UX-F-06** — create `.streamlit/config.toml` + fix CSS h2/h3 selector + wire severity classes

**Phase B — After Phase A completes, run in parallel:**

4. **EMB-01-REF** — `tools/embedding_engine.py` (refined per BA-EMB-01)
5. **TPL-01** — `tools/template_manager.py`
6. **UX-F-01** — page renumber + sidebar section dividers

**Phase C — After Phase B:**

7. **EMB-02-REF** — wire EmbeddingEngine into DocumentManager
8. **TPL-02** — update output_generator.py
9. **UX-F-02 / UX-F-03 / UX-F-04 / UX-F-05 / UX-F-07** — remaining UX fixes (can run in parallel with each other)

**Phase D — After Phase C:**

10. **EMB-03-REF** — embedding status badge in Streamlit
11. **TPL-03** — Settings 4-tab redesign
12. **TPL-04** — intake template selector on all workflow pages
13. **WORK-01** — `workflows/workpaper.py` (after AK sign-off on BA-WORK-01)
14. **P9-UI-01** — `pages/01_Engagements.py` (after AK decision on UX-D-06)

**Phase E — After Phase D:**

15. **TPL-05** — AC smoke test
16. **WORK-02 / WORK-03** — workpaper triggers in tracker + done stages
17. **CONV-01** — `workflows/evidence_chat.py` (after AK sign-off on BA-CONV-01)
18. **P9-UI-02** — wire engagement_id into all workflow pages

**Phase F — After Phase E:**

19. **CONV-02** — `pages/14_Evidence_Chat.py` (needs EMB-02-REF + CONV-01)

**All gates cleared as of 2026-04-19:**
- BA-WORK-01 CONFIRMED — mid-pipeline trigger, Maher-driven structure, workpaper promotion to final
- BA-CONV-01 CONFIRMED — persistent collapsible panel on all pages (shared component via bootstrap)
- UX-D-06 RESOLVED — new 01_Engagements.py, Scope becomes step inside New Engagement flow
- UX-D-07 RESOLVED — persistent panel, not standalone page

**Only remaining open decision:** UX-D-05 (remove st.form from generic intake) — non-blocking.

## COMPLETION STATUS

```
Phase 1 (Foundation):          100%  ██████████ DONE
Phase 2 (Agents):               100%  ██████████ DONE
Phase 3 (FRM workflow):         100%  ██████████ DONE
Phase 4 (Remaining workflows):  100%  ██████████ DONE
Phase 5 (Personas + UI):         85%  █████████░ CLI UI done; Streamlit DONE (merged 97626d9)
Phase 6 (Bilingual):             60%  ██████░░░░ EN done; AR pending
Phase 7 (Blank framework):       20%  ██░░░░░░░░ P7-GATE passed; packaging tasks pending
Phase 8 (Streamlit):            100%  ██████████ DONE — merged to main
Phase 9 (Engagement framework):   5%  ░░░░░░░░░░ Schemas being designed; P9-01 starting
Phase 10 (New service lines):    40%  ████░░░░░░ DD/Sanctions/TT workflows built; KFs in progress
Phase 11 (Precision intake):      0%  ░░░░░░░░░░ Not started
Phase 12 (Knowledge files):      55%  █████░░░░░ FRM/Investigation/DD/Sanctions/TT done; 4 pending
Phase 13 (FRM guided exercise):   0%  ░░░░░░░░░░ Designed; not started
Sprint-EMB:                       5%  ░░░░░░░░░░ EMB-00 done; EMB-01-REF starting
Sprint-TPL:                       0%  ░░░░░░░░░░ Starting Phase A+B this session
Sprint-WORK:                      0%  ░░░░░░░░░░ Designed; UNBLOCKED — ready to build Phase D
Sprint-CONV:                      0%  ░░░░░░░░░░ Designed; UNBLOCKED — ready to build Phase E/F
Sprint-UX-FIXES:                  0%  ░░░░░░░░░░ Starting Phase A this session
Sprint-AIC:                       0%  ░░░░░░░░░░ After Sprint-EMB
Sprint-RD:                        0%  ░░░░░░░░░░ Parallel with P9-01..04
```

**OVERALL: ~63% complete**

## CARRY_FORWARD_CONTEXT
Session 024 (Architect session) decomposed:
- Sprint-TPL (5 tasks): TemplateManager, output_generator update, Settings 4-tab, intake selector, AC smoke
- Sprint-EMB (3 refinement tasks): EMB-01-REF/EMB-02-REF/EMB-03-REF refine Session 022 tasks per BA-EMB-01
- Sprint-P9 (4 tasks): P9-01-SLUG/SESSION/STATE/AC — project schema foundation
- Sprint-WORK (3 tasks): WorkpaperGenerator, Case Tracker trigger, pipeline done trigger — gated on AK sign-off
- Sprint-CONV (2 tasks): EvidenceChat backend, Evidence Chat page — gated on AK sign-off + UX-D-07
- Sprint-UX-FIXES (7 tasks): UX-F-01..07 — navigation, intake forms, progress, output, tracker, visual, settings
- Sprint-P9-UI (2 tasks): Engagements page, workflow wire-up — gated on UX-D-06
- Dependency graph in todo.md updated with all new sprints
- templates.json confirmed present at firm_profile/templates/ with 8 workflow slots
- output_generator.py confirmed: already has template_path param; TPL-02 adds TemplateManager integration

## BLOCKERS_AND_ENV_LIMITATIONS
- UX-D-05: Remove st.form from generic intake — open but non-blocking for all current sprints
- P8-12-EXCEL: MISSING_BA_SIGNOFF
- P8-13-TIER: MISSING_BA_SIGNOFF
- SRL-B-BA: MISSING_BA_SIGNOFF
- FRM-R-00: MISSING_BA_SIGNOFF
- Sprint-FE: FE-GATE-BA (BA-FE-01 missing)
- Sprint-WF/FR: GATED on RD-01
- Sprint-FE FE-06: GATED on P9-05 design decision
