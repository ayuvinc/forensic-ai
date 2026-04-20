# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 030: junior-dev builds Phase H (RD-02..06, P9-07A/B, P9-08)**

Phase G complete and merged (9f83126 → main). 131 tests pass (no regression).
Phase H is unblocked. RD-01 (BaseReportBuilder) now available — unblocks RD-02..06.

**Phase H — primary tasks:**

  RD-02: New file `streamlit_app/shared/template_selector.py` — `render_template_selector(workflow_type: str)`.
    Checks `firm_profile/firm.json["templates"][workflow_type]`. If no template set:
    renders two buttons: "Use my template" (st.file_uploader for .docx) / "Use default".
    On upload: saves to `firm_profile/templates/{workflow_type}.docx`; updates firm.json["templates"].
    Returns the resolved template path (str | None).

  RD-03: Update `tools/file_tools.py:write_final_report()` — call BaseReportBuilder to produce the
    .docx output instead of OutputGenerator. Load template via firm.json["templates"][workflow] if set.
    Apply section_overrides dict (passed as new param). Call _version_existing_report() before writing.
    Keep existing markdown (.md) write unchanged.

  RD-04: New function `tools/file_tools.py:_version_existing_report(case_id: str)` — if
    `final_report.*.md` or `final_report.*.docx` exist in the write destination (F_Final/ for AF,
    root for legacy): move them to `Previous_Versions/final_report.v{N}.*`; create `Previous_Versions/`
    if missing. Called by RD-03 before each write. Return highest version number used.

  RD-05: Investigation section overrides — in `workflows/investigation_report.py`, after pipeline
    completes, build a section_overrides dict with the 13-section structure (per BA-R-05) and pass
    to write_final_report(). No new files — modify existing workflow.

  RD-06: FRM section overrides — in `workflows/frm_risk_register.py`, after pipeline completes,
    build section_overrides with Risk Register Table + summary sections and pass to write_final_report().
    No new files — modify existing workflow.

  P9-07A: Add "Default Language Standard" selectbox to `pages/14_Settings.py`:
    - 4 options: "ACFE Internal Review" / "Expert Witness" / "Regulatory Submission" / "Board Pack"
    - Key values: "acfe" / "expert_witness" / "regulatory" / "board_pack"
    - Save writes `firm_profile/firm.json["default_language_standard"]`; existing fields preserved.
    - Bootstrap (streamlit_app/shared/session.py) loads value into st.session_state.default_language_standard.

  P9-07B: New file `agents/shared/language_standards.py` — `LANGUAGE_STANDARD_BLOCKS: dict[str, str]`.
    4 entries per spec (acfe / expert_witness / regulatory / board_pack).
    Update `agents/junior_analyst/prompts.py`, `agents/project_manager/prompts.py`,
    `agents/partner/prompts.py`: build_system_prompt() accepts `language_standard: str = "acfe"`;
    appends the relevant block. All three __call__() methods pass context.get("language_standard","acfe").

  P9-08: New dir `agents/reviewer/` + `review_agent.py`:
    - ReviewAnnotation schema in schemas/artifacts.py: finding_id, support_level (supported/partially_supported/unsupported), evidence_cited list, logic_gaps list, rewritten_text Optional[str].
    - ReviewAgent.__call__(draft, context) → list[ReviewAnnotation]: iterates findings; classifies support level; finding with citations=[] auto-classified "unsupported" without model call; rewrites per language_standard.
    - Wire into orchestrator: after Partner approval, before final report write.
    - Streamlit: in FRM done stage, add support_level badge (green/amber/red) per risk item.
    - Stored to D_Working_Papers/ai_review_{YYYYMMDD}.json.

**Phase H — acceptance criteria highlights:**
  RD-02: render_template_selector() returns resolved path; saves to firm.json on upload; no crash if firm.json missing templates key
  RD-03: write_final_report() calls BaseReportBuilder; _version_existing_report() called before write; section_overrides param accepted
  RD-04: existing final_report.* moved to Previous_Versions/v{N} before each write; Previous_Versions/ created if absent
  RD-05: Investigation pipeline final output uses 13-section structure (code inspection)
  RD-06: FRM pipeline final output uses section_overrides (code inspection)
  P9-07A: Settings page has selectbox with 4 options; save updates firm.json without clobbering existing fields; bootstrap sets session_state.default_language_standard
  P9-07B: LANGUAGE_STANDARD_BLOCKS has 4 keys; build_system_prompt("expert_witness") includes "court-ready"; missing language_standard defaults to "acfe" (no KeyError)
  P9-08: ReviewAnnotation importable from schemas.artifacts; support_level="invalid" raises ValidationError; finding with citations=[] → "unsupported" without API call; D_Working_Papers/ai_review_{date}.json written; badges visible in FRM done stage

**Gates:**
  RD-02: No gates.
  RD-03: Depends on RD-01 (done) + RD-04 (same session).
  RD-04: No gates — helper function, no deps.
  RD-05/06: Depends on RD-03.
  P9-07A/B: No gates.
  P9-08: Depends on P9-07B (language_standard in context).

## COMPLETION STATUS

```
Phase 1-8 + Sprints A-G: 100% ██████████ DONE — all merged
Phase G (P9-04c/d, P9-05, P9-06, RD-01): 100% ██████████ DONE — merged 9f83126
Sprint-RD:                50%  █████░░░░░ RD-00/01 done; RD-02..06 next (Phase H)
P9 (Engagement Framework): 60%  ██████░░░░ P9-01..06 done; P9-07/08/09 open
Sprint-WF:                  0%  ░░░░░░░░░░ GATED on RD-01 ← now unblocked
Sprint-FR:                  0%  ░░░░░░░░░░ GATED on RD-01 + P9-05 ← both done
Sprint-FE:                  0%  ░░░░░░░░░░ BLOCKED on FE-GATE-BA
```

**OVERALL: ~70% complete by task count (~88% by functional value)**

## CARRY_FORWARD_CONTEXT
Session 029 built Phase F + Phase G (12 tasks total):

Phase F (merged 4315d2a):
- CONV-01/02: EvidenceChat backend + shared panel
- AIC-01/02/03: post-intake Q&A + pre-run review + ProjectManager context methods
- P9-04a/b: AF_FOLDERS + is_af_project()

Phase G (merged 9f83126):
- P9-04c/d: AF artifact routing (E_Drafts, F_Final) + migration path
- P9-05: pages/16_Workspace.py — full Input Session workspace
- P9-06: DocumentManager context accumulation (75% threshold → Haiku summary)
- RD-01: BaseReportBuilder with template fallback + atomic save

131 tests pass throughout. 1 defect fixed (Phase F AIC-01 chat_message rendering).

## BLOCKERS_AND_ENV_LIMITATIONS
- Sprint-WF (WF-01..05) and Sprint-FR (FR-01..06) now unblocked by RD-01 — can run in Phase H or H+1
- Sprint-FE still BLOCKED on FE-GATE-BA (needs /ba session — UX decisions for AI questions stage placement)
- P9-09 (wire all workflow pages) should follow P9-07B and P9-08 — schedule for Phase I
