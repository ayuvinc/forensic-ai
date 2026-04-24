---
Status: active
Last updated: 2026-04-24 — Session 050
Owner: Architect
---

# GoodWork Forensic AI — Application Plan

## What This Is

An AI-augmented forensic consulting workbench. Maher runs structured casework (FRM, Investigation, Transaction Testing, Due Diligence, Sanctions, Policy/SOP, Proposal) through guided intake, AI analysis pipelines, and human review checkpoints. Every output is locally stored, versioned, and auditable. The product is not a report generator — it is a workbench where Maher's professional judgment is embedded at every stage.

---

## Seven Layers — Current State

### Layer 1 — Knowledge & Intelligence
*What the AI knows about the domain.*

| Item | Status |
|---|---|
| FRM framework (8 modules, COSO/ACFE/ISO 37001) | BUILT — `knowledge/frm/frm_framework.md` |
| Investigation framework (7 types, evidence standards) | BUILT — `knowledge/investigation/` |
| Policy/SOP, DD, TT, Sanctions frameworks | BUILT — `knowledge/` subdirectories |
| UAE AML regulatory knowledge (Federal Decree-Law No. 20 of 2018, goAML, DFSA AML Module) | MISSING |
| India PMLA / PML Rules 2005 / FIU-IND obligations | MISSING |
| COSO framework — control categories, common gaps by industry | MISSING |
| ACFE fraud typologies — red flags, evidence patterns per scheme | MISSING |
| Industry-specific control frameworks (banking, real estate, tech, etc.) | MISSING |

**Gap severity: HIGH.** Without embedded regulatory knowledge, the AI fetches from web lookups (unreliable, citable-but-wrong risk). The Project_FRM_test run cited Federal Law No. 8 of 2004 (Financial Free Zones) as the UAE AML law — a knowledge gap, not a citation format problem.

---

### Layer 2 — Context Intake
*What the AI knows about THIS specific client and engagement.*

| Item | Status |
|---|---|
| Case metadata (client, industry dropdown, jurisdiction) | BUILT |
| Workflow-specific parameters (FRM modules, engagement context, etc.) | BUILT |
| AI-assisted intake questions — AIC pass (BA-R-10) | BUILT |
| Document upload + type classification | PARTIAL — TT has full upload; others have shells |
| **Process understanding stage** — how does THIS client's business work? | MISSING from ALL workflows |
| Stakeholder discussion capture (BA-R-09) | DESIGNED but not built |
| Policy/SOP upload → structured process context extraction | MISSING |

**Gap severity: CRITICAL.** Without process context, every workflow produces generic industry-level analysis. Investigation cannot find procurement fraud evidence without knowing the client's procurement process. FRM cannot rate risks accurately without knowing the client's existing controls. This is the single biggest quality gap.

**Process understanding stage inputs (per workflow):**
- FRM: existing policies/SOPs, control environment, prior audit findings, system landscape, org structure
- Investigation: business process for the specific fraud type (procurement flow, payroll process, expense cycle), access controls, approval authorities, data/system availability
- Transaction Testing: transaction lifecycle, normal patterns, system architecture, approval thresholds, available data extract
- Due Diligence: target's business model, revenue sources, customer/vendor relationships, ownership structure

---

### Layer 3 — Pipeline & Analysis
*The AI analysis engine.*

| Item | Status |
|---|---|
| Multi-agent chain: junior → PM → partner | BUILT |
| FRM 8-module loop with sequential indexing | BUILT (indexing bug fixed Session 050) |
| Schema validation + schema_retry on empty findings | BUILT (double-retry graceful skip fixed Session 050) |
| Artifact versioning (per-agent, per-version, atomic write) | BUILT |
| Hook system (validate, persist, audit, render, citations) | BUILT |
| Error log (logs/error_log.jsonl) | BUILT |
| **Partner prompt violates CLAUDE.md** — blocks delivery instead of flagging | BROKEN — must fix before any output is used in production |
| Pipeline state index (resume on failure, milestone tracking) | MISSING — Sprint-INDEX-01 |
| Regulatory understanding vs. live citation lookup | MISSING — Sprint-KB-02 |

**Broken item note:** BA-IA-08 (confirmed Session 022) and CLAUDE.md both specify: "Partner NEVER blocks sign-off — always approves with explicit disclaimers." The current Partner prompt rejects drafts and sets `revision_requested=True` over citation errors. This causes the pipeline to exit without a final report. The Project_FRM_test case was entirely blocked by this. Fix is 2 prompts, 1 test.

---

### Layer 4 — Human Review & Collaboration
*Where Maher applies professional judgment during analysis.*

| Item | Status |
|---|---|
| Human checkpoint panel at pipeline milestones | MISSING — Sprint-CHECKPOINT-01 |
| Inline artifact editing (corrections fed forward into next stage) | MISSING |
| Interim .docx + .md downloads at milestones (not just final output) | MISSING |
| Context gap flagging on findings without process context | MISSING |
| Multi-reviewer comments (second person reviews checkpoint) | LONG-TERM — Model 3+ |

