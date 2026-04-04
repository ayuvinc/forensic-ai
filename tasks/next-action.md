# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
ba

## NEXT_TASK
Planning session with Maher — validate 3-level scope hierarchy, confirm top 3 service line priorities,
draft intake questionnaire structures (8–12 questions each), review knowledge file scope, design chaining UX.
Run /ba then /architect. This gates Phases 10–12.

PLANNING AGENDA ADDITIONS (from Session 009 close — PRIORITY 1 FIRST):

0. [PRIORITY 1] FRM guided-exercise redesign — current one-shot generation is fundamentally wrong.
   Design the FRM as a structured assessment conversation:
   Step 1: Show plan — "Here are the 8 modules. We will cover X, Y, Z based on your scope."
   Step 2: Per module — present risk sub-areas, ask which apply to this client/industry
   Step 3: Per risk area — ask: any known incidents? existing controls? probability (1-5)? impact (1-5)?
   Step 4: Model generates the risk item from consultant's answers + regulatory baseline
   Step 5: Consultant reviews each risk item — approve / modify / skip
   Step 6: Final register assembled from confirmed items
   Zero-information case: model shows the framework, presents industry-baseline risks as DRAFT,
   consultant confirms/adjusts each one before it goes into the register.
   This same pattern applies to: Investigation Report scoping, Due Diligence checklist, Transaction Testing scope.
   Design question for planning: which steps are conversational vs form-based in Streamlit UI?
1. Zero-information draft design: define "content floor" per workflow — what the engine produces when
   consultant provides no documents and minimal intake. E.g. FRM → industry-baseline risks from knowledge file.
   Every workflow must return a usable starting-point draft, never a blank deliverable.
   Design question: for each scope type (FRM, Investigation, Policy, Proposal, Transaction Testing, etc.)
   what are the 5–15 baseline items the engine can always populate from domain knowledge alone?
2. Apply same principle to investigations: if no documents, engine drafts from publicly known facts +
   asks targeted questions to fill gaps. Partner/PM review still applies.
3. Context limit hygiene: sessions must close before 80% context. Check at session-open.

## CARRY_FORWARD_CONTEXT
- Session 009 closed. Smoke test PASSED (Option 4 — Whistleblower Policy). Word output wired in.
- 4 bugs fixed: doc tool filter, has_documents() guard, JSON code-block parsing, doc manager hallucination guard.
- Scope expanded from 7 phases to 12 phases. Completion: 48%.
- Streamlit (Option A) confirmed as frontend.
- FRM full smoke test (Option 6) still pending — aborted mid-run to save API tokens.
- KF-00 (knowledge/policy_sop/) is the quickest quality win — policy prompt produces 8/10 draft
  missing 8 predictable gaps; adding knowledge file + prompt checklist will close them.
- Planning session required before building Phases 10–12 (new service lines, precision intake, knowledge files).

## PARALLEL_QUICK_WIN
If Maher not available for planning session, next best task is:
KF-00 — Create knowledge/policy_sop/framework.md and knowledge/policy_sop/sources.md to fix the
8 gaps identified in ChatGPT review of Whistleblower Policy output (Session 009).
Gaps: anonymous complaint protocol, retaliation mechanism + disciplinary matrix, evidence/chain-of-custody,
SLA for closure comms, malicious vs good-faith definition, DPDP Act 2023, vendor enforcement, metrics/KPIs.

## BLOCKERS_AND_ENV_LIMITATIONS
- Phase 10–12 GATED on planning session with Maher.
- Phase 7 GATED on FRM full smoke test (P7-GATE) — needs 1-module FRM run to verify quality.
- QR-17 (document ingestion live test) still pending.
- C-06a–e (integration tests) can run without API key.

## HANDOFF_NOTE
Session 009 closed by session-close. Option 4 smoke test PASSED. Scope expanded (Phases 8–12).
Next: planning session with Maher (BA + Architect) to gate Phases 10–12.
If blocking: KF-00 or C-06a can start immediately without waiting for planning session.
