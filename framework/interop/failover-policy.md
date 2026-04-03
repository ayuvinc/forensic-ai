# Failover Policy
# AK Cognitive OS — Mutual Fallback
# Date: 2026-03-18

---

## Principle

If one stack is unavailable or consistently failing, the other continues in degraded mode.
Degraded mode is explicit, declared, and audited — never silent.

---

## Failover Triggers

A stack is considered failed/unavailable when ANY of:

| Trigger | Threshold | Action |
|---|---|---|
| Repeated BLOCKED | 3+ times on same artifact, same agent | Escalate + switch mode |
| Schema mismatch | Output doesn't match interop-contract-v1.md | BLOCKED + notify AK |
| Timeout | No response in expected session window | AK declares degraded mode |
| Contradictory S0 | Both stacks give opposite S0 findings | Both blocked — AK + Architect resolve |
| Stack unavailable | Claude Code down or Codex session unavailable | Automatic degraded mode |

---

## Codex Unavailable → Degraded SOLO_CLAUDE

When Codex cannot be reached or consistently fails:

```
DEGRADED MODE: SOLO_CLAUDE
Declare in channel.md: MODE: DEGRADED_SOLO_CLAUDE
Audit: FRAMEWORK_DELTA_LOGGED with reason=codex_unavailable
```

### What Claude does in SOLO_CLAUDE degraded mode
```
Phases normally owned by Codex → replaced as follows:

  Codex Review        → Architect manual code review
                         (read all changed files, check against criteria)
  Codex S0/S1/S2      → Architect classifies findings using same severity policy
  Codex APPROVED      → Architect signs off with note: [DEGRADED: SOLO_CLAUDE]
  Codex Creator fix   → Junior Dev handles all fixes
  Final sign-off      → /qa-run QA_APPROVED + Architect code review
```

### Quality gates maintained in degraded mode
- /regression-guard still runs (non-negotiable)
- /qa-run still runs (non-negotiable)
- /handoff-validator still runs
- /audit-log still appends with `origin: claude-core`
- All findings still documented in sprint-review.md (written by Architect)

### When to return to COMBINED
- Next session, if Codex is available
- AK declares: `MODE: COMBINED` in channel.md
- No backfill required — degraded session is complete as-is

---

## Claude Unavailable → Degraded SOLO_CODEX

When Claude Code is not available (session crash, environment issue):

```
DEGRADED MODE: SOLO_CODEX
Declare in channel.md: MODE: DEGRADED_SOLO_CODEX
```

### What Codex does in SOLO_CODEX degraded mode
```
Phases normally owned by Claude → replaced as follows:

  Implementation      → Codex Creator mode (if code not yet written)
  Regression check    → Codex reads test results from last known run
                         (cannot run test suite directly — note as MANUAL_REQUIRED)
  Sprint package      → Codex writes sprint-summary.md manually
  QA run              → Codex reviews criteria vs code (cannot automate test run)
                         → marks tests as MANUAL_REQUIRED for AK to verify
  Session close       → Codex writes next-action.md scaffold
                         git operations: AK must run manually
```

### What Codex cannot do in degraded mode
```
- Run test/build/lint commands (no shell access)
- Write to filesystem directly (AK must copy Codex output)
- Update SESSION STATE in todo.md automatically
```

### Degraded SOLO_CODEX — AK touch points increase
In this mode AK becomes the bridge for all filesystem operations.
Aim to restore Claude Code access before continuing.

---

## Repeated BLOCKED Escalation Protocol

If the same agent BLOCKs 3+ consecutive times on the same artifact:

```
Step 1: Log to [AUDIT_LOG_PATH]:
        event_type: FRAMEWORK_DELTA_LOGGED
        summary: "Agent {name} BLOCKED 3x on {artifact} — escalating"

Step 2: Architect reads the last 3 BLOCKED outputs
        Identify: is this a data problem, config problem, or framework bug?

Step 3: Classify:
        DATA PROBLEM → fix the artifact, rerun agent
        CONFIG PROBLEM → fix path overrides in CLAUDE.md, rerun
        FRAMEWORK BUG → log to framework-improvements.md, bypass agent for this session

Step 4: If bypassing agent:
        Document bypass in channel.md: [AGENT_BYPASS: {agent} reason={reason}]
        Audit: event_type: AK_DECISION, summary="bypassed {agent}: {reason}"
        Proceed manually for that phase
```

---

## Schema Mismatch Protocol

If either stack produces output that doesn't match interop-contract-v1.md:

```
Step 1: Consuming stack emits:
        status: BLOCKED
        failures: ["SCHEMA_VIOLATION: {field} — expected {type}, got {actual}"]
        next_action: "Producing stack must fix output format"

Step 2: AK routes back to producing stack with BLOCKED output
        Producing stack corrects and re-runs

Step 3: If 2+ schema mismatches from same stack in same session:
        Log to framework-improvements.md
        Review interop-contract-v1.md — contract may need clarification
```

---

## Fallback Priority Order

```
1. COMBINED (both stacks healthy)           ← default, preferred
2. SOLO_CLAUDE degraded (Codex unavailable) ← most capabilities preserved
3. SOLO_CODEX degraded (Claude unavailable) ← reduced automation, AK bridges
4. MANUAL (both unavailable)                ← AK runs checklist manually
                                              todo.md + lessons.md + git ops
```

Manual mode exists as emergency only. Document in channel.md and resume with COMBINED next session.

---

## Audit Labels in Failover

All degraded mode actions must carry:
```
origin: claude-core     (SOLO_CLAUDE degraded)
origin: codex-core      (SOLO_CODEX degraded)
```
Plus note in summary: `[DEGRADED: {mode}]`

Never use `origin: combined` in degraded mode — combined implies both stacks healthy.
