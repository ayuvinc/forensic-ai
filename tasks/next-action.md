# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
junior-dev

## NEXT_TASK
Sprint-10A (ARCH-S-01 + ARCH-S-07) — schemas build. Two tasks, no dependencies, can start immediately:
1. ARCH-S-01: Add RiskContextItem to schemas/artifacts.py
2. ARCH-S-07: Add SanitisedIndexEntry to schemas/artifacts.py
3. ARCH-S-06: Add SanitisationError to tools/knowledge_library.py (scaffold only)

Run these three in sequence (ARCH-S-01 + ARCH-S-07 touch the same file; ARCH-S-06 is a separate file). After: ARCH-S-02 (schemas/dd.py), ARCH-S-03 (schemas/transaction_testing.py), ARCH-S-04 (schemas/engagement_scope.py), ARCH-S-05 (state_machine.py).

Parallel with schemas: KF-00 (knowledge/policy_sop/framework.md) — no code deps, pure content.

## CARRY_FORWARD_CONTEXT
- Session 011: Architect session. Sprint-10A schema gaps closed (ARCH-S-06, ARCH-S-07 added). docs/hld.md populated — no longer a stub.
- Sprint-10A..10H design is complete and AK-approved. Build queue is OPEN.
- Critical path: Schemas (10A) → Knowledge Files (10B, parallel) → Historical Library (10C) → FRM Redesign (10D) → Service Lines (10E) → Scoping (10F) → Chaining (10G, gated on Phase 8) → Disclaimers (10H, parallel with E/F)
- FRM smoke test (P7-GATE) still pending — must pass before FRM-R-01..08 merge. Do not start FRM-R-01 until P7-GATE passes.
- QR-17 (document ingestion live test) still pending — gated on live API keys.
- SanitisationError location: tools/knowledge_library.py (module-level), not schemas/ — avoids circular dep.
- SanitisedIndexEntry: schemas/artifacts.py — no PII fields by model definition (enforced structurally).

## BLOCKERS_AND_ENV_LIMITATIONS
- FRM-R-01..08 GATED on P7-GATE (FRM smoke test baseline passing).
- Sprint-10G (Chaining) GATED on Phase 8 (Streamlit) completion.
- SCOPE-WF-01 GATED on KF-NEW (engagement_taxonomy knowledge file).
- SL-GATE-01..03 GATED on respective knowledge files (KF-02, KF-04, KF-01).

## HANDOFF_NOTE
Architect session complete. Sprint-10A..10H fully designed and AK-approved. docs/hld.md written. ARCH-S-06 + ARCH-S-07 added to Sprint-10A. Build queue open.
Recommended parallel start: (1) ARCH-S-01+ARCH-S-07+ARCH-S-06 in sequence → then ARCH-S-02..05; (2) KF-00 independently.
