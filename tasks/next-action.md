# NEXT ACTION

## SESSION
OPEN

## NEXT_PERSONA
junior-dev

## NEXT_TASK
**Session 051 (continued) — Build Sprint-FOLDER-01**

Sprint-PARTNER-FIX-01 merged to main (QA_APPROVED 2026-04-24). 139 tests pass.

**Build now — Sprint-FOLDER-01 (4 tasks, 8 pages):**
1. FOLDER-01 `pages/02_Investigation.py` — pre-create case folder + write minimal state.json before `run_in_status()`
2. FOLDER-02 `pages/06_FRM.py` — same
3. FOLDER-03 `pages/09_Due_Diligence.py` — same
4. FOLDER-04 `pages/04_Policy_SOP.py`, `05_Training.py`, `07_Proposal.py`, `10_Sanctions.py`, `11_Transaction_Testing.py` — same pattern, batch commit

**Pattern:** In each workflow page, immediately before `run_in_status(...)`:
```python
from tools.file_tools import case_dir
import json, datetime
folder = case_dir(case_id)
folder.mkdir(parents=True, exist_ok=True)
state_file = folder / "state.json"
if not state_file.exists():
    state_file.write_text(json.dumps({
        "case_id": case_id,
        "workflow": workflow_type,
        "status": "running",
        "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }))
```
Must use atomic write (`.tmp` then `os.replace()`) — consistent with `file_tools.py` pattern.
Guard: if `case_id` is empty/None, show `st.error()` and return before creating folder.
Security: `case_id` is slugified by Pydantic intake validator — path traversal already blocked.

**Branch:** `feature/sprint-folder-01-pre-create-case-folder`

**After FOLDER-01:** Sprint-UX-PROGRESS-01 (progress bar fix — Option A: replace st.progress with st.status spinner).

## COMMAND
```
/junior-dev build Sprint-FOLDER-01 (FOLDER-01/02/03/04)
```

## COMPLETION STATUS

```
Phase 1-8 + Sprints A-G:        100% ██████████ DONE
Phase H + Phase I (P9):          100% ██████████ DONE
Sprint-RD/WF/FR/AIC/EMB/FE:     100% ██████████ DONE
Sprint-WORK/CONV/KL/ACT/TPL:    100% ██████████ DONE
Sprint-IA-01/02/03/04:           100% ██████████ DONE
Sprint-KB-01:                    100% ██████████ MERGED — smoke check deferred
Sprint-QUAL-01:                  100% ██████████ DONE
ARCH-SIM-01/02:                  100% ██████████ DONE
Sprint-UX-ERR-01:                100% ██████████ DONE
Sprint-UX-WAIT-01:               100% ██████████ DONE
Sprint-DOCX-01:                  100% ██████████ MERGED 2026-04-24
Sprint-PARTNER-FIX-01:           100% ██████████ MERGED 2026-04-24
Sprint-FOLDER-01:                0%  ░░░░░░░░░░ ACTIVE — Tier 1
Sprint-UX-PROGRESS-01:           0%  ░░░░░░░░░░ QUEUED — Tier 1
Sprint-INDEX-01:                 0%  ░░░░░░░░░░ QUEUED — Tier 2 Foundation
Sprint-PROCESS-01:               0%  ░░░░░░░░░░ QUEUED — Tier 2 Foundation (BA needed)
Sprint-KB-02:                    0%  ░░░░░░░░░░ QUEUED — Tier 2 Foundation (content needed)
Sprint-CHECKPOINT-01:            0%  ░░░░░░░░░░ QUEUED — Tier 3
Sprint-CLOSE-01:                 0%  ░░░░░░░░░░ QUEUED — Tier 3 (BA needed)
Sprint-EVIDENCE-01:              0%  ░░░░░░░░░░ QUEUED — Tier 3 (BA needed)
Sprint-SMOKE-01:                 0%  ░░░░░░░░░░ QUEUED — Tier 5
Sprint-UX-WIRE-01:               0%  ░░░░░░░░░░ QUEUED — Tier 4
Sprint-UX-STREAM-01:             0%  ░░░░░░░░░░ QUEUED — Tier 4
Sprint-CLI-ERR-01:               0%  ░░░░░░░░░░ QUEUED — Tier 5 (design needed)
```

## BLOCKERS_AND_ENV_LIMITATIONS
- R-NEW-13 OPEN: evidence-chain enforcement prompt-only — production cases blocked
- BA-REQ-SANCTIONS-EVIDENCE-01: Sanctions output not evidenced — do not use for real compliance files
- BA-REQ-CLOSE-01: No Mark Complete/Close button yet
- Sprint-KB-01 smoke check: DEFERRED (no API credit)
- **API credits: limited** — all pipeline testing blocked until credits restored; FOLDER-01 has no API dependency (safe to build)
- Recommendations coercion P1: RiskItem field validator looks for 'recommendation' key but model returns 'title' key — raw dicts still render in .md output. Fix in Sprint-KB-02 or standalone hotfix.

## CARRY_FORWARD_CONTEXT
- Full application plan at `docs/app-plan.md` — authoritative sprint order, 7-layer gap analysis
- Partner fix merged: pipeline can now complete without stalling at Partner stage
- FOLDER-01 pattern: all 8 pages need the same pre-create block — batch FOLDER-04 across 5 pages in one commit
- Sprint-INDEX-01 is the foundation for CHECKPOINT-01, SESSION-ENTRY-01, PROCESS-01 persistence
- Project name = case folder (slugified). Engagement path: Engagements page sets it.
- FRM pipeline: schema_retry fires on empty findings; double-retry graceful skip works; module index display fixed
