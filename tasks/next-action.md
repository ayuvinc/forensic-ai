# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 030 continued (or Session 031): junior-dev builds Phase I (P9-09 + Sprint-WF/FR)**

Phase H complete and merged (dff5671 → main). 20 ACs QA_APPROVED.
Phase I is unblocked.

**Phase I — primary tasks:**

  P9-09: Wire all workflow pages to project context.
    Files: pages/02_Investigation.py, pages/06_FRM.py, pages/07_Proposal.py,
           pages/04_Policy_SOP.py, pages/05_Training.py, pages/08_PPT_Pack.py,
           pages/00_Scope.py, pages/09_Due_Diligence.py, pages/10_Sanctions.py,
           pages/11_Transaction_Testing.py
    Deps: P9-03A, P9-04, P9-05, P9-06, P9-07B, P9-08 — all DONE.
    BA: BA-P9-01, BA-P9-03.

    P9-09a: When st.session_state.active_project is set: pre-fill intake fields from
      project context (client_name, service_type, language_standard); lock fields
      set at project creation.
    P9-09b: When active_project set: DocumentManager initialized from
      ProjectManager.get_context_for_agents() instead of fresh intake; accumulated
      context passed to pipeline.
    P9-09c: Post-pipeline: artifacts → E_Drafts/; final report → F_Final/ (via P9-04).
      Case Tracker reads from F_Final/.
    P9-09d: Case Tracker (pages/09_Case_Tracker.py): P9 projects → "View Project"
      link routes to Engagements page with active_project set.
    P9-09e: No active_project → existing behavior unchanged (backward compat).

  Sprint-WF (now unblocked — RD-01 + P9-05 done):
    WF-01..05 — workflow-level improvements; see Sprint-WF block in todo.md.

  Sprint-FR (now unblocked — RD-01 + P9-05 done):
    FR-01..06 — report/finalize improvements; see Sprint-FR block in todo.md.

**Phase I — acceptance criteria highlights:**
  P9-09a: intake form shows pre-filled client_name from project; field is read-only
  P9-09b: pipeline receives interim_context.md content (if exists) via DocumentManager
  P9-09c: final report for AF project lands in cases/{slug}/F_Final/final_report.en.md
  P9-09d: Case Tracker "View Project" button present for P9 projects; absent for legacy
  P9-09e: all pages function identically when no active_project (no regression)

**Gates:**
  P9-09: all P9 deps done (confirmed). Large task — decompose at build time per page.
  Sprint-WF/FR: unblocked — schedule after P9-09 or interleave.

## COMPLETION STATUS

```
Phase 1-8 + Sprints A-G: 100% ██████████ DONE — all merged
Phase H (RD-02..06, P9-07A/B, P9-08): 100% ██████████ DONE — merged dff5671
Sprint-RD:                100% ██████████ RD-00..06 all done
P9 (Engagement Framework): 80%  ████████░░ P9-01..08 done; P9-09 open
Sprint-WF:                  0%  ░░░░░░░░░░ UNBLOCKED — next after P9-09
Sprint-FR:                  0%  ░░░░░░░░░░ UNBLOCKED — next after P9-09
Sprint-FE:                  0%  ░░░░░░░░░░ BLOCKED on FE-GATE-BA
```

**OVERALL: ~75% complete by task count (~92% by functional value)**

## CARRY_FORWARD_CONTEXT
Session 030 built Phase H (8 tasks):
- RD-02: template_selector.py — firm template upload/resolve
- RD-03: write_final_report() → BaseReportBuilder + section_overrides + versioning
- RD-04: _version_existing_report() → Previous_Versions/v{N}
- RD-05: investigation 13-section structure
- RD-06: FRM 7-section structure
- P9-07A: bootstrap loads default_language_standard
- P9-07B: LANGUAGE_STANDARD_BLOCKS + all 3 agent prompts
- P9-08: ReviewAgent + ReviewAnnotation + FRM done-stage badges

## BLOCKERS_AND_ENV_LIMITATIONS
- P9-09 is large — must decompose per workflow page at build time
- Sprint-FE still BLOCKED on FE-GATE-BA (needs /ba session — UX decisions for AI questions stage placement)
- Sprint-WF and Sprint-FR both unblocked; can run after P9-09 or in parallel
