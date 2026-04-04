# Session 009 — Smoke Test + Scope Expansion

**Date:** 2026-04-04
**Sprint:** Sprint-09 (Smoke Test + Scope Expansion)
**Status:** CLOSED

---

## What Was Done

### Smoke Test (Live API — Option 4 Policy/SOP)

End-to-end smoke test run with live Anthropic + Tavily API keys.

**Option 4 (Policy/SOP) — Whistleblower Policy — PASSED**
- Whistleblower Policy for UAE firm generated
- 4 authoritative citations included
- `final_report.en.md` written to cases/{id}/
- `final_report.en.docx` written (Word output wired in)
- Audit log populated correctly
- State machine: INTAKE_CREATED → DELIVERABLE_WRITTEN

**Option 6 (FRM) — ABORTED** — JSON parsing confirmed working but full run stopped mid-way (token cost). Not a failure — bug root cause identified and fixed before run.

---

## Bugs Found and Fixed

| Bug | Root Cause | Fix |
|-----|-----------|-----|
| BUG-02 | `find_relevant_docs` tool declared but not registered when no DocumentManager → `ToolNotFoundError` | `_DOC_TOOL_NAMES` filter in all 3 agents' `get_tool_definitions(document_manager=None)` |
| BUG-03 | `DocumentManager.read_excerpt()` raised `FileNotFoundError` when PM hallucinated a case_id as doc_id | `has_documents()` guard in run.py; `read_excerpt()` returns graceful message instead of raising |
| BUG-04 | Model wraps JSON output in `` ```json `` code blocks; original regex matched raw JSON but failed to parse | `_parse_output()` in `junior_analyst/agent.py` extracts from code block first, then fallback |
| BUG-05 | Empty `DocumentManager` (no docs) passed to agents → model hallucinated doc_ids | `active_doc_manager = None` guard in run.py; only pass manager when `has_documents()` is True |

---

## Features Added

- **Word output**: `write_final_report()` in `tools/file_tools.py` now auto-generates `.docx` alongside `.md`. Graceful skip if python-docx unavailable.

---

## Scope Expansion Decisions

| Decision | Detail |
|----------|--------|
| Frontend | Streamlit (Option A) confirmed — 3-5 days, Python-native, browser-based |
| Workflow chaining | Same case_id approach — follow-on workflows appended to existing case |
| New service lines | 7 new scopes: Transaction Testing, Due Diligence, Fraud Audit, Sanctions Screening, ESI Review, Expert Witness, HUMINT |
| Scope hierarchy | 3 levels: Service Line → Engagement Type → Specific Deliverable |
| Precision intake | 8–12 questions per scope type (requires planning session) |
| Knowledge files | 8 new knowledge directories (KF-00..KF-07); KF-00 (policy_sop) is quickest win |
| Planning session | BA + Architect session required before building Phases 10–12 |

---

## Completion Assessment

**Old scope completion (Phases 1–7):** 78% structural, ~48% live-verified

**New scope completion (Phases 1–12):** 48% overall
- Phases 1–6: COMPLETE (structural, 57 modules)
- Phase 7: GATED (blank framework packaging — needs FRM full smoke test)
- Phases 8–12: PENDING (frontend, chaining, new service lines, intake, knowledge files)

---

## Lessons Recorded

1. **[CODE]** Policy/SOP prompt produces strong 8/10 first draft but misses 8 predictable gaps — added as mandatory checklist target for KF-00.
2. **[PROCESS]** Mode B workflows produce strong working drafts, not final output. Position as "80% done in 2 minutes" — consultant fills gaps as SME.

---

## Risks Updated

- **R-002**: CLOSED — API key active, smoke test passed
- **R-009**: PARTIAL — Option 4 passed, Option 6 still pending

---

## Open Items Carried Forward

- P7-GATE: FRM full smoke test (Option 6) — run with 1 module only to verify quality
- C-06a–e: Integration tests (no API key needed)
- FE-01..FE-06: Streamlit frontend implementation
- KF-00: knowledge/policy_sop/ (quickest win — fixes policy quality immediately)
- Planning session with Maher: scope hierarchy, intake questionnaires, knowledge files
- QR-17: Document ingestion path still not live-tested
