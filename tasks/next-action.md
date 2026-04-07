# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
junior-dev → then AK (P7-GATE manual run)

## NEXT_TASK
**REVISED PRIORITY (Monte Carlo Session 013):**

**Step 1 (junior-dev):** Build Sprint-10L SRL-01..04 — mode-aware PM + Partner review criteria.
G-13/G-14 cause 63% of all crashes. Fix this before running P7-GATE matrix.
Files: agents/project_manager/prompts.py, agents/project_manager/agent.py,
       agents/partner/prompts.py, agents/partner/agent.py

**Step 2 (AK, manual):** Run `python run.py` → Option 6 → complete FRM workflow end-to-end.
Run 3 consecutive times. All 3 must pass. This is P7-GATE.

**Step 3 (junior-dev, after P7-GATE):** Sprint-10K PPH-01a (RESEARCH_MODE smart default) + PPH-05
(require_citations=False for non-compliance workflows). Together as one commit.

**Step 4:** Run 16-position structured coverage matrix (positions assigned in Session 013).

## CARRY_FORWARD_CONTEXT
- Session 013: BUG-08/09/10/11 fixed + merged to main
- Monte Carlo (100 iter): 60% crash rate, trust→0 by iter 11, Nash equilibrium iter 3
- Dominant failure: G-13/G-14 (PM/Partner revision loop) — 38/60 crashes
- Sprint-10L (mode-aware review) now PRIORITY 1 ahead of PPH-05 and P7-GATE matrix
- Sprint-10J (taxonomy + modularity) and BA-014/015 confirmed — schedule after P7-GATE
- BA-013 (FRM as engagement suite) confirmed — schedule after Sprint-10L

## BLOCKERS_AND_ENV_LIMITATIONS
- G-13/G-14: PM/Partner reject knowledge_only output → loop exhaustion (Sprint-10L fix)
- G-07: require_citations=True in FRM live mode (PPH-05 fix — after Sprint-10L)
- P7-GATE: gated on Sprint-10L completing first

After P7-GATE passes → choose one of:
  A. Sprint-10D  — FRM guided exercise redesign (FRM-R-01..08) — HIGHEST product value
  B. Sprint-10C  — Historical Knowledge Library (HRL-00..06)
  C. FE-01..06   — Streamlit frontend migration

## CARRY_FORWARD_CONTEXT
- Session 012: Sprint-10E/10H/10F all COMPLETE, merged to main. 14 menu items.
- Session 013 (this): BUG-08 (find_relevant_docs) confirmed fixed from prior session. BUG-09 root cause
  diagnosed: Tavily SDK ignores timeout kwarg → 60s hang per attempt × 3 = 3min+ before fallback.
  Fix: RESEARCH_MODE=knowledge_only stubs all Tavily calls immediately.
- BA-013 confirmed: FRM Option 6 redesigned as engagement suite (Risk Register + Policy + Training).
  Implementation sprint TBD after P7-GATE.
- Codex review of Sprint-10E/10F DEFERRED — credits limited.

## BLOCKERS_AND_ENV_LIMITATIONS
- R-009: Sprint-10D GATED on P7-GATE (FRM smoke test — manual, requires live API keys)
- R-010: FRM redesign regression risk — do not start Sprint-10D without P7-GATE baseline
- BUG-09: Tavily SDK timeout kwarg silently ignored — RESEARCH_MODE flag is the fix (Sprint-10I)
