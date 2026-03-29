# NEXT ACTION

## NEXT_PERSONA
junior-dev

## TASK
Resolve external findings (persistence, Arabic, DocumentManager) and prepare for smoke test.
API keys are NOT required during development — smoke test will be run separately when keys are ready.

## CONTEXT
Sprint-02 QA gate passed (QR-01..15 all PASS). Codebase is structurally complete (57 modules).
Three external findings from Final Feedback review are now resolved in this sprint.

### Resolved This Session
- F-EXT-01 (Medium): Case persistence fixed — all guided intake paths (options 2–8) now call
  `_persist_intake()` which writes intake.json + state.json atomically.
- F-EXT-02 (Medium): Arabic README claims corrected — Arabic is now correctly documented as
  generated when `language=ar` is selected. `generate_arabic` context flag wired into
  investigation and FRM workflows.
- F-EXT-03 (Low): DocumentManager wiring fixed — options 2 and 6 now instantiate
  DocumentManager and pass it to workflows. Graceful fallback to None if init fails.

## Pre-Conditions for Smoke Test (deferred — do NOT block development on these)
- B-01: .env file with real ANTHROPIC_API_KEY and TAVILY_API_KEY
- B-02: `pip install -r requirements.txt` completes without errors

## SMOKE TEST ACCEPTANCE CRITERIA (run when keys are ready)
- [ ] S3-01 .env created with ANTHROPIC_API_KEY and TAVILY_API_KEY set
- [ ] S3-02 `pip install -r requirements.txt` completes without errors
- [ ] S3-03 `python run.py` reaches the 10-item Rich menu
- [ ] S3-04 Firm profile wizard completes, firm_profile/firm_profile.json written
- [ ] S3-05 FRM Risk Register (Option 6) completes for a test client → cases/{id}/final_report.en.md written
- [ ] S3-06 audit_log.jsonl has events for each pipeline stage
- [ ] S3-07 Resume: interrupt mid-run, restart, orchestrator detects and resumes
- [ ] S3-08 intake.json present in cases/{id}/ for all workflow paths (verify fix F-EXT-01)
