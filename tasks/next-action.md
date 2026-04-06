# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
session-close

## NEXT_TASK
Close Session 010. BA planning complete, architecture complete. No build work started this session — planning only.

Sprint-10 is fully designed. Build queue in dependency order:
1. Sprint-10A (Schemas) — ARCH-S-01 through ARCH-S-05 — no deps, build first
2. Sprint-10B (Knowledge Files) — KF-NEW, KF-02, KF-04, KF-01, KF-00 — parallel with schemas
3. Sprint-10C (Historical Library) — HRL-00 then HRL-01..06 — after ARCH-S-01
4. Sprint-10D (FRM Guided Exercise) — FRM-R-01..08 — after ARCH-S-01
5. Sprint-10E (New Service Lines) — SL-GATE-01..03 — after schemas + knowledge files
6. Sprint-10F (Engagement Scoping) — SCOPE-WF-01/02 — after KF-NEW + ARCH-S-04
7. Sprint-10G (Chaining) — CHAIN-00..02 — after Phase 8 (Streamlit)
8. Sprint-10H (Disclaimers) — ARCH-GAP-01/02 — parallel with workflows

## CARRY_FORWARD_CONTEXT
- Session 010 was a pure planning session — BA + Architect. Zero code written.
- 10 BA entries confirmed (BA-002 through BA-011) in tasks/ba-logic.md.
- 35+ tasks written to tasks/todo.md (Sprint-10A through 10H).
- docs/problem-definition.md and docs/scope-brief.md are now populated (no longer stubs).
- AKR-08b (/architect session to fill docs/hld.md gaps) is partially addressed — hld.md not yet updated this session; should be updated next architect session.
- FRM smoke test (Option 6, P7-GATE) still pending — needs real API keys, not blocked by planning.
- QR-17 (document ingestion live test) still pending.
- CE Creates DD reports on Desktop/GoodWork/ are the designated seed data for the DD historical library — Maher to run HRL-01 import wizard once it's built.
- GoodWork_Pilot_Proposal_Draft.docx = separate product (B2B training programme) — not in scope for forensic-ai/ build; flag for future product roadmap discussion.

## BLOCKERS_AND_ENV_LIMITATIONS
- Phase 10–13 build GATED on AK review and approval of architecture (tasks/todo.md Sprint-10A through 10H).
- Sprint-10G (Chaining) GATED on Phase 8 (Streamlit) completion.
- SCOPE-WF-01 GATED on KF-NEW (engagement_taxonomy knowledge file).
- SL-GATE-01 through SL-GATE-03 GATED on respective knowledge files (KF-01, KF-02, KF-04).
- FRM smoke test (P7-GATE) still pending — must pass before FRM guided exercise redesign is merged.

## HANDOFF_NOTE
Session 010 closed by session-close after BA + Architect. No code changes this session.
Next session: begin Sprint-10A (schemas) or Sprint-10B (knowledge files) — both have zero dependencies and can start immediately.
Recommended start: ARCH-S-01 (RiskContextItem) + KF-00 (policy_sop quick win) in parallel — shortest path to FRM redesign + policy quality fix.
