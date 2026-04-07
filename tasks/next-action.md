# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
junior-dev

## NEXT_TASK
Sprint-10F — Engagement Scoping Workflow

Build `workflows/engagement_scoping.py`:
- 5-step problem-first flow per BA-010
- Reads `knowledge/engagement_taxonomy/framework.md` at runtime
- Produces `ConfirmedScope` (schemas/engagement_scope.py — already built)
- Routes to existing workflow via run.py dispatch
- Add Option 0 "Scope New Engagement" entry point to run.py + menu

Task IDs:
- SCOPE-WF-01: workflows/engagement_scoping.py
- SCOPE-WF-02: run.py / menu — add Option 0 entry point

Gates: KF-NEW ✓ (merged) | ARCH-S-04 ✓ (merged) — FULLY UNBLOCKED

## CARRY_FORWARD_CONTEXT
- Session 012: todo.md decongested (75% token reduction), releases/completed-tasks.md created
- Branches merged: feature/sprint-10A-schemas-kf00 + feature/sprint-10B-knowledge-files → main
- Sprint-10H COMPLETE: templates/disclaimer_licensed_db.md + templates/disclaimer_humint_scope.md
- Sprint-10E COMPLETE: workflows/due_diligence.py, sanctions_screening.py, transaction_testing.py — all import clean, wired to menu options 11/12/13
- Menu now 13 items (was 10): added DILIGENCE category (11/12/13)
- Codex review of Sprint-10A/10B DEFERRED — credits limited; review when weekly limit resets
- Next after 10F: Sprint-10D (FRM guided exercise redesign) — BUT only after P7-GATE (FRM smoke test)

## BLOCKERS_AND_ENV_LIMITATIONS
- R-009: FRM smoke test still pending — Sprint-10D gated
- R-010: FRM redesign regression risk — do not start Sprint-10D without baseline smoke test
- Codex review deferred (credits) — structural QA not yet run on Sprint-10E code
