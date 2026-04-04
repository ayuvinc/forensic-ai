# LESSONS LEARNED

## Format
Each entry: `[YYYY-MM-DD] [CATEGORY] Lesson text`
Categories: ARCH | CODE | PROCESS | TOOLING | RESEARCH

---

## Entries

[2026-04-04] [CODE] Policy/SOP prompt produces strong 8/10 first draft (near enterprise-grade per external review) but
misses 8 predictable gaps: (1) anonymous complaint handling protocol, (2) retaliation investigation mechanism +
disciplinary matrix, (3) evidence handling / forensics / chain of custody, (4) SLA for closure communication to
whistleblower, (5) malicious vs good-faith complaint definition (must be precise or courts view as suppressive),
(6) DPDP Act 2023 integration for India jurisdiction, (7) vendor/third-party enforcement mechanism, (8) metrics /
KPI reporting framework for Audit Committee. Fix: add these as mandatory checklist in policy_sop system prompt.
Validated by external ChatGPT review on Whistleblower Policy generated Session 009.

[2026-04-04] [PROCESS] Mode B workflows produce strong working drafts, not final output. Position as "80% done in
2 minutes — consultant fills gaps as SME." Option 3 (Persona Review → Regulator) is the quality gate that takes
draft from 8/10 to 9/10 before client delivery. This split must be explicit in UI labelling and onboarding.

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
