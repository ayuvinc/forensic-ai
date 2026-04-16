# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Phase 8 — Streamlit Frontend (continued) + Architecture Improvements**

Build order (strict — each unblocks the next):
1. ARCH-INS-01 (severity-tagged events) — `streamlit_app/shared/pipeline.py` — 3 sub-tasks
2. ARCH-INS-02 (materialized case index) — `tools/file_tools.py` + `write_state()` — 3 sub-tasks
3. P8-08a..j — 10 remaining workflow pages (all depend on ARCH-INS-01)
4. P8-09a — Case Tracker page (depends on ARCH-INS-02)
5. P8-10a — Settings page
6. P8-11a — Document ingestion UI
7. P8-14a..f — End-to-end smoke test

ARCH-INS-03 (circuit breaker) — post Phase 8, pre-production. Do not start until P8-14 passes.

Manual verification AK must run before next build session:
- P8-00c: `python run.py` → Option 6 → confirm state advances to DELIVERABLE_WRITTEN
- P8-02d: Same — confirm FRM output identical to pre-split
- P8-05b: Check cases/{id}/ — final_report.* in root, *.v*.json in interim/
- P8-06e: `streamlit run app.py` → FRM page → A/F/R buttons visible and clickable

## CARRY_FORWARD_CONTEXT
Session 017 (planning only — no session-open run):
- Reviewed Transplant-workflow HLD/LLD (9-service EDA, strangler-fig, frontend integration LLD)
- Assessed forensic-ai % completion: 48%
- Identified 6 transferable patterns from Transplant architecture
- Wrote 3 high-priority architecture tasks into tasks/todo.md:
  - ARCH-INS-01: severity-tagged pipeline events (prerequisite for P8-08)
  - ARCH-INS-02: materialized case index (prerequisite for P8-09)
  - ARCH-INS-03: circuit breaker for Tavily/Anthropic (post-Phase 8)
- Updated Phase 8 dependency graph to include new prerequisites
- Patterns deferred for later: ResearchProvider adapter, dead-letter for failed runs

## BLOCKERS_AND_ENV_LIMITATIONS
- P8-12-EXCEL: MISSING_BA_SIGNOFF
- P8-13-TIER: MISSING_BA_SIGNOFF
- SRL-B-BA: MISSING_BA_SIGNOFF — behavioral matrix blocked
- FRM-R-00: MISSING_BA_SIGNOFF — custom risk areas blocked
- feature/P8-phase8-streamlit not pushed to remote
- Manual verification (P8-00c, P8-02d, P8-05b, P8-06e) requires live API key + streamlit installed
