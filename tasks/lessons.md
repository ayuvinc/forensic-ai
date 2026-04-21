# LESSONS LEARNED

## Format
Each entry: `[YYYY-MM-DD] [CATEGORY] Lesson text`
Categories: ARCH | CODE | PROCESS | TOOLING | RESEARCH

---

## Entries

[2026-04-04] [ARCH] FRM (and structured assessment workflows) must be designed as GUIDED EXERCISES, not
one-shot AI generation. Current design asks model to generate the full risk register in one prompt — this
produces empty or poor output because the model lacks client-specific context. Correct design:
(1) Show framework/plan first — here are the 8 modules, here is what we will cover in each
(2) For each module: present risk sub-areas → ask consultant to confirm which apply to this client
(3) For each risk area: ask about known incidents, existing controls, probability assessment, impact rating
(4) Model provides structure + regulatory baseline; consultant provides client-specific context
(5) Co-created output — not AI-generated, but AI-structured with consultant input at each step
This applies to: FRM Risk Register, Investigation Report, Due Diligence, Transaction Testing.
Any workflow that produces a structured assessment must follow guided-exercise pattern, not one-shot.

[2026-04-04] [ARCH] Zero-information drafts are a core product requirement, not an edge case. If a consultant
provides no client documents and no detailed intake, the engine must still produce a usable starting-point draft
by (a) asking clarifying questions OR (b) populating with industry-baseline risks/findings from its knowledge base.
The FRM risk register for a fintech with no documents should return ~10 baseline AML/KYC risks from RBI/PMLA
framework — not 0 risks. This applies to all workflows: investigation report, policy/SOP, proposal, FRM.
Design principle: "starting point draft even with zero client information" must be explicit in every agent
system prompt and every knowledge file. Consultant then adds/removes/adjusts. Engine is never allowed to
return a blank deliverable when it has domain knowledge to draw on. Add to planning: define baseline
content floor per workflow type.

[2026-04-04] [PROCESS] Session context limit (87%) — check context usage at session-open and session-close;
if approaching limit mid-session, close and open a new session rather than compressing context further.
High-context sessions risk losing carry-forward detail. Mitigation: keep sessions focused on one sprint goal;
do not mix smoke tests + scope expansion + bug fixes in one session.

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

[2026-04-07] [ARCH] Any guardrail that enforces external-data quality (citations, authoritative sources,
live lookups) MUST be mode-aware. Check RESEARCH_MODE before firing. In knowledge_only mode: replace
hard block with disclaimer appended to output. In live mode: hard block stands. This applies to
NoCitationsError, any future sanctions-match-required check, and any regulatory-source enforcement.
Lesson from BUG-10 (Session 013): citation guard was not mode-aware, blocked knowledge_only smoke test.

[2026-04-07] [ARCH] Config flags that control data quality degradation must default to the HIGHER
quality setting when the required credential is present. RESEARCH_MODE should default to "live" if
TAVILY_API_KEY exists, not "knowledge_only". Silent degradation is worse than a startup error.
Lesson from BUG-09 (Session 013): default was knowledge_only regardless of key presence.

[2026-04-07] [ARCH] Workflows with compliance/legal implications (sanctions screening, regulatory
sign-off) must surface degraded-mode warnings as unmissable UI panels — not inline text. A disclaimer
buried in draft output may not be read. Sanctions workflow in knowledge_only mode must render a red
warning panel before output. Consultant must acknowledge before proceeding. Lesson from PPH-02 design.

[2026-04-07] [PROCESS] When fixing a guardrail to support a new mode (e.g. knowledge_only), immediately
assess every other guardrail in the same file for the same gap. Don't fix one instance and ship —
audit the full file. BUG-09/10 smoke test required 3 separate fix-test cycles that could have been 1.

[2026-04-07] [ARCH] The 3-agent review pipeline (Junior → PM → Partner) was designed assuming
documents + live research are always present. In knowledge_only mode, PM correctly rejects generic
output → revision loop exhausts at MAX_REVISION_ROUNDS → crash. This is the system working as
designed, not a bug. Fix: PM and Partner agents need mode-aware acceptance criteria. In
knowledge_only mode: accept best-effort model output, flag gaps as open_questions not revision
requests, never request revision for missing citations. G-13/G-14 account for 38/60 crashes
in 100-iteration Monte Carlo — the biggest production risk, not the research tool stubs.

[2026-04-07] [PROCESS] Game theory + Monte Carlo simulation is a faster and cheaper way to find
production failure modes than running actual smoke tests. 100 theoretical iterations (2 min, zero
API cost) revealed G-13/G-14 as the dominant failure mode — something 16 structured real runs
would have taken hours to discover. Use Monte Carlo before every major feature release to estimate
crash rate and trust trajectory before touching production. Seed with real p-values from code
inspection.

