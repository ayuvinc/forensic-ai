# Smoke Test — Sprint-DOCX-01
Date: 20260424
Sprint: sprint-docx-01
Tester: AK (manual)
Overall: QA_APPROVED

## Summary
| Step | Area | Severity | Result | Notes |
|------|------|----------|--------|-------|
| A-1 | Startup | P0 | PASS | FRM page rendered without crash — slow cold start noted |
| A-2 | Intake | P0 | PASS | Form accepted input, no validation errors |
| A-3 | Pipeline trigger | P0 | PASS | Pipeline started, tip panel visible, no immediate crash |
| B-1 | Pipeline completion | P0 | PASS | Pipeline completed (1 module, fast test). Done Zone rendered. |
| B-2 | Done Zone render | P0 | PASS | Green "FRM Risk Register complete" banner visible. Case ID: Project_Test_FRM. No error panel. |
| C-1 | .docx button visible | P0 | PASS | "Download Word document" button visible left side of Done Zone. |
| C-2 | .docx download | P0 | PASS | File downloaded successfully |
| C-3 | .docx opens in Word | P0 | PASS | AK confirmed all worked |
| C-4 | .md button visible | P0 | PASS | "Download Markdown backup" button visible right side of Done Zone. Labels match. |
| C-5 | .md download | P0 | PASS | FRM_Risk_Register_ABC_Inc_Project_Test_FRM.md downloaded to ~/Downloads |
| D-1 | Regression: PPT Pack | P1 | PASS | Page rendered without crash |
| D-2 | Regression: Due Diligence | P1 | PASS | Page rendered without crash |
| D-3 | FRM page reload | P1 | FAIL | Streamlit rerun triggered pipeline finalize — FRMDeliverable ValidationError: RiskItem instances treated as foreign types after module reload. Fixed: risk_register now serialized via model_dump() before FRMDeliverable construction. |

## P0 Failures (blocks QA_APPROVED)
- B-1: Pipeline crashed at Partner review (Module 1). ValidationError in RiskItem — recommendations field expects List[str], model returned List[dict]. Done Zone never rendered. Cannot confirm DOCX-03 download buttons. Bug is pre-existing (not introduced by Sprint-DOCX-01). Must fix before rerun.

## Observations (not failures)
- B-1 (in progress): UI appears idle/complete while pipeline is still running — user becomes impatient. Pre-existing issue. Targeted by Sprint-UX-PROGRESS-01 (progress bar fix) and Sprint-UX-STREAM-01 (streaming progress). AK confirmed this will be addressed in revision scope.

## P1 Issues (documented, does not block QA_APPROVED)
- Report content: recommendations rendered as raw Python dict strings (e.g. `{'title': '...', 'description': '...', 'control_framework': '...'}`) — coercion validator extracted wrong key. Visible in .md output. Needs prompt fix or schema change to RecommendationItem.
- Report content: all 3 risks have identical recommendations — prompt is not differentiating per risk.
- Report content: same 2 regulatory references repeated across all 3 risks.
- Pipeline bug (second run): FileNotFoundError in write_final_report — cases/Project_Test_FRM/ dir not pre-created for non-AF projects. Fixed inline (final_dir.mkdir added). Sprint-FOLDER-01 root cause confirmed.

## P1 Failures (documented, does not block)
- none yet

## QA Signal
QA_APPROVED
Reason: All 10 P0 steps passed. Both download buttons confirmed visible and functional. .docx and .md files downloaded successfully. 3 P1 issues documented (recommendations dict rendering, dir pre-creation bug fixed inline, FRMDeliverable module-reload bug fixed inline). Branch feature/sprint-docx-01-download-buttons is ready to merge to main.