**Gap severity: HIGH.** This is the core product differentiator. Without it, the product is an output generator. With it, it is a professional workbench. Maher catching the wrong UAE law at the identification stage checkpoint takes 30 seconds. The current pipeline takes 3 agent iterations and still doesn't fully fix it.

---

### Layer 5 — Output & Closure
*What Maher gets and how cases close.*

| Item | Status |
|---|---|
| Final .docx + .md download (Done Zone) | BUILT — Sprint-DOCX-01 |
| Case folder with all versioned artifacts | BUILT |
| Audit log per case | BUILT |
| Interim milestone downloads | MISSING — Sprint-CHECKPOINT-01 |
| Mark Complete / Close engagement (BA-REQ-CLOSE-01) | MISSING |
| Sanctions per-hit evidence capture (BA-REQ-SANCTIONS-EVIDENCE-01) | MISSING |
| Evidence chain enforcement in Investigation (R-NEW-13) | PROMPT-ONLY — not enforced at runtime |

---

### Layer 6 — Navigation & UX
*How Maher moves through the app.*

| Item | Status |
|---|---|
| 17 pages, core workflows functional | BUILT |
| Crash reporter + structured error log | BUILT |
| Forensic tip panel during pipeline runs | BUILT — Sprint-UX-WAIT-01 |
| App startup command not obvious — `app.py` vs `streamlit_app/app.py` confusion | BROKEN — Sprint-STARTUP-01 |
| Startup health check (missing .env, missing API key) | MISSING — Sprint-STARTUP-01 |
| Pre-create case folder on Run click | MISSING — Sprint-FOLDER-01 |
| Progress bar turns red mid-pipeline | BROKEN — Sprint-UX-PROGRESS-01 |
| Sidebar shifts on page navigation | BROKEN — Sprint-UX-NAV-01 (needs wireframe) |
| Session log: open workflow → see active cases → resume | MISSING — Sprint-SESSION-ENTRY-01 |
| Pipeline streaming progress | MISSING — Sprint-UX-STREAM-01 |
| @st.fragment, st.toast, page dimming | MISSING — Sprint-UX-WIRE-01 |

---

### Layer 7 — Testing & Quality Gates
*Confidence that it works.*

| Item | Status |
|---|---|
| 131 unit tests | BUILT — passing |
| Smoke test spec (Sprint-IA-03) | BUILT — not run recently |
| Multi-workflow formal smoke suite | MISSING — Sprint-SMOKE-01 |
| CLI headless error runner | MISSING — Sprint-CLI-ERR-01 (needs design) |

---

## Workflow Gap Summary

| Workflow | Process Context | Partner Fix | Checkpoint | Evidence Chain | Other |
|---|---|---|---|---|---|
| FRM | MISSING — critical | BROKEN | MISSING | N/A | Knowledge base gaps |
| Investigation | MISSING — critical | BROKEN | MISSING | R-NEW-13 prompt-only | Stage design (long-term) |
| Transaction Testing | MISSING | BROKEN | MISSING | N/A | Doc upload partial |
| Due Diligence | MISSING | BROKEN | MISSING | N/A | |
| Sanctions | MISSING | BROKEN | MISSING | BA-REQ-SANCTIONS-EVIDENCE-01 | knowledge_only gate works |
| Policy/SOP | N/A | BROKEN | MISSING | N/A | Co-build not built (Sprint-IA-04) |
| Training | N/A | BROKEN | MISSING | N/A | |
| Proposal | N/A | BROKEN | MISSING | N/A | |

---

## Sprint Sequence — Ordered by Dependency

### Tier 0 — Immediate (close current branch)
| Sprint | What | Why Now |
|---|---|---|
| DOCX-03 smoke | AK verifies download buttons on FRM Done Zone | Unblocks Sprint-DOCX-01 merge |
| **Sprint-DOCX-01 merge** | Merge feature branch to main | All Sprint 049 fixes land on main |

### Tier 1 — Fix What's Broken (no new features until these are done)
| Sprint | What | Tasks |
|---|---|---|
| **Sprint-PARTNER-FIX-01** | Fix Partner prompt to never block — flags + conditions only, per CLAUDE.md BA-IA-08 | ~2 tasks |
| **Sprint-FOLDER-01** | Pre-create case folder + minimal state.json on Run click | 4 tasks — already designed |
| **Sprint-UX-PROGRESS-01** | Replace broken progress bar with indeterminate spinner (Option A) | 2 tasks — already designed |

### Tier 2 — Foundation (everything quality-related builds on these)
| Sprint | What | Tasks |
|---|---|---|
| **Sprint-INDEX-01** | pipeline_index.json — state tracking, resume on failure, milestone artifacts | 5 tasks — already designed |
| **Sprint-PROCESS-01** | Process understanding stage for FRM, Investigation, TT, DD — structured intake, document extraction, context injection | ~12 tasks — needs BA logic |
| **Sprint-KB-02** | Knowledge base regulatory expansion — UAE AML, India PMLA, COSO, ACFE fraud typologies | Content work + prompt wiring |