[2026-04-07] [ARCH] Fix priority must be derived from crash frequency, not intuition or recency.
BUG-09/10/11 were urgent because they blocked the smoke test. But Monte Carlo showed G-13/G-14
(PM/Partner review loop exhaustion) cause 63% of all crashes in real usage. The fix order should
be: (1) mode-aware review criteria, (2) C=0 for non-compliance workflows, (3) schema field
defaults, (4) UI warnings. Intuition said fix the obvious bugs first — simulation said fix the
review chain first.

[2026-04-07] [ARCH] Nash equilibrium in a consulting tool: if trust < 0.60, the practitioner
permanently avoids the feature that caused the crash. Trust hit zero at iteration 11 in simulation.
Recovery is near-impossible once a practitioner decides a tool is unreliable — they will route
around it permanently. This means: zero crashes is the only acceptable target for core workflows
(FRM, Investigation). Degraded-with-warning is acceptable. CRASH is not.

[2026-04-21] [PROCESS] The QA gate (QA_APPROVED) was never connected to UI runtime verification.
Sprint ACs were verifiable by code inspection or CLI smoke test. No AC ever required opening the
Streamlit app and confirming a page loads. QA_APPROVED meant "backend pipeline is correct" not
"frontend renders correctly." These are two different claims. Every sprint that ships frontend pages
must include an explicit AC: "run streamlit, open all affected pages, confirm render before
QA_APPROVED." Code correctness does not imply UI runtime correctness.

[2026-04-21] [ARCH] Two pages sharing the same numeric prefix in pages/ is undefined behavior in
Streamlit (pages/01_Engagements.py and pages/01_Scope.py both existed). Streamlit routing uses the
filename prefix to order and register pages. Collisions are resolved by filesystem sort order, which
is not guaranteed. Result: one page may silently shadow the other, or both may behave erratically.
Rule: enforce unique numeric prefixes across all pages/ files before any sprint is QA_APPROVED.
Architect must verify this during task decomposition, not after a crash report.

[2026-04-21] [ARCH] Using Streamlit private APIs (streamlit.runtime.scriptrunner.get_script_run_ctx,
ctx.page_script_hash, ctx.script_path) for page detection is fragile. These are undocumented
attributes that change across Streamlit versions. Swallowing the AttributeError silently (bare
except) hides the failure and causes every page to attempt a redirect. Rule: page detection logic
must use only the documented public API (st.query_params, page filename inspection via __file__,
or a session_state flag). Never read private ctx attributes for routing decisions.

[2026-04-21] [ARCH] Calling bootstrap(st) at module level (top of every Streamlit page, outside any
function or render block) means an import failure in any of the 8 modules loaded by bootstrap crashes
the page before it renders anything. The crash is invisible to the user — they see a blank page or
an unhandled exception with no recovery path. Rule: bootstrap() must be wrapped in try/except at
every call site, and failures must render a visible degraded-mode panel rather than a hard crash.

[2026-04-21] [PROCESS] Pages built and verified in isolation do not constitute a tested application.
st.session_state is shared across all Streamlit pages at runtime. A page that expects session keys
set by a previous page will crash if navigated to directly or if the prior page failed. Integration
must be explicitly tested: run the app, open each page in order from a clean state, verify that
session state flows correctly from page to page. This test was never in the sprint cycle. Add it.

[2026-04-21] [PROCESS] Manual smoke tests without a written protocol produce no permanent artifact and
restart from zero every sprint. The fix is a reusable skill (/smoke-test) that: (1) loads a per-sprint
test spec from tasks/smoke-tests/{sprint_id}.md, (2) drives one atomic step at a time with 1/0 binary
feedback, (3) asks confirm questions on pass and diagnostic questions on fail, (4) writes results to
releases/ as the session progresses. The spec format separates the interaction protocol (the skill) from
the test steps (the spec), so the skill never needs to change when a new sprint is tested. Lesson: any
recurring manual verification process that produces no artifact should be extracted into a skill.

[2026-04-21] [ARCH] Simulation (parametric MC + empirical + future-direction MC) is a full pre-build
quality system, not a one-off exercise. Three phases: (1) parametric MC — assign failure probabilities
to each code path, compute crash rate across 1000 runs, identify dominant failure modes; (2) empirical
— run real code with mocked LLM responses, confirm/refute each parametric claim with actual behaviour;
(3) future-direction MC — simulate workflows that do not exist yet, surface design gates before build
begins. This session produced 30 FUT-N tickets, fixed 8 P1/P2 defects before any production crash, and
wrote 4 design gates blocking 4 future features from being built incorrectly. Run this before every
major feature sprint, not just when things break.
