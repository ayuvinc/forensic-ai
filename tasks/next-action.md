# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 024: junior-dev begins Sprint-TPL + Sprint-UX-FIXES (Phase A+B)**

Phase 9 schemas designed. Sprint-TPL, Sprint-WORK, Sprint-CONV, Sprint-UX-FIXES, Sprint-P9-UI all decomposed and written to todo.md. 25 tasks total.

**REVISED BUILD SEQUENCE (post-Codex review 2026-04-19):**

Sprint-SETUP (FIRST — ship blocker, no deps):
  SETUP-00: config consolidation (firm.json canonical path)
  SETUP-01: streamlit_app/shared/readiness.py
  SETUP-02: pages/00_Setup.py
  SETUP-03: bootstrap() readiness check

Phase A (after SETUP-03, parallel):
  EMB-00: requirements.txt
  P9-01-SLUG/SESSION/STATE/AC: schemas/project.py
  UX-F-06: .streamlit/config.toml + CSS fixes
  TPL-MOVE: move base templates to assets/templates/

Phase B (after Phase A, parallel):
  EMB-01: tools/embedding_engine.py
  TPL-01: tools/template_manager.py
  UX-F-01: page renumber + sidebar dividers
  UX-F-02: intake form fixes (clarity — ship blocker for Maher)
  TEST-01/02/03: tests/ scaffold + state machine + file_tools

Phase C (after Phase B, parallel):
  EMB-02: wire EmbeddingEngine into DocumentManager
  TPL-02: output_generator.py ← TemplateManager
  UX-F-03/04/05/07: pipeline progress + output + tracker + settings
  TEST-04/05/06/07: remaining test suite

Phase D (after Phase C, parallel):
  EMB-03: embedding status badge
  TPL-03/04: Settings 4-tab + intake template selector
  WORK-01: workflows/workpaper.py
  P9-UI-01: pages/01_Engagements.py
  KL-00/01: knowledge manifest + retriever

Phase E (after Phase D):
  TPL-05: AC smoke test
  WORK-02/03: workpaper triggers
  CONV-01: workflows/evidence_chat.py
  P9-UI-02: engagement wire-up
  ACT-01: logs/activity.jsonl writer + Activity Log page
  KL-02: engagement harvest pipeline

Phase F (after Phase E):
  CONV-02: streamlit_app/shared/engagement_shell.py (panel)

NOTE: Sprint-CONV moved to Phase E/F — depends on EMB-02,
engagement_shell.py design, and conversation persistence.
Not critical path for first client use.

**All gates cleared as of 2026-04-19:**
- BA-WORK-01 CONFIRMED — mid-pipeline trigger, Maher-driven structure, workpaper promotion to final
- BA-CONV-01 CONFIRMED (UPDATED) — persistent panel via engagement_shell.py (NOT bootstrap)
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
- Sprint-SETUP: SHIP BLOCKER — must complete before Maher can use app
- UX-D-05: st.form removal — open, non-blocking
- All other gates cleared 2026-04-19
