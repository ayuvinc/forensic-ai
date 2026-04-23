# Codex Review Handoff — 2026-04-23

## Instruction for Claude

Claude must review these Codex comments before selecting or executing the next sprint.

After review, Claude should propose concrete actions for Aditya's approval. Do not delete this file until Aditya has approved the proposed actions. Once Aditya approves and the actions are either completed or intentionally deferred, delete this file as part of cleanup.

## Review Summary

Codex performed a pragmatic repository exploration on 2026-04-23. The repo is functionally healthy but not release-clean.

## Positive Findings

- Main pytest suite passes: `131 passed, 19 warnings` on Python 3.13.12.
- Static compilation passes across `app.py`, `core`, `agents`, `streamlit_app`, `pages`, `workflows`, `schemas`, `tools`, and `tests`.
- Product architecture is coherent: Streamlit app, workflow pages, orchestrator, schemas, tools, local project/case storage.
- Crash reporter implementation is directionally sound: `streamlit_app/shared/crash_reporter.py` writes structured JSON, captures sanitized session context, and avoids reading case content.
- Repository hygiene is mostly sensible: `.env`, `cases/`, `firm_profile/`, pycache, and generated crash JSON are ignored.

## Risks and Required Review

### 1. Git State Is Not Release-Clean

`main` is ahead of `origin/main` by 7 commits and has a large dirty worktree:

- 17 modified Streamlit pages.
- New crash reporter file.
- Large `simulation/` archive move.
- New empirical files under `tests/`.
- Modified `.gitignore`, `streamlit_app/shared/pipeline.py`, and `tasks/ba-logic.md`.

Claude should decide whether to commit, split, or park these changes before starting new sprint work.

### 2. Rescued Empirical Files Are Not Pytest-Collected

The moved empirical files under `tests/` define runner helpers such as `run_all_orchestrator_tests()` and `run_all_hook_tests()`, but they do not define pytest-discoverable `def test_*` functions.

Result: `pytest` passes, but it does not validate those empirical checks.

Claude should either:

- Add pytest wrappers for the empirical checks.
- Keep them as manual runners but document and gate them explicitly.
- Move them out of pytest naming if they are not meant to be collected.

### 3. Orchestrator Empirical Failure: Revision Limit Expectation Mismatch

Manual empirical run produced:

`E3.3 FAIL — NO EXCEPTION RAISED — junior_calls=3, pm_calls=2 — MAX_REVISION_ROUNDS not enforced`

Observed code intentionally promotes the best available junior draft to Partner after PM revision limit:

`core/orchestrator.py` around the PM revision-limit branch returns a draft with `revision_limit_reached=True` instead of raising.

Claude should decide whether the empirical test expectation is stale or whether the product rule is wrong. This should be resolved before treating the empirical suite as a quality gate.

### 4. Evidence-Chain Enforcement Still Looks Weak

Manual empirical hook run showed:

- Bad evidence IDs were not blocked.
- Non-permissible evidence was not blocked.

This aligns with older Codex concern C-03: evidence-chain enforcement may still be prompt-enforced rather than runtime-enforced.

Claude should inspect the partner path, post-hooks, and evidence classifier before declaring this closed.

### 5. Offline Embedding Behavior Needs Smoke Coverage

Manual empirical run attempted to reach HuggingFace for `sentence-transformers/all-MiniLM-L6-v2` and fell back after network failure.

Claude should include this in Sprint-SMOKE-01 or an equivalent smoke matrix:

- First-run with no network.
- Existing local model/cache.
- Knowledge-only mode.
- Fallback to full-document context.

## Recommended Next Action

Prioritize Sprint-SMOKE-01, but include the empirical-test collection issue and evidence-chain enforcement as pre-smoke cleanup or explicit smoke risks.

Do not begin large UX work until the dirty worktree and empirical-test ambiguity are resolved.
