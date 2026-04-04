# RISK REGISTER

## Format
| ID | Status | Category | Risk | Impact | Mitigation |
|----|--------|----------|------|--------|------------|

---

## Risks

| ID | Status | Category | Risk | Impact | Mitigation |
|----|--------|----------|------|--------|------------|
| R-001 | OPEN | API | Tavily free tier limited to 1000 searches/month — could exhaust during heavy testing | Medium | Cache all research results locally per case_id; add `use_cached` flag to research tools |
| R-002 | CLOSED | API | Anthropic API key not yet confirmed working in this environment | High | RESOLVED: API key active, smoke test passed Session 009 (2026-04-04) |
| R-003 | OPEN | ARCH | Arabic rendering in Rich terminal may not display correctly on all Mac/Windows terminals | Low | Test early with a sample bilingual output; have plain-text fallback |
| R-004 | OPEN | SCOPE | Proposal deck (PPT prompt pack) depends on undefined external tool `claude_ppt` | Low | Keep deck output as prompt files only (no direct PPT generation); document dependency clearly in README |
| R-005 | CLOSED | PROCESS | No task tracking system existed at project start | Low | Resolved: tasks/ scaffold created 2026-03-29 |
| R-006 | OPEN | AK_DECISION | docs/problem-definition.md and docs/scope-brief.md are stubs — no confirmed content | Medium | Requires /ba discovery session with AK to populate; blocks traceability-matrix completion |
| R-007 | OPEN | AK_DECISION | docs/hld.md has sections marked [TO VERIFY VIA /architect SESSION] — partial only | Low | Requires /architect session to fill gaps; currently sufficient for navigation |
| R-008 | OPEN | AK_DECISION | AKR-09 deferred: AK-Cognitive-OS skills/ directory contains v1.x format commands — cannot install without downgrading project | Low | Revisit only when AK-Cognitive-OS skills/ are updated to v2.0 format |
| R-009 | PARTIAL | PROCESS | No live smoke test run — 57 modules structural only, never tested with real API keys | High | PARTIAL: Option 4 (Policy/SOP) smoke test PASSED Session 009. Two bugs found and fixed (doc tool registration, has_documents guard). Option 6 (FRM) smoke test still pending. |
