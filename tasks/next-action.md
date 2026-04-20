# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 030: junior-dev builds Phase G (P9-04c/d, P9-05, P9-06, RD-01)**

Phase F complete and merged (4315d2a → main). 131 tests pass (no regression).
Phase G is fully unblocked. Build tasks below in order.

**Phase G — primary tasks:**

  P9-04c: Update `tools/file_tools.py:write_artifact()` — if `is_af_project(case_id)` is True,
    write to `cases/{id}/E_Drafts/` instead of root. Legacy projects: unchanged.
    Also update `write_final_report()` — AF projects write to `cases/{id}/F_Final/` instead of root.
    Guard: `is_af_project()` check at top of each function. Both paths must use atomic .tmp → os.replace().

  P9-04d: Update post-run migration in `tools/file_tools.py` (P8-05a logic) — for AF projects:
    migrate root `*.v*.json` → `E_Drafts/` (not `interim/`). For legacy projects: `interim/` unchanged.
    Use `is_af_project()` to branch.

  P9-05: New file `pages/09_Workspace.py` (replaces/extends the engagement workspace).
    Wire into existing `pages/01_Engagements.py` "Open Workspace" button.
    Implements full Input Session UI per todo.md P9-05a–P9-05e spec:
    - Project header (name, client, service type, language chip, last session date)
    - A-F folder tree with collapsible expanders + file list + upload per folder
    - Input/Final Run mode selector (radio, prominent)
    - Input panel: file uploader → C_Evidence/, session notes, key facts form, red flags form, context budget bar
    - Final Run panel: materials summary (doc/note/fact/flag counts) + "Run [workflow] Pipeline" button

  P9-06: Update `tools/document_manager.py` and `tools/project_manager.py`:
    - Add `CONTEXT_BUDGET_CHARS` reference to DocumentManager (already in config.py)
    - `DocumentManager.get_total_chars()` — sum char_count of all registered docs
    - `DocumentManager.context_usage_pct()` — get_total_chars() / CONTEXT_BUDGET_CHARS * 100
    - After each register_document(): check context_usage_pct(). If ≥ 75%: call _trigger_interim_context_write(case_id)
    - `_trigger_interim_context_write(case_id)`: Haiku call → write via ProjectManager.write_interim_context()
    - `DocumentManager.get_context_for_agents()`: if interim_context.md exists → return its content + docs
      registered after it; else → return all doc content

  RD-01: New file `tools/report_builder.py` — `BaseReportBuilder(template_path=None)`:
    - Uses python-docx. Loads template if provided; falls back to blank Document if template styles incompatible.
    - Methods: add_cover_page(title, subtitle, metadata), add_toc(), add_section(heading, content),
      add_subsection(heading, content), set_header(text), set_footer(text), save(output_path) → Path.
    - All writes atomic: write to .tmp path first, os.replace() to final.
    - Style fallback: catch python-docx style errors; log warning; continue with default styles.

**Phase G — acceptance criteria highlights:**
  P9-04c: write_artifact() for AF project → file lands in E_Drafts/ (unit test)
  P9-04c: write_final_report() for AF project → file lands in F_Final/ (unit test)
  P9-04c: legacy case paths unchanged (unit test)
  P9-05: page renders without error when no active_project set
  P9-05: Input mode shows file uploader + notes + facts + flags panels
  P9-05: Final Run mode shows materials summary before Run button
  P9-06: context_usage_pct() > 0 when docs registered; 0.0 when empty
  P9-06: At ≥75%: D_Working_Papers/interim_context.md created
  P9-06: get_context_for_agents() returns interim_context.md when present
  RD-01: BaseReportBuilder importable; save() writes a valid .docx (python-docx can reopen it)
  RD-01: Style fallback does not crash when template is None

**Gates:**
  P9-04c/d: No gates — is_af_project() already merged.
  P9-05: Depends on P9-04c (AF folder routing), P9-03A (done).
  P9-06: No gates — CONTEXT_BUDGET_CHARS already in config.py.
  RD-01: No gates — standalone, no upstream deps.

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
Phase F (CONV-01/02/AIC-01/02/03/P9-04a/b):      100%  ██████████ DONE — merged 4315d2a
Sprint-EMB:                     100%  ██████████ DONE — EMB-00/01/02/03 all done
Sprint-TPL:                      67%  ██████░░░░ TPL-01/02/03/04 done; TPL-05 open non-blocking
Sprint-UX-FIXES:                 86%  █████████░ UX-F-01..07 done; UX-D-05 open non-blocking
Sprint-TEST:                     86%  █████████░ TEST-01..07b done
Sprint-P9:                      100%  ██████████ P9-01/P9-02 done
Sprint-WORK:                    100%  ██████████ WORK-01/02/03 all DONE
Sprint-CONV:                    100%  ██████████ CONV-01/02 DONE
Sprint-ACT:                     100%  ██████████ ACT-00/01/02/03 all DONE
Sprint-KL:                      100%  ██████████ KL-00/01/02 all DONE
Sprint-AIC:                     100%  ██████████ AIC-01/02/03 DONE
Sprint-RD:                       5%  ░░░░░░░░░░ RD-00 done; RD-01 next
Sprint-P9-UI:                   100%  ██████████ P9-UI-01/02 both DONE
P9 (Engagement Framework):       45%  █████░░░░░ P9-01/02/03/04a/b done; P9-04c/d/05/06/07/08/09 open
```

**OVERALL: ~65% complete by task count (~86% by functional value)**

## CARRY_FORWARD_CONTEXT
Session 029 built Phase F (7 tasks + config additions):
- CONV-01: workflows/evidence_chat.py — EvidenceChat: chat(), session_end(), session_end_recovered()
- CONV-02: streamlit_app/shared/evidence_chat_panel.py — shared panel (not standalone page per AK locked decision)
- AIC-01: render_intake_questions() — Haiku, st.chat_message style, intake_qa.json
- AIC-02: render_prefinalrun_review() — Sonnet, 3-5 warning cards, prefinalrun_review.json, Run-button gate
- AIC-03: ProjectManager.get_intake_qa_context() + get_prefinalrun_context()
- P9-04a/b: AF_FOLDERS constant + is_af_project() in file_tools.py
- config.py: CEM_CONTEXT_CHARS=16000, CONTEXT_BUDGET_CHARS=400000

QA: 1 defect found/fixed (AIC-01 st.chat_message rendering). 131 tests pass.

## BLOCKERS_AND_ENV_LIMITATIONS
- No blockers for Phase G tasks
- P9-05 is the largest task in Phase G — if session context limit approaches 80%, close after P9-04c/d + RD-01
- Sprint-FE still BLOCKED on FE-GATE-BA (needs /ba session first)
- Sprint-WF, Sprint-FR GATED on RD-01 (now in-flight with Phase G)