### Tier 3 — Core Product Quality (builds on Tier 2)
| Sprint | What | Tasks |
|---|---|---|
| **Sprint-CHECKPOINT-01** | Human review panel + interim downloads at every milestone | 5 tasks — already designed |
| **Sprint-CLOSE-01** | Mark Complete / Close button — BA-REQ-CLOSE-01 | Needs BA design |
| **Sprint-EVIDENCE-01** | Sanctions per-hit evidence capture — BA-REQ-SANCTIONS-EVIDENCE-01 | Needs BA design |

### Tier 4 — UX Polish (after core is stable)
| Sprint | What | Gate |
|---|---|---|
| Sprint-UPLOAD-01 | Document upload with type classification for all workflows | After INDEX-01 |
| Sprint-UX-NAV-01 | Pinned sidebar | Needs wireframe first |
| Sprint-SESSION-ENTRY-01 | Session log with active case entry on workflow open | Needs wireframe + INDEX-01 |
| Sprint-UX-WIRE-01 | @st.fragment, st.toast, page dimming | Unblocked |
| Sprint-UX-STREAM-01 | Pipeline streaming | Unblocked |

### Tier 5 — Quality Gates (run in parallel with Tier 3-4)
| Sprint | What | Gate |
|---|---|---|
| Sprint-SMOKE-01 | Formal multi-workflow smoke suite | Unblocked — spec already written |
| Sprint-CLI-ERR-01 | Headless error runner | Needs architecture design |

### Tier 6 — Advanced Features (after Tiers 1-3 are solid)
| Sprint | What | Gate |
|---|---|---|
| Sprint-IA-04 | Policy/SOP co-build mode | After INDEX-01 + CHECKPOINT-01 |
| Sprint-STAGE-01 | Full stage-based workflow redesign | After INDEX-01 + CHECKPOINT-01 + PROCESS-01 |
| Phase 7 | White-label packaging | After smoke tests pass |

---

## Design Debt — Needs BA/Design Work Before Sprint Can Start

| Item | What's needed |
|---|---|
| Sprint-PROCESS-01 | BA logic: process understanding questionnaires per workflow (FRM, Investigation, TT, DD) — what questions, what structure, how extracted from documents |
| Sprint-CLOSE-01 | BA design: engagement closure state machine — what terminal states mean, what gets locked on close |
| Sprint-EVIDENCE-01 | BA design: per-hit evidence capture schema for Sanctions — what fields required, how stored |
| Sprint-CLI-ERR-01 | Architecture design: headless pipeline runner — how to invoke without browser, how to log errors |
| Sprint-UX-NAV-01 | UX wireframe: NAV-00 pattern — pinned sidebar layout |
| Sprint-SESSION-ENTRY-01 | UX wireframe: session log entry screen layout |
| Sprint-STAGE-01 | Full architecture design: stage boundaries per workflow, state transitions, backward compatibility |

---

## Legacy Items — Review for Archive

The following sprints in tasks/todo.md were designed for an earlier architecture and are superseded or blocked indefinitely. AK to confirm archive:

| Item | Reason |
|---|---|
| Sprint-10L Phase B (Behavioral Matrix) | BLOCKED: MISSING_BA_SIGNOFF — no path to unblock |
| Sprint-10C (Historical Knowledge Library) | Superseded by `knowledge/` directory approach |
| Sprint-10D (FRM Guided Exercise Redesign) | Long-term; no active path |
| Sprint-10G (Workflow Chaining) | Superseded by Sprint-INDEX-01 + Sprint-CHECKPOINT-01 |
| Sprint-EMB (Semantic Embeddings) | READY_FOR_REVIEW but requires API credits; defer until production |
| Phase 10–13 | Long-term planning items; no active build path |
| Sprint-AIC, Sprint-RD, Sprint-FE | Partially superseded by Sprint-IA-01/02/03 completions |

---

## Critical Path Summary

```
DOCX-03 smoke → merge Sprint-DOCX-01
                    ↓
         Sprint-PARTNER-FIX-01 (unblocks all pipeline output quality)
         Sprint-FOLDER-01      (small, 1 session)
         Sprint-UX-PROGRESS-01 (small, 1 session)
                    ↓
         Sprint-INDEX-01       (foundation — resume + milestones)
         Sprint-PROCESS-01     (foundation — process context quality)
         Sprint-KB-02          (foundation — knowledge depth)
                    ↓
         Sprint-CHECKPOINT-01  (human review layer — the differentiator)
         Sprint-CLOSE-01       (closure flow)
                    ↓
         UX polish + Quality gates + Advanced features
```

---

## Immediate Next Session

**Persona:** Architect
**Goal:** Merge Sprint-DOCX-01. Write BA logic for Sprint-PROCESS-01 (process understanding stage). Write Sprint-PARTNER-FIX-01 tasks and build it (2 tasks, low risk). Then plan Sprint-INDEX-01 build session.

**Pre-build gate for Sprint-PROCESS-01:** BA logic must specify the exact process understanding questions per workflow before Junior Dev writes a single line of intake code.
