# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 033: junior-dev builds Sprint-EMB on branch feature/sprint-emb**

Sprint-WF + Sprint-FR complete and merged (3b498cc → main). 27/27 ACs PASS.
Sprint-EMB is unblocked (different files from WF/FR — no conflict risk).

**Sprint-EMB — Semantic Embeddings:**
  EMB-01: `tools/embedding_engine.py` — `EmbeddingEngine(case_id)`: `ingest(doc_id, text)`,
           `get_context_for_query(query, top_k=5)`, `available` property; uses
           `sentence-transformers` (offline) or stubs when unavailable; stores in
           `D_Working_Papers/embeddings/`
  EMB-02: `tools/document_manager.py:register_document()` — after existing write, call
           `EmbeddingEngine(case_id).ingest(doc_id, text)` if engine available;
           write `D_Working_Papers/case_intake.md` on first call
  EMB-03: `pages/16_Workspace.py` — Semantic Search expander: text input + submit →
           calls `EmbeddingEngine.get_context_for_query()`; fallback message when
           engine unavailable (available=False) — no crash
  EMB-04: `core/orchestrator.py` — context-building block: when
           `EmbeddingEngine(case_id).available` is True, add `embedded_context` key
           to agent context dict; when False, omit key (DocumentManager content used)

**Branch:** feature/sprint-emb
**ACs:** see Sprint-EMB AC block in tasks/todo.md

## COMPLETION STATUS

```
Phase 1-8 + Sprints A-G:   100% ██████████ DONE — all merged
Phase H + Phase I (P9):    100% ██████████ DONE — merged c8ee66f
Sprint-RD:                 100% ██████████ RD-00..06 all done
P9 (Engagement Framework): 100% ██████████ P9-01..09 all done
Sprint-WF:                 100% ██████████ DONE — merged 3b498cc
Sprint-FR:                 100% ██████████ DONE — merged 3b498cc
Sprint-AIC:                100% ██████████ DONE — merged 4315d2a
Sprint-EMB:                  0% ░░░░░░░░░░ UNBLOCKED — build next
Sprint-FE:                   0% ░░░░░░░░░░ BLOCKED on FE-GATE-BA
```

**OVERALL: ~85% complete by task count (~97% by functional value)**

## CARRY_FORWARD_CONTEXT
Session 032 built Sprint-WF + Sprint-FR on feature/sprint-wf-fr:
- WF-01a: project_manager helpers (exhibit, lead, open/confirmed filtering)
- WF-01b: Workspace UI — Exhibit Register + Leads Register expanders
- WF-01c: InvestigationSections (evidence list, detailed findings with exhibit footnotes, leads, appendix)
- WF-02: DDSections (per-subject + consolidated)
- WF-03: TTSections (exceptions table, summary, Excel via openpyxl)
- WF-04: SanctionsSections (hit detail with disposition validation, false positive table, exec summary)
- WF-05: firm_profile/sanctions_disposition_policy.json
- FR-01: Stakeholder input form + _save_stakeholder() (append-only, ValueError on missing name)
- FR-02: get_stakeholder_context() + FRM junior prompt injection
- FR-03: recommendation_depth in CaseIntake schema + st.radio in FRM intake
- FR-04: FRMExcelBuilder (2-sheet xlsx: risk register + heat map)
- FR-05: BaseReportBuilder.add_heat_map() (5×5 DOCX table, fluent)
- FR-06: depth-aware recommendation instruction in junior prompt (_DEPTH_INSTRUCTIONS dict)

NOTE on EMB-04 carry-forward: get_context_for_agents() in DocumentManager is implemented but
no agent calls it yet. This is the primary thing EMB-04 closes.

## BLOCKERS_AND_ENV_LIMITATIONS
- Sprint-EMB: sentence-transformers may not be in requirements.txt — check first; if not, add it
  and handle ImportError gracefully (EmbeddingEngine.available = False when library missing)
- Sprint-FE still BLOCKED on FE-GATE-BA (needs /ba session for AI questions stage UX decisions)
