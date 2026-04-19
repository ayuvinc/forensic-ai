# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 025: junior-dev builds Phase B (parallel tasks)**

Phase A complete and merged (5dd5de1 → merge 73d4b6e).
Phase B is fully unblocked.

**Phase B — build in parallel (all independent):**
  EMB-01: tools/embedding_engine.py — EmbeddingEngine with fallback (R-NEW-07)
  TPL-01: tools/template_manager.py — TemplateManager wrapping assets/templates/
  UX-F-01: page renumber + sidebar dividers (0_Scope → 00_Setup already done; renumber remaining)
  UX-F-02: intake form fixes (clarity — ship blocker for Maher)
  TEST-01: tests/conftest.py + shared fixtures
  TEST-02: tests/test_state_machine.py
  TEST-03: tests/test_file_tools.py

**Phase C (after Phase B):**
  EMB-02: wire EmbeddingEngine into DocumentManager
  TPL-02: output_generator.py ← TemplateManager
  UX-F-03/04/05/07: pipeline progress + output + tracker + settings
  TEST-04/05/06/07: remaining test suite

**Phase D (after Phase C):**
  EMB-03: embedding status badge
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
Phase A (EMB-00/P9-01/UX-F-06): 100%  ██████████ DONE — merged this session
Sprint-EMB:                      20%  ██░░░░░░░░ EMB-00 done; EMB-01 Phase B
Sprint-TPL:                       0%  ░░░░░░░░░░ TPL-01 starting Phase B
Sprint-UX-FIXES:                 14%  █░░░░░░░░░ UX-F-06 done; UX-F-01/02 Phase B
Sprint-TEST:                      0%  ░░░░░░░░░░ TEST-01/02/03 starting Phase B
Sprint-P9:                      100%  ██████████ P9-01 done (schemas)
Sprint-WORK:                      0%  ░░░░░░░░░░ Phase D
Sprint-CONV:                      0%  ░░░░░░░░░░ Phase E/F
Sprint-ACT:                       0%  ░░░░░░░░░░ Phase D
Sprint-KL:                        0%  ░░░░░░░░░░ Phase D
Sprint-AIC:                       0%  ░░░░░░░░░░ After Sprint-EMB
Sprint-RD:                        0%  ░░░░░░░░░░ Parallel with Phase B
```

**OVERALL: ~42% complete by task count (~68% by functional value)**

## CARRY_FORWARD_CONTEXT
Session 024 built:
- Sprint-SETUP (SETUP-00..03): firm.json canonical, readiness.py, 00_Setup.py wizard, bootstrap() gate
- EMB-00: requirements.txt + sentence-transformers/chromadb
- P9-01 (SLUG/SESSION/STATE/AC): schemas/project.py + 29 tests
- UX-F-06: .streamlit/config.toml, CSS h2/h3, severity CSS divs, sidebar footer
- All merged to main. No open branches.

Codex rescoping review processed:
- Full scope retained (all workflows ship)
- CLI = dev/support only; Maher uses Streamlit exclusively
- Branded .docx mandatory from day one

QA notes from Phase A:
- pipeline.py docstring says 'CRITICAL → st.error()' — stale, cosmetic, fix in Phase B
- datetime.utcnow() deprecated in Python 3.13 — fix when test suite expands

## BLOCKERS_AND_ENV_LIMITATIONS
- UX-D-05: st.form removal from generic intake — open, non-blocking
- No other blockers
