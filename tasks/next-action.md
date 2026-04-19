# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 027: junior-dev builds Phase D (parallel tasks)**

Phase C complete and merged (c6a0599 → main). 120 tests pass.
Phase D is fully unblocked.

**Phase D — build in parallel (all independent):**
  EMB-03: embedding status badge in Case Tracker (12_Case_Tracker.py) — show "Indexed / Pending / Failed" badge in document detail panel; read embedding_status from index.json entry
  TPL-03: Settings page — add 4-tab layout (Firm Profile / Templates / Team / Pricing); wire template upload to TemplateManager.update_custom()
  TPL-04: Intake template selector — add template_path field to generic_intake_form(); pass to OutputGenerator.generate_docx(template_path=...)
  WORK-01: Create workflows/workpaper.py — WorkpaperSection dataclass, run_workpaper_workflow(); guided interview flow per BA-WORK-01
  P9-UI-01: Create pages/01_Engagements.py — two-panel engagement dashboard; ProjectIntake list from projects/; "New Engagement" CTA switches to 0_Scope.py
  KL-00: Create knowledge/manifest.json — index all knowledge/*.md with doc_id, domain, version, effective_date, supersedes, authority_level
  KL-01: Create tools/knowledge_retriever.py — KnowledgeRetriever.retrieve(query, case_context) → KnowledgeBundle; queries kb_base, kb_user_sanitised, kb_engagement ChromaDB collections
  ACT-00: Create logs/ directory + tools/activity_logger.py — ActivityLogger, ActivityEntry dataclass, append_activity(case_id, event_type, summary, metadata)
  ACT-01: Wire ActivityLogger into: case creation (new_case), workflow start/complete, agent handoffs

**Gate before WORK-01:** confirm BA-WORK-01 exists in tasks/ba-logic.md — BLOCK if missing.
**Gate before P9-UI-01:** confirm P9-01 schemas (schemas/project.py) are complete — they are (merged Phase A).

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
Sprint-EMB:                      67%  ██████░░░░ EMB-00/01/02 done; EMB-03 Phase D
Sprint-TPL:                      40%  ████░░░░░░ TPL-01/02 done; TPL-03/04 Phase D
Sprint-UX-FIXES:                 86%  █████████░ UX-F-01/02/03/04/05/06/07 done; UX-D-05 open non-blocking
Sprint-TEST:                     57%  █████░░░░░ TEST-01/02/03/04/06/07 done; TEST-05/07b Phase D
Sprint-P9:                      100%  ██████████ P9-01 done (schemas)
Sprint-WORK:                      0%  ░░░░░░░░░░ Phase D
Sprint-CONV:                      0%  ░░░░░░░░░░ Phase E/F
Sprint-ACT:                       0%  ░░░░░░░░░░ Phase D
Sprint-KL:                        0%  ░░░░░░░░░░ Phase D
Sprint-AIC:                       0%  ░░░░░░░░░░ After Sprint-EMB
Sprint-RD:                        0%  ░░░░░░░░░░ Parallel with Phase D
```

**OVERALL: ~52% complete by task count (~76% by functional value)**

## CARRY_FORWARD_CONTEXT
Session 026 built Phase C (9 parallel tasks):
- EMB-02-REF: embedding_status field added to DocumentEntry; EmbeddingEngine.embed_document() wired in document_manager.register_document() with try/except
- TPL-02: OutputGenerator.generate_docx() 3-tier resolution (explicit → TemplateManager → plain); GW_ style fallback; audit event on case_id
- UX-F-03: run_in_status() — st.progress(), _AGENT_LABELS (7 entries), failure expander, pipeline_log_events buffer
- UX-F-04: render_done_zone() shared helper created; FRM/Investigation/DD done stages wired; FRM rewrite_count spinner
- UX-F-05: _STATUS_LABELS (11 entries), Client column, on_select="rerun" dataframe, engagement_id scaffold
- UX-F-07: completeness indicator (top of Settings), T&C textarea, Proposal pre-flight, REFACTOR-01 roadmap entry
- TEST-04/06/07: 23 new tests; total suite now 120 passed

QA warnings (non-blocking, carry forward to Phase D):
- W-01: Case Tracker "Draft" vs "Draft Ready" — cosmetic
- W-02: TEST-07 return-type only; file artifact assertions deferred to TEST-07b
- UX-D-05: st.form removal from generic intake — open non-blocking
- pipeline.py docstring 'CRITICAL → st.error()' stale — cosmetic
- datetime.utcnow() deprecated — fix when test suite expands

## BLOCKERS_AND_ENV_LIMITATIONS
- BA-WORK-01 required before WORK-01 can enter build queue
- No other blockers
