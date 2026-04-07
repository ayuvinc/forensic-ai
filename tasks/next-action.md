# NEXT ACTION

## SESSION
CLOSED

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Sprint-10L Phase A — complete remaining tasks on feature/sprint-10L-mode-aware-review-chain**

**Step 1 (junior-dev):** Fix SRL-02 defect in `agents/partner/prompts.py`:
- Add `research_mode: str = "knowledge_only"` param to `build_task_message()`
- When `research_mode == "live"`: append "Use regulatory_lookup to verify any regulatory claims before approving." to the task message
- When `research_mode == "knowledge_only"`: omit that line (model has no live tool access)

**Step 2 (junior-dev):** SRL-03a — `agents/project_manager/agent.py`:
- `from config import RESEARCH_MODE` at top
- Pass `research_mode=RESEARCH_MODE` to `prompts.build_system_prompt()` call in `__call__`

**Step 3 (junior-dev):** SRL-03b — `agents/partner/agent.py`:
- Same import
- Pass `research_mode=RESEARCH_MODE` to `prompts.build_system_prompt()` AND `prompts.build_task_message()`

**Step 4 (junior-dev):** Verify imports clean — run:
`python -c "from agents.project_manager.agent import ProjectManager; from agents.partner.agent import Partner; print('OK')"`

**Step 5 (AK, manual):** SRL-04 — P7-GATE:
Run `python run.py` → Option 6 → FRM → 2 modules → complete end-to-end.
Must pass 3 consecutive times with no G-13/G-14 crash.

## CARRY_FORWARD_CONTEXT
- Session 014: Sprint-10L scoped + split (Phase A = prompt fix, Phase B = behavioral matrix)
- SRL-01 done: agents/project_manager/prompts.py rewritten with RESEARCH_MODE-aware criteria
- SRL-02 written but defect: build_task_message() dropped regulatory_lookup instruction for live mode — must fix before merge
- Phase B (REVIEW_MODE + verdict spectrum + behavioral matrix) gated on P7-GATE + BA sign-off
- Feature branch: feature/sprint-10L-mode-aware-review-chain

## BLOCKERS_AND_ENV_LIMITATIONS
- SRL-02 defect must be fixed before any merge to main
- P7-GATE gated on Phase A completing (SRL-01..03b all merged)
- Sprint-10L Phase B: MISSING_BA_SIGNOFF — no BA entries for behavioral matrix in ba-logic.md
- Sprint-10K (PPH-01..04) gated on P7-GATE
- Sprint-10J (taxonomy) gated on P7-GATE
