# Session 004 — Sprint Summary

## Sprint
- sprint_id: sprint-03 (continued — C-03 remediation)
- session_id: 004
- date: 2026-04-02
- mode: SOLO_CLAUDE

## Objective
Codex finding C-03 remediation: evidence-chain enforcement moved from prompt-instruction to runtime code. QR-16 added and passed (7/7 sub-checks).

## Tasks Covered
- C-03a: Partner agent — _enforce_evidence_chains() overrides approved=True when FindingChain references LEAD_ONLY/INADMISSIBLE evidence (agents/partner/agent.py)
- C-03b: Post-hook enforce_evidence_chain added to POST_HOOKS (position 2, between validate_schema and persist_artifact) — HookVetoError on bad chain (hooks/post_hooks.py)
- C-03c: Evidence items threaded via closure in partner_fn; _build_evidence_items() converts DocumentEntry→EvidenceItem (workflows/investigation_report.py)
- C-03d: QR-16 — 7/7 sub-checks PASS: validate_finding_chain rejects LEAD_ONLY, hook vetoes bad approval, passes approved=False, passes PERMISSIBLE, no-op for FRM, no-op without evidence_items, agent-level override works
- F-EXT-01: _persist_intake() added to run.py — intake.json and initial state.json written for options 2–8 (partial C-02 fix)
- F-EXT-02: Arabic output claims corrected (partial C-05 fix)
- F-EXT-03: DocumentManager wired into options 2 and 6 in run.py (partial C-04 fix)

## Files Changed
- agents/partner/agent.py — _enforce_evidence_chains()
- hooks/post_hooks.py — enforce_evidence_chain hook added
- workflows/investigation_report.py — _build_evidence_items(), closure threading
- run.py — _persist_intake(), DocumentManager integration

## Tests Added/Updated
- QR-16: 7/7 sub-checks PASS (evidence chain enforcement end-to-end)

## Acceptance Criteria Mapping
- C-03a: approved=True blocked when LEAD_ONLY/INADMISSIBLE referenced — PASS
- C-03b: HookVetoError raised on bad chain — PASS
- C-03d: All 7 sub-checks PASS — PASS

## Security Decisions
- Evidence chain enforcement is now a hard code-level gate, not a prompt suggestion. Partner cannot approve findings with inadmissible evidence regardless of LLM output.

## Risks / Tradeoffs
- C-01, C-02, C-04, C-05, C-06, C-07 remain open (deferred to sprint-04)
- F-EXT-01/02/03 are partial fixes — full remediation items remain in sprint-03 backlog
- No live smoke test with real API keys — R-002 still open
