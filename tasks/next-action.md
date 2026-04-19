# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 023: Begin Sprint-EMB + P9-01 (Phase 9 gate cleared)**

Phase 8 complete. Branch merged to main (97626d9). P8-14 superseded. All gates cleared.

**Build sequence (from MEMORY.md):**
Sprint-EMB → Sprint-AIC → Sprint-RD (parallel with P9-01..P9-04) → Sprint-WF/FR/FE → P9-09 wire-up

**Session 023 scope — junior-dev starts with:**

1. **Sprint-EMB** (no external gating — first task):
   - EMB-00: add `sentence-transformers>=2.7.0` and `chromadb>=0.4.0` to `requirements.txt`
   - EMB-01: `tools/embedding_engine.py` — EmbeddingEngine class with graceful fallback (R-NEW-07)
   - EMB-02: wire into `DocumentManager.register_document()`

2. **P9-01** (parallel — no deps outside schemas/):
   - P9-01a: `schemas/project.py` — ProjectIntake with slug validator (R-019 mitigation)
   - P9-01b: InputSession schema
   - P9-01c: ProjectState schema
   - AC: import smoke + path traversal + empty slug test

**DO NOT start before these are discussed with AK:**
- Interim workpaper generation design (affects P9-05)
- Conversational evidence mode design (affects FE-06)
- See tasks/ba-logic.md MEMORY note re: next session topics

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
Phase 9 (Engagement framework):   0%  ░░░░░░░░░░ Designed; build starting this session
Phase 10 (New service lines):    40%  ████░░░░░░ DD/Sanctions/TT workflows built; KFs in progress
Phase 11 (Precision intake):      0%  ░░░░░░░░░░ Not started
Phase 12 (Knowledge files):      55%  █████░░░░░ FRM/Investigation/DD/Sanctions/TT done; 4 pending
Phase 13 (FRM guided exercise):   0%  ░░░░░░░░░░ Designed; not started
Sprint-EMB:                       0%  ░░░░░░░░░░ Starting this session
Sprint-AIC:                       0%  ░░░░░░░░░░ After Sprint-EMB
Sprint-RD:                        0%  ░░░░░░░░░░ Parallel with P9-01..04
```

**OVERALL: ~62% complete**

## CARRY_FORWARD_CONTEXT
Session 022 built:
- P8-14 superseded — smoke test scope replaced by Sprint-RD + Phase 9 design
- feature/P8-phase8-streamlit merged to main (97626d9) — Phase 8 complete
- Phase 9 framework designed (BA-P9-01..06) — all in tasks/ba-logic.md
- P9 tasks decomposed (P9-01..P9-09) — written to tasks/todo.md
- Sprint-EMB, AIC, RD, WF, FR, FE tasks written to tasks/todo.md
- R-019 (path traversal), R-020 (legacy/AF format coexistence) added to risk-register

## BLOCKERS_AND_ENV_LIMITATIONS
- Interim workpaper design: MUST discuss with AK before P9-05 / FE-06 build begins
- Conversational evidence mode: MUST discuss with AK before FE-06 build begins
- P8-12-EXCEL: MISSING_BA_SIGNOFF
- P8-13-TIER: MISSING_BA_SIGNOFF
- SRL-B-BA: MISSING_BA_SIGNOFF
- FRM-R-00: MISSING_BA_SIGNOFF
- Sprint-FE: MISSING_BA_SIGNOFF (FE-GATE-BA)
- Sprint-WF/FR: GATED on RD-01
- Sprint-FE: GATED on P9-05 design decision
