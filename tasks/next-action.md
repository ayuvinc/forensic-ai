# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 032: junior-dev builds Sprint-WF + Sprint-FR on one branch**

P9-09 complete and merged (c8ee66f → main). 5 ACs QA_APPROVED.
Sprint-WF and Sprint-FR are both unblocked. Build them together on one branch
(they both touch tools/project_manager.py — safer to avoid merge conflicts).

**Sprint-WF — Workflow-Specific Report Sections:**
  WF-01a: tools/project_manager.py — add_exhibit(), add_lead(), update_lead(),
           get_open_leads(), get_confirmed_leads() helpers
  WF-01b: Input Session workspace — Exhibit Register expander + Leads Register
           expander; confirmed lead → Haiku draft finding
  WF-01c: tools/report_sections/investigation.py — InvestigationSections:
           build_evidence_list(), build_detailed_findings() with Exhibit footnotes,
           build_open_leads_section(), build_exhibits_appendix()
  WF-02:  tools/report_sections/due_diligence.py — DDSections (per-subject + consolidated)
  WF-03:  tools/report_sections/transaction_testing.py — TTSections (exceptions table,
           summary page, Excel via openpyxl)
  WF-04:  tools/report_sections/sanctions.py — SanctionsSections (hit detail,
           false positive table, exec summary with disposition policy)
  WF-05:  firm_profile/sanctions_disposition_policy.json — default policy

**Sprint-FR — FRM Enhanced Deliverable:**
  FR-01: Stakeholder Input form in Workspace; save → D_Working_Papers/stakeholder_inputs.json
  FR-02: ProjectManager.get_stakeholder_context(slug); inject into FRM junior prompt;
         stakeholders in DOCX Appendix
  FR-03: recommendation_depth field in FRM intake schema + st.radio; default "structured"
  FR-04: tools/frm_excel_builder.py — FRMExcelBuilder: Sheet 1 risk register + Sheet 2 heat map
  FR-05: BaseReportBuilder.add_heat_map(risk_items) — 5×5 DOCX colour-coded table
  FR-06: Depth-aware recommendation generation; junior prompt depth instruction

**Branch:** feature/sprint-wf-fr
**ACs:** see Sprint-WF AC block and Sprint-FR AC block in tasks/todo.md

## COMPLETION STATUS

```
Phase 1-8 + Sprints A-G: 100% ██████████ DONE — all merged
Phase H + Phase I (P9):  100% ██████████ DONE — merged c8ee66f
Sprint-RD:                100% ██████████ RD-00..06 all done
P9 (Engagement Framework): 100% ██████████ P9-01..09 all done
Sprint-WF:                  0%  ░░░░░░░░░░ UNBLOCKED — build next
Sprint-FR:                  0%  ░░░░░░░░░░ UNBLOCKED — build next (same branch as WF)
Sprint-EMB:                 0%  ░░░░░░░░░░ UNBLOCKED — parallel to WF/FR (different files)
Sprint-FE:                  0%  ░░░░░░░░░░ BLOCKED on FE-GATE-BA
```

**OVERALL: ~80% complete by task count (~95% by functional value)**

## CARRY_FORWARD_CONTEXT
Session 031 built Phase I P9-09 (5 sub-tasks):
- P9-09a: all 3 intake forms pre-fill from project; client_name locked; slug as case_id
- P9-09b: get_project_dm() + get_project_language_standard() in intake.py;
          Investigation/FRM pass project DM to pipeline; language_standard in headless_params
- P9-09c: get_final_report_path() in file_tools.py; all 8 done zones use it
- P9-09d: Case Tracker "View Project" button for engagement_id entries
- P9-09e: backward compat — UUID case_id when no active_project

NOTE on AC2 partial: get_context_for_agents() in DocumentManager is implemented but no
agent calls it yet. Full wiring deferred to Sprint-EMB EMB-04.

## BLOCKERS_AND_ENV_LIMITATIONS
- Sprint-WF + Sprint-FR: both touch project_manager.py — must be on ONE branch together
- Sprint-EMB (EMB-01..04) can build in parallel (different files: embedding_engine.py, orchestrator.py)
- Sprint-FE still BLOCKED on FE-GATE-BA (needs /ba session — UX decisions for AI questions stage placement)
