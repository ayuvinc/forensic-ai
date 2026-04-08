# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
architect

## NEXT_TASK
**Phase 8 — Streamlit Frontend Migration**

Wire all 10 menu options as Streamlit sidebar navigation. Replace terminal UI with browser-based interface. Fixes UX problems confirmed in Session 015 P7-GATE test:
- Risk item review hidden behind spinner (FE-07)
- No clean case output view (FE-08)
- Word document branding (FE-09)

Start with /architect to design the Streamlit page map and component breakdown before any build begins. Phase 8 has 9 tasks (FE-01..09) and is a significant migration — plan mode required.

## CARRY_FORWARD_CONTEXT
Session 015 completed:
- Sprint-10L Phase A: MERGED — PM/Partner now receive RESEARCH_MODE; G-13/G-14 fixed
- P7-GATE: PASSED — FRM 2-module run in knowledge_only, no crash
- BUG-12: FIXED — FRM state now advances to DELIVERABLE_WRITTEN after pipeline
- Sprint-10K: MERGED — smart RESEARCH_MODE default, sanctions warning panel, mode banner, guardrails.md
- Sprint-10J: MERGED — 4 taxonomy JSON files (industries, frm_modules, jurisdictions, routing_table), prompt_with_options(), FRM intake uses taxonomy selectors

Deferred:
- Phase 8 (Streamlit) — next priority
- Sprint-10D (FRM guided exercise — BA-002 confirmed, Sprint-10J done)
- Sprint-10C (Historical library — BA-003 confirmed)
- Sprint-10L Phase B (behavioral matrix — MISSING_BA_SIGNOFF)
- FRM-R-00 (custom risk areas with stakeholder docs — MISSING_BA_SIGNOFF)
- AK: clarify what "extracted knowledge" to add to knowledge base (noted in next-action)

## BLOCKERS_AND_ENV_LIMITATIONS
- Sprint-10L Phase B: MISSING_BA_SIGNOFF — do not start
- FRM-R-00: MISSING_BA_SIGNOFF — extends BA-002, needs sign-off before build
- 6 stale feature branches — delete after confirming merged to main
- RESEARCH_MODE now defaults to live if TAVILY_API_KEY present — verify on next live run
