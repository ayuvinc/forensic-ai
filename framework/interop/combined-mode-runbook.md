# Combined Mode Runbook
# AK Cognitive OS — COMBINED execution
# Date: 2026-03-18

---

## When to use COMBINED mode

Default for: standard features, bug fixes, refactors.
Required when: task touches auth, DB, AI, or new domain types.
Optional for: hotfixes (SOLO_CLAUDE is faster, use COMBINED if risk is high).

AK declares mode in `channel.md` header at session start:
```
MODE: COMBINED
SESSION: [N]
SPRINT: [identifier]
```

---

## Phase Ownership Table

Strictly disjoint. No phase has two owners. No duplication.

```
PHASE                   OWNER     TOOL/COMMAND          OUTPUT
─────────────────────────────────────────────────────────────────────
1. Session open         Claude    /session-open          standup to AK
2. BA (if new feature)  Claude    /ba                    tasks/ba-logic.md
3. UX (if UI change)    Claude    /ux                    tasks/ux-specs.md
4. Architecture         Claude    /architect             tasks/todo.md
5. Security gate        Claude    /security-sweep        signed-off or BLOCKED
6. QA criteria          Claude    /qa (pre-build)        acceptance criteria
7. Handoff validate     Claude    /handoff-validator     PASS or BLOCKED
8. Audit log            Claude    /audit-log             [AUDIT_LOG_PATH] entry
── BUILD LANE ──────────────────────────────────────────────────────
9. Implementation       Claude    /junior-dev            code + tests
10. Regression guard    Claude    /regression-guard      GREEN or BLOCKED
11. Sprint package      Claude    /sprint-packager       sprint-summary.md
12. Review packet       Claude    /review-packet         channel.md
13. Intake check        Claude    /codex-intake-check    CODEX_READY or BLOCKED
── CODEX LANE ──────────────────────────────────────────────────────
14. Review              Codex     Reviewer mode          sprint-review.md
15. Creator fix (opt)   Codex     Creator mode           sprint-delta.md
── RE-ENTRY (if fixes) ─────────────────────────────────────────────
16. Re-regression       Claude    /regression-guard      GREEN or BLOCKED
17. Re-package          Claude    /sprint-packager       updated sprint summary
18. Re-review           Codex     Reviewer mode (delta)  updated verdict
── VALIDATION ──────────────────────────────────────────────────────
19. QA validation       Claude    /qa-run                PASS/FAIL per criterion
20. Code review         Claude    /architect             review notes
21. UX review           Claude    /ux                    UI check vs wireframe
22. Final sign-off      Codex     APPROVED verdict       in sprint-review.md
── CLOSE ────────────────────────────────────────────────────────────
23. Lessons extract     Claude    /lessons-extractor     proposed lessons
24. AK approves lessons AK        —                      AK_DECISION
25. Session close       Claude    /session-close         next-action.md + push
26. Framework delta     Claude    /framework-delta-log   framework-improvements.md
27. Final audit         Claude    /audit-log             SESSION_CLOSED entry
─────────────────────────────────────────────────────────────────────
All audit entries: origin=combined
```

---

## Parallel Execution Lanes

When tasks are independent (no shared files, types, or routes):

```
Step 1: Architect assigns lane per task
        Lane A: [task_id_1, task_id_2]
        Lane B: [task_id_3]

Step 2: Both lanes run Junior Dev simultaneously
        Lane A builds → /regression-guard
        Lane B builds → /regression-guard

Step 3: MERGE COORDINATOR (/sprint-packager)
        Waits for ALL lanes to reach GREEN
        If any lane BLOCKED: package only green lanes, mark blocked lane separately
        Produces single sprint-summary.md covering all green tasks

Step 4: Single Codex review of combined packet
        All tasks in one review pass
        Findings reference task_id — disjoint ownership preserved

Step 5: Creator fixes (if any) run per finding
        Each fix goes back through /regression-guard before re-packaging
```

### Lane independence rules
- Tasks sharing a type definition → SAME lane (not parallelisable)
- Tasks sharing an API route → SAME lane
- Tasks sharing a component → SAME lane
- Tasks with no shared files → DIFFERENT lanes (parallelise)

---

## Handoff Protocol (Claude → Codex)

### What Claude produces (required before Codex opens)
All 7 must exist or `/codex-intake-check` BLOCKS:
```
1. sprint-summary.md               (sprint reviews path)
2. changed-files manifest           (in sprint summary)
3. criteria map 1:1 with tasks      (in sprint summary)
4. regression evidence              (GREEN — created by /regression-guard)
5. ux-specs.md section cited        (if any component file changed)
6. architecture constraints         (if new type or API route)
7. security sign-off                (from /security-sweep or Architect note)
```

### What Codex produces (required before QA opens)
```
1. sprint-review.md                (sprint reviews path)
2. verdict: APPROVED|CONDITIONS|REJECTED
3. findings with S0/S1/S2 per finding
4. ak_decision_required: true|false
5. If Creator mode: sprint-delta.md
```

### What AK does at handoff points
Only 4 touch points in COMBINED mode:
```
1. Declare mode + session objective    → start
2. Open Codex + hand channel.md       → after intake check passes
3. AK_DECISION items (if any)         → after Codex review
4. Approve lessons                    → before session close
```

---

## Conflict Resolution (COMBINED mode)

When Claude and Codex findings contradict:

| Scenario | Resolution |
|---|---|
| Tests PASS (Claude) + structural flaw (Codex) | Codex wins. Tests passing ≠ correct design. |
| Security finding — different severity | Higher severity wins. |
| Codex REJECTED + Claude review PASS | Codex wins. Codex has fresh-session independence. |
| Both BLOCKED, different reasons | Both listed in failures[]. Architect decides order of fix. |
| Codex APPROVED + AK disagrees | AK wins. AK_DECISION logged. |
| S0 from either stack | Merge BLOCKED. No override. Architect + AK required. |
| S2 conflict (advisory only) | Both findings logged. Builder chooses resolution with rationale. |

All conflicts log event_type: AK_DECISION or BOUNDARY_FLAG_OPENED.

---

## COMBINED Mode — Definition of Done

Session cannot close unless ALL of the following:
- [ ] All tasks QA_APPROVED by /qa-run
- [ ] Codex APPROVED verdict on current sprint
- [ ] All S0 findings resolved (Architect signed off)
- [ ] All S1 findings resolved or AK-accepted (logged)
- [ ] All S2 findings logged with rationale or fixed
- [ ] /regression-guard GREEN on final code state
- [ ] tasks/ba-logic.md and tasks/ux-specs.md clear
- [ ] /session-close PASS
- [ ] [AUDIT_LOG_PATH] has SESSION_CLOSED entry
