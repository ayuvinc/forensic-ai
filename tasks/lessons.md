# LESSONS LEARNED

## Format
Each entry: `[YYYY-MM-DD] [CATEGORY] Lesson text`
Categories: ARCH | CODE | PROCESS | TOOLING | RESEARCH

---

## Entries

[2026-03-29] [PROCESS] Start sessions with /session-open to get standup context and avoid duplicate work.
[2026-03-29] [ARCH] Build order matters: schemas before agents, state machine before orchestrator, hooks before tool registry.
[2026-03-29] [ARCH] FRM Risk Register (Phase 3) is the highest priority workflow — it exercises the full stack and proves end-to-end viability.
[2026-03-29] [ARCH] Research tools split into general (Tavily) vs authoritative-only (regulatory, sanctions) — never mix trust levels in final deliverables.
[2026-03-29] [ARCH] Artifact writes must be atomic: write to .tmp first, then os.replace() to prevent partial writes.
