# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 035: junior-dev runs TPL-05 end-to-end smoke test**

Session 034 was an interim QA/planning closeout only. It clarified that `TPL-05` is the only genuinely pending item from the prior handoff; the other options previously listed here were already completed and merged.

**Primary task:**

`TPL-05` smoke test:
  Run the FRM pipeline end-to-end with `RESEARCH_MODE=knowledge_only`, generate `cases/{case_id}/F_Final/final_report.docx`, open it with `python-docx`, confirm at least one `GW_` style is present, verify `template_resolved` audit event has `fallback: false`, and confirm `firm_profile/templates/templates.json` maps `frm_risk_register.base` to `frm_risk_register_base.docx`.

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
Sprint-WORK-02/03:         100% ██████████ DONE — merged 34bdcb1
TPL-05 smoke test:           0% ░░░░░░░░░░ NEXT
Sprint-CONV-02:            100% ██████████ DONE — merged 4315d2a
KL-02 / ACT-02 / ACT-03:  100% ██████████ DONE — merged dfe9d65
```

**OVERALL: ~92% complete by task count (~99% by functional value)**

## CARRY_FORWARD_CONTEXT
Session 033 built Sprint-EMB + Sprint-FE on separate feature branches:
- Sprint-EMB: EmbeddingEngine (ChromaDB + sentence-transformers), DocumentManager wire, Workspace semantic search, Orchestrator context injection
- Sprint-FE: ai_questions stage on 10 pages (one-at-a-time, case_intake.md), Settings template selector, FRM xlsx download, Sanctions per_hit_review, DD intake extensions + routing, Workspace conditional panels (DD/San/TT), Case Tracker Previous Versions
Session 034 added the final `TPL-05` acceptance criteria and corrected the stale handoff so the next build session does not reopen already-finished work.

## BLOCKERS_AND_ENV_LIMITATIONS
- sentence-transformers not installed in dev env — EMB tests use code-inspection path; live embedding requires: `pip install sentence-transformers chromadb`
- TPL-05 requires FRM pipeline to run end-to-end (needs ANTHROPIC_API_KEY + RESEARCH_MODE=knowledge_only)
