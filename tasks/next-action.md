# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 026: junior-dev builds Phase C (parallel tasks)**

Phase B complete and merged (1ee8cf4 → merge on main).
Phase C is fully unblocked.

**Phase C — build in parallel (all independent):**
  EMB-02: wire EmbeddingEngine into DocumentManager.register_document(); add embedding_status field to DocumentEntry
  TPL-02: update tools/output_generator.py to call TemplateManager().resolve(workflow_type) instead of hardcoded firm_profile/template.docx
  UX-F-03: pipeline progress bar — st.progress + agent label mapping + failure log capture in run_in_status()
  UX-F-04: done stage — inline report preview (st.expander), copy case ID button, "Start Another" button
  UX-F-05: Case Tracker (12_Case_Tracker.py) — status label mapping, dataframe row selection, Client column
  UX-F-07: Settings (14_Settings.py) — completeness indicator, T&C textarea, firm.json consolidation
  TEST-04: tests/test_post_hooks.py
  TEST-06: tests/test_output_generator.py
  TEST-07: tests/test_workflow_smoke.py

**Note before TPL-02:** confirm GW_ named styles (GW_Heading1, GW_Body) exist in firm_profile/templates/base.docx before building TPL-02.

**Phase D (after Phase C):**
  EMB-03: embedding status badge in Case Tracker
  TPL-03/04: Settings 4-tab + intake template selector
  WORK-01: workflows/workpaper.py
  P9-UI-01: pages/01_Engagements.py
  KL-00/01: knowledge manifest + retriever
  ACT-00/01: logs/ dir + ActivityLogger

**Phase E (after Phase D):**
  TPL-05: AC smoke test
  WORK-02/03: workpaper triggers
  CONV-01: workflows/evidence_chat.py
  P9-UI-02: engagement wire-up
  ACT-02/03: wire + Activity Log page
  KL-02: engagement harvest pipeline

**Phase F (after Phase E):**
  CONV-02: streamlit_app/shared/engagement_shell.py (panel)

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
Phase B (EMB-01/TPL-01/UX-F-01/02/TEST-01/02/03): 100% ██████████ DONE — merged this session
Sprint-EMB:                      40%  ████░░░░░░ EMB-00/01 done; EMB-02 Phase C
Sprint-TPL:                      20%  ██░░░░░░░░ TPL-01 done; TPL-02 Phase C
Sprint-UX-FIXES:                 43%  ████░░░░░░ UX-F-01/02/06 done; UX-F-03/04/05/07 Phase C
Sprint-TEST:                     43%  ████░░░░░░ TEST-01/02/03 done; TEST-04/06/07 Phase C
Sprint-P9:                      100%  ██████████ P9-01 done (schemas)
Sprint-WORK:                      0%  ░░░░░░░░░░ Phase D
Sprint-CONV:                      0%  ░░░░░░░░░░ Phase E/F
Sprint-ACT:                       0%  ░░░░░░░░░░ Phase D
Sprint-KL:                        0%  ░░░░░░░░░░ Phase D
Sprint-AIC:                       0%  ░░░░░░░░░░ After Sprint-EMB
Sprint-RD:                        0%  ░░░░░░░░░░ Parallel with Phase C
```

**OVERALL: ~47% complete by task count (~72% by functional value)**

## CARRY_FORWARD_CONTEXT
Session 025 built Phase B (7 parallel tasks):
- EMB-01-REF: tools/embedding_engine.py — EmbeddingEngine with two-layer fallback (ImportError → available=False; download error → available=False), ChunkResult dataclass, ChromaDB upsert, retrieve() returns [] if unavailable
- TPL-01: tools/template_manager.py — TemplateManager, _safe_path() traversal guard, resolve() 4-tier cascade, validate_docx() 7-style check, update_custom() rotation
- UX-F-01: 14 pages renumbered with zero-padded names (01_Scope → 14_Settings); sidebar section guide HTML injected in bootstrap()
- UX-F-02: dd_intake_form() merged single-form DD intake; frm_intake_form() redesigned with multiselect outside st.form for on_change reactivity; generic_intake_form() submit labels and placeholders from dicts
- TEST-01: tests/conftest.py with patched_cases_dir monkeypatching config.CASES_DIR + tools.file_tools.CASES_DIR + _INDEX_PATH
- TEST-02: tests/test_state_machine.py — 97 tests, all pass
- TEST-03: tests/test_file_tools.py — path traversal, atomic writes, state roundtrip, audit append

QA warnings (non-blocking, carry forward):
- Verify GW_ named styles exist in firm_profile/templates/base.docx before TPL-02 build
- pipeline.py docstring 'CRITICAL → st.error()' stale — cosmetic fix when convenient
- datetime.utcnow() deprecated in Python 3.13 — fix when test suite expands

## BLOCKERS_AND_ENV_LIMITATIONS
- UX-D-05: st.form removal from generic intake — open, non-blocking
- No other blockers
