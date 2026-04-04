# LESSONS LEARNED

## Format
Each entry: `[YYYY-MM-DD] [CATEGORY] Lesson text`
Categories: ARCH | CODE | PROCESS | TOOLING | RESEARCH

---

## Entries

[2026-04-04] [PROCESS] Clarify remediation target version BEFORE architect runs — misidentifying v1.2 vs v2.0 caused one full design pass to be discarded and redone.
[2026-04-04] [ARCH] AK-CogOS v2.0 adds significant structural requirements not in v1.x: docs/ planning directory (8 artifacts), releases/ audit trail, anti-sycophancy protocol, conversation-derived planning docs.
[2026-04-04] [PROCESS] P0 blocking artifacts (tasks/ba-logic.md, tasks/ux-specs.md, framework-improvements.md) must be created first in any project onboarding — every skill references them on AUTO-RUN.
[2026-04-04] [PROCESS] install-claude-commands.sh requires --dry-run audit and explicit AK approval before live execution — never run blind; it may overwrite project-specific commands.

[2026-03-29] [PROCESS] Start sessions with /session-open to get standup context and avoid duplicate work.
[2026-03-29] [ARCH] Build order matters: schemas before agents, state machine before orchestrator, hooks before tool registry.
[2026-03-29] [ARCH] FRM Risk Register (Phase 3) is the highest priority workflow — it exercises the full stack and proves end-to-end viability.
[2026-03-29] [ARCH] Research tools split into general (Tavily) vs authoritative-only (regulatory, sanctions) — never mix trust levels in final deliverables.
[2026-03-29] [ARCH] Artifact writes must be atomic: write to .tmp first, then os.replace() to prevent partial writes.
[2026-04-02] [CODE] Prefer deriving import-time state from canonical source data instead of persisting duplicate mutable state that can drift.
[2026-04-02] [CODE] Topbar/session chrome should reset on import, route change, and session restart so stale UI context is not carried forward.
[2026-04-02] [TOOLING] Offline or network-restricted environments limit build verification; handoff notes should record when validation was intentionally deferred.
