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
| R-009 | MITIGATED | PROCESS | No live smoke test run — 57 modules structural only, never tested with real API keys | High | MITIGATED Session 015: P7-GATE PASSED — FRM Option 6 complete (knowledge_only, 2 modules, no crash, final_report.en.md written). Option 4 passed Session 009. Core pipeline confirmed working. Live-mode (TAVILY) run still pending but not a blocker. |
| R-010 | OPEN | ARCH | FRM guided exercise redesign (Sprint-10D) touches workflows/frm_risk_register.py and schemas/artifacts.py — regression risk to existing FRM pipeline if refactor is not isolated correctly | High | Mitigation: FRM-R-01..08 must be built behind a feature flag or new workflow path until P7-GATE (FRM smoke test) has a baseline passing run to compare against |
| R-011 | OPEN | ARCH | tools/knowledge_library.py sanitisation — if PII stripping logic is incomplete, client names or passport numbers from historical reports could surface in new engagement outputs | High | Mitigation: ARCH-S-02 schema defines PII fields explicitly; sanitise() validates stripped output against known PII field list before writing index entry; SanitisationError hard gate |
| R-012 | OPEN | SCOPE | 35+ new tasks in Sprint-10A–10H represent 2–3x the volume of work already completed; scope creep risk if all tasks attempt to start simultaneously | Medium | Mitigation: critical path enforced (Schemas → KFs → Library → Workflows); next session starts with ARCH-S-01 + KF-00 only |
| R-013 | OPEN | PROCESS | docs/hld.md still has sections marked [TO VERIFY VIA /architect SESSION] — partially addressed but not updated this session | Low | Next architect session should update hld.md with Phase 10–13 architecture decisions before Sprint-10E/F/G builds begin |
| R-014 | OPEN | ARCH | FRM workflow split (P8-02) refactors run_frm_workflow() body — risk that CLI behaviour changes or run_frm_workflow() no longer calls review loop correctly | High | Mitigation: P8-02d is a mandatory CLI smoke test before P8-06-FRM begins. run_frm_workflow() signature must be byte-for-byte identical. |
| R-015 | OPEN | ARCH | Long FRM pipeline (2–3 min) with coarse on_progress calls — browser spinner may show no updates for extended periods, user assumes crash | Medium | Mitigation: ensure on_progress is called per module AND per agent step (Junior/PM/Partner labels). Currently called at module level only. |
| R-016 | OPEN | SECURITY | Streamlit default binding is 0.0.0.0:8501 — case data (firm_profile, case reports) visible on LAN if machine is on shared network | Low | Mitigation: document in README that `streamlit run app.py --server.address=localhost` is required, or add .streamlit/config.toml with address=localhost committed to repo. |
| R-017 | OPEN | ARCH | FE-08 interim migration uses shutil.move() — not atomic; process kill mid-migration leaves mixed state (some v*.json in root, some in interim/) | Low | Mitigation: best-effort migration acceptable — artifacts still readable in both locations; case_tracker must tolerate files in either location. |
| R-018 | OPEN | PROCESS | pages/ numbering skips 1 (0_Scope, 2_Investigation…) — sidebar ordering gap is cosmetic but may confuse if pages are reordered later | Low | Mitigation: renumber pages sequentially at P8-08 task time; architect to confirm final numbering before build. |
