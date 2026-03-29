# RISK REGISTER

## Format
| ID | Status | Category | Risk | Impact | Mitigation |
|----|--------|----------|------|--------|------------|

---

## Risks

| ID | Status | Category | Risk | Impact | Mitigation |
|----|--------|----------|------|--------|------------|
| R-001 | OPEN | API | Tavily free tier limited to 1000 searches/month — could exhaust during heavy testing | Medium | Cache all research results locally per case_id; add `use_cached` flag to research tools |
| R-002 | OPEN | API | Anthropic API key not yet confirmed working in this environment | High | Run `python -c "import anthropic; print(anthropic.__version__)"` at session start to verify |
| R-003 | OPEN | ARCH | Arabic rendering in Rich terminal may not display correctly on all Mac/Windows terminals | Low | Test early with a sample bilingual output; have plain-text fallback |
| R-004 | OPEN | SCOPE | Proposal deck (PPT prompt pack) depends on undefined external tool `claude_ppt` | Low | Keep deck output as prompt files only (no direct PPT generation); document dependency clearly in README |
| R-005 | CLOSED | PROCESS | No task tracking system existed at project start | Low | Resolved: tasks/ scaffold created 2026-03-29 |
