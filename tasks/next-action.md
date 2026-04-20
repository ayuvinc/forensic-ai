# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 028: junior-dev builds Phase E (wiring + activity log + knowledge harvester)**

Phase D complete and merged (dfe9d65 → main). 120 tests pass (no regression).
Phase E is fully unblocked. Build all tasks in parallel where possible.

**Phase E — primary tasks (build in parallel):**
  WORK-02: Wire WorkpaperGenerator into Case Tracker — add "Generate Workpaper" button to case detail expander; gate on status ≥ JUNIOR_DRAFT_COMPLETE; pass most recent junior_output.v*.json as source_artifacts
  WORK-03: Wire WorkpaperGenerator into pipeline done zone — call after PARTNER_REVIEW_COMPLETE; auto-generate workpaper with pipeline artifacts; store path in CaseState
  ACT-02: Wire ActivityLogger into bootstrap() and all pipeline stages — log SESSION_START in bootstrap(); log PIPELINE_START/COMPLETE/ERROR in run_in_status() post-hooks; use module-level singleton from tools/activity_logger.py
  ACT-03: Create pages/07_Activity_Log.py — read logs/activity.jsonl; paginated table (50 rows); filter by category/engagement_id; no edit capability (read-only)
  KL-02: Create tools/knowledge_harvester.py — KnowledgeHarvester.harvest(domain) → None; reads knowledge/manifest.json; chunking logic (800-token chunks, 100-token overlap); writes to ChromaDB kb_base collection; skip if doc_id+version already indexed; log harvest events via ActivityLogger

**Phase E — secondary / non-blocking:**
  P9-UI-02: Wire active_project into all workflow pages (02_Investigation.py, 04_Policy_SOP.py, 05_Training.py, 06_FRM.py, 07_Proposal.py, 08_PPT_Pack.py, 09_Due_Diligence.py, 10_Sanctions.py, 11_Transaction_Testing.py) — read st.session_state["active_project"] at intake and pass engagement slug to pipeline; skip gracefully if None (standalone mode still works)
  TEST-05: tests/test_project_schema.py — confirm schemas/project.py ProjectIntake/ProjectState pass validation; derive_slug collision logic; already in tasks/todo.md PENDING

**Gates:**
  WORK-02/03: No additional gates — WORK-01 is done.
  ACT-02: No gates — ACT-01 is done.
  KL-02: No gates — KL-00/01 are done.
  P9-UI-02: No gates — P9-UI-01 is done; schemas/project.py from Phase A is stable.
  TEST-05: No gates.

## COMPLETION STATUS

```
Phase 1 (Foundation):          100%  ██████████ DONE
Phase 2 (Agents):               100%  ██████████ DONE
Phase 3 (FRM workflow):         100%  ██████████ DONE
Phase 4 (Remaining workflows):  100%  ██████████ DONE
Phase 5 (Personas + UI):         85%  █████████░ CLI UI done; Streamlit DONE
Phase 6 (Bilingual):             60%  ██████░░░░ EN done; AR pending
Phase 7 (Blank framework):       20%  ██░░░░░░░░ P7-GATE passed; packaging pending
Phase 8 (Streamlit):            100%  ██████████ DONE — merged 97626d9
Sprint-SETUP:                   100%  ██████████ DONE — merged 81dfdd8
Phase A (EMB-00/P9-01/UX-F-06): 100%  ██████████ DONE — merged
Phase B (EMB-01/TPL-01/UX-F-01/02/TEST-01/02/03): 100% ██████████ DONE — merged
Phase C (EMB-02/TPL-02/UX-F-03/04/05/07/TEST-04/06/07): 100% ██████████ DONE — merged c6a0599
Phase D (EMB-03/TPL-03/04/WORK-01/P9-UI-01/P9-02/KL-00/01/ACT-00/01): 100% ██████████ DONE — merged dfe9d65
Sprint-EMB:                     100%  ██████████ DONE — EMB-00/01/02/03 all done
Sprint-TPL:                      67%  ██████░░░░ TPL-01/02/03/04 done; TPL-05 open non-blocking
Sprint-UX-FIXES:                 86%  █████████░ UX-F-01/02/03/04/05/06/07 done; UX-D-05 open non-blocking
Sprint-TEST:                     57%  █████░░░░░ TEST-01/02/03/04/06/07 done; TEST-05/07b Phase E
Sprint-P9:                      100%  ██████████ P9-01/P9-02 done
Sprint-WORK:                     20%  ██░░░░░░░░ WORK-01 done; WORK-02/03 Phase E
Sprint-CONV:                      0%  ░░░░░░░░░░ Phase F (after Sprint-WORK)
Sprint-ACT:                      33%  ███░░░░░░░ ACT-00/01 done; ACT-02/03 Phase E
Sprint-KL:                       67%  ██████░░░░ KL-00/01 done; KL-02 Phase E
Sprint-AIC:                       0%  ░░░░░░░░░░ After Sprint-EMB (unblocked)
Sprint-RD:                        0%  ░░░░░░░░░░ Parallel with Phase E
```

**OVERALL: ~58% complete by task count (~80% by functional value)**

## CARRY_FORWARD_CONTEXT
Session 027 built Phase D (10 parallel tasks):
- EMB-03: document embedding badges (🟢/🟡/🔴/⚪) in Case Tracker detail expander; reads document_index.json
- TPL-03: Settings 4-tab layout; 5 completeness chips; template upload/preview/reset per workflow; critical GW_ style gate
- TPL-04: template_selector() collapsed expander in intake.py; 3-option radio; session state persistence; template_selector_ready() gate
- WORK-01: WorkpaperGenerator; 9-section ACFE; single Sonnet call; PRELIMINARY watermark; versioned to D_Working_Papers/
- P9-UI-01: pages/01_Engagements.py two-panel; New Engagement wizard; slug preview + collision detection; A-F folder tree
- P9-02: tools/project_manager.py; ProjectManager A-F lifecycle; InputSession; atomic JSON writes; context summary
- KL-00: knowledge/manifest.json; 14-entry manifest; all knowledge/*.md indexed
- KL-01: tools/knowledge_retriever.py; 3-layer ChromaDB; graceful fallback
- ACT-00: logs/.gitkeep + .gitignore; logs/*.jsonl gitignored
- ACT-01: tools/activity_logger.py; append-only JSONL; 50MB rotation; 10 event categories

QA warnings carried forward from Phase C (non-blocking):
- W-01: Case Tracker "Draft" vs "Draft Ready" — cosmetic
- W-02: TEST-07 return-type only; file artifact assertions deferred to TEST-07b
- UX-D-05: st.form removal from generic intake — open non-blocking

New QA warnings from Phase D (non-blocking):
- W-03: EMB-03 chunk_count not shown in badge (DocumentEntry schema lacks chunk_count field) — add in future task
- W-04: P9-02 (ProjectManager) was unlisted dependency; built inline — no task ID in todo.md originally

## BLOCKERS_AND_ENV_LIMITATIONS
- No blockers for Phase E tasks
- Sprint-AIC (AI-assisted intake) can start in parallel — unblocked since Sprint-EMB complete
- Sprint-CONV (EvidenceChat) depends on WORK-02/03 completion — Phase F
