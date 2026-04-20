# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 029: junior-dev builds Phase F (CONV-01, CONV-02, Sprint-AIC)**

Phase E complete and merged (0c127e9 → main). 120 tests pass (no regression).
Phase F is fully unblocked. Build tasks below.

**Phase F — primary tasks:**
  CONV-01: Create `workflows/evidence_chat.py` — `EvidenceChat` class: `chat(case_id, message, selected_doc_ids, conversation_history) -> str`. Single Sonnet turn. System prompt scoped to registered documents only. Context cap at `config.CEM_CONTEXT_CHARS` = 16,000 chars. Retrieval: EmbeddingEngine.retrieve() if available, else DocumentManager.find_relevant_docs(). Saves full conversation to `D_Working_Papers/evidence_chat_{YYYYMMDD_HHMMSS}.md` on session_end. Auto-save on mid-session app close.
  CONV-02: Create `streamlit_app/shared/evidence_chat_panel.py` — persistent collapsible chat panel injected on all pages via bootstrap(). Two-panel layout: left (1/3) document selector from DocumentManager with embedding status badges; right (2/3) chat interface. "Save as Lead" / "Save as Key Fact" / "Save as Red Flag" action buttons per assistant response. "NOT FOR CLIENT REVIEW" warning banner persistent. Conversation persists via cases/{id}/evidence_chat.jsonl. NOT a standalone page — shared panel component.
  AIC-01: Post-intake Haiku pass — after intake form submit, ask up to 3 follow-up questions conversationally (st.chat_message style); answers to `D_Working_Papers/intake_qa.json`; "Skip for now" button available.
  AIC-02: Pre-final-run Sonnet pass — reviews accumulated materials; renders 3–5 warning cards (Resolve or Proceed anyway); results to `D_Working_Papers/prefinalrun_review.json`; Run button locked until all cards acknowledged.
  AIC-03: `ProjectManager.get_intake_qa_context()` + `get_prefinalrun_context()` — inject into agent context dict.

**Phase F — secondary / non-blocking:**
  RD-00: Add `openpyxl>=3.1.0` to requirements.txt.
  P9-04a/b: Add AF_FOLDERS constant + is_af_project() to tools/file_tools.py.

**Gates:**
  CONV-01: No gates — EMB-02-REF docs available for retrieval fallback.
  CONV-02: depends on CONV-01.
  AIC-01/02/03: No gates — EMB and ACT complete.
  RD-00/P9-04a/b: No gates.

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
Phase E (WORK-02/03/ACT-02/03/KL-02/P9-UI-02/TEST-05): 100% ██████████ DONE — merged 0c127e9
Sprint-EMB:                     100%  ██████████ DONE — EMB-00/01/02/03 all done
Sprint-TPL:                      67%  ██████░░░░ TPL-01/02/03/04 done; TPL-05 open non-blocking
Sprint-UX-FIXES:                 86%  █████████░ UX-F-01/02/03/04/05/06/07 done; UX-D-05 open non-blocking
Sprint-TEST:                     71%  ███████░░░ TEST-01/02/03/04/05/06/07 done; TEST-07b open non-blocking
Sprint-P9:                      100%  ██████████ P9-01/P9-02 done
Sprint-WORK:                    100%  ██████████ WORK-01/02/03 all DONE
Sprint-CONV:                      0%  ░░░░░░░░░░ Phase F (CONV-01/02 next)
Sprint-ACT:                     100%  ██████████ ACT-00/01/02/03 all DONE
Sprint-KL:                      100%  ██████████ KL-00/01/02 all DONE
Sprint-AIC:                       0%  ░░░░░░░░░░ Phase F (AIC-01/02/03 next)
Sprint-RD:                        5%  ░░░░░░░░░░ RD-00 only (requirements.txt) is next
Sprint-P9-UI:                   100%  ██████████ P9-UI-01/02 both DONE
```

**OVERALL: ~62% complete by task count (~84% by functional value)**

## CARRY_FORWARD_CONTEXT
Session 028 built Phase E (7 parallel tasks):
- WORK-02: Case Tracker workpaper button; status-gated (_TERMINAL/INTAKE_CREATED/_ELIGIBLE); _load_source_artifacts() reads E_Drafts/ + root; DocumentManager.get_index()
- WORK-03: render_done_zone() enable_workpaper param; FRM + Investigation done stages wired
- ACT-02: SESSION_START in bootstrap(); PIPELINE_START/COMPLETE/ERROR in run_in_status(); SETTINGS events with old/new_value; DOCUMENT event in write_artifact(); DELIVERABLE in mark_deliverable_written()
- ACT-03: pages/15_Activity_Log.py (07 conflicted with 07_Proposal.py); pagination 50/page; filters; CSV export
- KL-02: tools/knowledge_harvester.py; _BLOCKED_FIELDS + _PII_PATTERNS two-layer sanitisation; firm_profile/knowledge/engagement/index.jsonl promotion; atomic write
- P9-UI-02: engagement_id: Optional[str] in CaseIntake; render_engagement_banner(); FRM pre-writes state.json before pipeline; orchestrator._set_status() carries engagement_id forward
- TEST-05: tests/test_project_schema.py; 120 total tests pass

QA gaps fixed during Phase E:
- ACT-02: DELIVERABLE events added to write_artifact() + mark_deliverable_written() (tools/file_tools.py) to reach ≥5 event categories
- P9-UI-02: FRM pre-writes state.json in pages/06_FRM.py before pipeline transitions (FRM bypasses Orchestrator)

QA warnings carried forward (non-blocking):
- W-01: Case Tracker "Draft" vs "Draft Ready" label — cosmetic
- W-02: TEST-07 return-type only; file artifact assertions deferred to TEST-07b
- W-03: EMB-03 chunk_count not in badge (DocumentEntry schema lacks chunk_count)
- W-04: P9-02 (ProjectManager) was unlisted dep — no task ID; documented
- W-05: ACT-03 page named 15_ not 07_ (R-018 pre-existing conflict)
- W-06: SETUP events (00_Setup.py) deferred — not built in Phase E

## BLOCKERS_AND_ENV_LIMITATIONS
- No blockers for Phase F tasks
- Sprint-RD and Sprint-AIC can run in parallel with Sprint-CONV
- Sprint-FE blocked on FE-GATE-BA (BA-FE-01 missing — needs /ba session first)
