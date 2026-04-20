# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 034: junior-dev builds Sprint-WORK-02 + Sprint-WORK-03 OR Sprint-AIC follow-up (TPL-05 smoke test)**

Sprint-EMB + Sprint-FE complete and merged (a526bab → main). 20/20 ACs PASS each.

**Priority order (pick one):**

**Option A — Sprint-WORK-02 + WORK-03 (WorkpaperGenerator follow-on):**
  WORK-02: `pages/16_Workspace.py` — Workpaper button integration (uses WORK-01 scaffold)
  WORK-03: `workflows/workpaper.py` — extended template system

**Option B — TPL-05 smoke test (unblocked, low-risk):**
  TPL-05: AC smoke test — FRM pipeline generates F_Final/final_report.docx using frm_risk_register_base.docx;
          open in python-docx, confirm GW_ styles present; audit_log has template_resolved event; templates.json correct

**Option C — Sprint-CONV-02 (EvidenceChat wiring to EMB):**
  Now unblocked by Sprint-EMB merge. Wires EMB-02 into CONV-01 retrieval path.

**Option D — KL-02 / ACT-02 / ACT-03 (knowledge/activity follow-ons):**
  All unblocked. Check tasks/todo.md for full specs.

**Branch convention:** `feature/sprint-{sprint-name}`
**ACs:** see relevant AC blocks in tasks/todo.md

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
Sprint-WORK-02/03:           0% ░░░░░░░░░░ UNBLOCKED — build next
TPL-05 smoke test:           0% ░░░░░░░░░░ UNBLOCKED
Sprint-CONV-02:              0% ░░░░░░░░░░ UNBLOCKED (EMB merged)
KL-02 / ACT-02 / ACT-03:    0% ░░░░░░░░░░ UNBLOCKED
```

**OVERALL: ~92% complete by task count (~99% by functional value)**

## CARRY_FORWARD_CONTEXT
Session 033 built Sprint-EMB + Sprint-FE on separate feature branches:
- Sprint-EMB: EmbeddingEngine (ChromaDB + sentence-transformers), DocumentManager wire, Workspace semantic search, Orchestrator context injection
- Sprint-FE: ai_questions stage on 10 pages (one-at-a-time, case_intake.md), Settings template selector, FRM xlsx download, Sanctions per_hit_review, DD intake extensions + routing, Workspace conditional panels (DD/San/TT), Case Tracker Previous Versions

## BLOCKERS_AND_ENV_LIMITATIONS
- sentence-transformers not installed in dev env — EMB tests use code-inspection path; live embedding requires: `pip install sentence-transformers chromadb`
- TPL-05 requires FRM pipeline to run end-to-end (needs ANTHROPIC_API_KEY + RESEARCH_MODE=knowledge_only)
