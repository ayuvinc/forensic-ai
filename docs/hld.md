---
Status: active
Source: code-observed + user-confirmed + ai-inferred
Last confirmed with user: 2026-04-07
Owner: Architect
Open questions: 0
---

# High-Level Design — GoodWork Forensic AI

## System Overview

GoodWork Forensic AI is a single-user, local-install Python application that simulates a forensic consulting firm's internal review hierarchy for a solo practitioner. It produces structured, audit-trailed, CXO-grade forensic deliverables — FRM risk registers, investigation reports, due diligence memos, sanctions screenings, policy/SOPs, client proposals, and training materials — by routing work through a three-agent pipeline (Junior Analyst → Project Manager → Partner) backed by the Anthropic Claude API and Tavily research. The consultant (Maher) drives every case; no output leaves the system without his review.

Entry points: `python run.py` (CLI, current), `streamlit run app.py` (Phase 8, planned).

---

## Major Components

| Module | Purpose | Key Dependencies |
|--------|---------|-----------------|
| `run.py` | CLI entry point; 10-item menu dispatcher | All workflows, config, ui/ |
| `config.py` | API keys, model routing, budget mode, paths | .env, instance_config/firm.json (Phase 7) |
| `core/state_machine.py` | CaseStatus enum + VALID_TRANSITIONS enforcement | schemas/case.py |
| `core/agent_base.py` | Agentic loop: tool dispatch, guardrails, MAX_TURNS, TIMEOUT | core/tool_registry.py, core/hook_engine.py |
| `core/orchestrator.py` | Pipeline sequencer: Junior→PM→Partner; revision loops; resume | core/agent_base.py, core/state_machine.py |
| `core/hook_engine.py` | Chain-of-responsibility pre/post hook runner | hooks/pre_hooks.py, hooks/post_hooks.py |
| `core/tool_registry.py` | Central tool dispatch; enforces ALLOWED_TOOLS per manifest | tools/ |
| `core/plugin_loader.py` | Loads agents/personas from manifest.json files | schemas/plugins.py |
| `schemas/` | All Pydantic data models (case, artifacts, research, presentation, dd, tx_testing, engagement_scope) | pydantic |
| `agents/junior_analyst/` | First-pass draft writer; 10-turn limit; Haiku/Sonnet | knowledge/, tools/research/ |
| `agents/project_manager/` | Review for completeness and quality; 6-turn limit; Sonnet | schemas/artifacts.py |
| `agents/partner/` | Regulatory sign-off; evidence chain enforcement; Opus/Sonnet | tools/research/regulatory_lookup.py |
| `personas/` | Client-perspective reviewers (CFO, Lawyer, Regulator, Adjuster) | schemas/artifacts.py |
| `workflows/` | 10 existing + 3 Phase 10 service lines + engagement scoping | core/orchestrator.py, schemas/ |
| `tools/research/` | 4 research classes with trust-level separation | Tavily API, authoritative sources |
| `tools/document_manager.py` | Case document ingestion, indexing, bounded retrieval | cases/{id}/document_index.json |
| `tools/knowledge_library.py` | Historical report/register ingestion; sanitisation gate (Phase 10C) | firm_profile/historical_*/ |
| `tools/file_tools.py` | Atomic artifact writes; .docx/.md generation | python-docx |
| `hooks/pre_hooks.py` | validate_input, normalize_language, sanitize_pii, attach_case_metadata | schemas/ |
| `hooks/post_hooks.py` | validate_schema, persist_artifact, append_audit_event, extract_citations, render_markdown | cases/{id}/ |
| `ui/` | Rich terminal menu, progress spinners, bilingual display, guided intake | rich |
| `knowledge/` | Static domain knowledge: FRM, investigation, policy_sop, DD, sanctions, tx_testing, engagement_taxonomy | (text files — no code deps) |
| `firm_profile/` | Firm credentials, pricing, T&C, historical library | tools/knowledge_library.py |
| `cases/{case_id}/` | All per-case artifacts: state.json, audit_log.jsonl, agent outputs, deliverables | tools/file_tools.py |

---

## Architecture and Data Flow

### Full-Pipeline Workflows (Investigation Report, FRM Risk Register)

```
[Maher] → [run.py / app.py menu]
              ↓
         [Workflow module] (e.g. frm_risk_register.py)
              ↓
         [ui/guided_intake.py] — conversational intake → CaseIntake (Pydantic)
              ↓
         [DocumentManager] — optional document ingestion → document_index.json
              ↓
         [Orchestrator] — sequences pipeline, manages revisions, detects resume
              ↓ (loop: up to MAX_REVISION_ROUNDS)
         [AgentBase: Junior Analyst]
              ↓ pre-hooks: validate → normalize_language → sanitize_pii → attach_metadata
              ↓ agentic loop (up to 10 turns)
              ↓ tool calls: search_web, regulatory_lookup, sanctions_check, read_document
              ↓ post-hooks: validate_schema → persist_artifact → append_audit_event → extract_citations → render_markdown
              → cases/{id}/junior_output.v{N}.json
              ↓
         [AgentBase: Project Manager] — same hook chain
              → cases/{id}/pm_review.v{N}.json
              ↓ (if revision: loop back to Junior)
         [AgentBase: Partner] — evidence chain enforcement + regulatory sign-off
              → cases/{id}/partner_approval.v{N}.json
              ↓
         [file_tools.write_final_report()] — produces final_report.en.md + final_report.en.docx
              ↓ (if Arabic requested)
              → final_report.ar.md
```

### Mode B Workflows (Policy/SOP, Training, Proposal, Due Diligence, Sanctions, Deck)

```
[Maher] → [Workflow module]
              ↓
         [guided_intake] → validated intake schema
              ↓
         [Single Anthropic API call — Sonnet or Haiku]
              ↓
         [file_tools.write_final_report()] → .md + .docx
              ↓
         [append_audit_event] + [_mark_deliverable_written()] → state.json: DELIVERABLE_WRITTEN
```

### FRM Guided Exercise (Phase 13 redesign)

```
[Maher] → intake → module selection → plan summary confirmation
    ↓
    FOR EACH MODULE:
        → show sub-areas list → Maher confirms scope (Y/N/Partial)
        FOR EACH CONFIRMED SUB-AREA:
            → 4 questions: incidents? controls? probability? impact? → RiskContextItem
            → model generates ONE RiskItem (title, scenario, ratings, recommendations)
            → Maher: Approve / Edit / Skip
            → if Edit: structured revision conversation → re-recommend all params → Maher confirms/overrides
    ↓
    → Register assembled from approved items only
    → Full pipeline: PM review → Partner sign-off on assembled register
```

### Research Tool Trust Hierarchy

```
[general_search.py]    → Tavily (any source)        → low-trust flag on results
[regulatory_lookup.py] → cb.gov.ae, dfsa.ae, adgm.com, sca.gov.ae, fsra.ae → authoritative only
[sanctions_check.py]   → ofac.treas.gov, un.org, sanctions.ec.europa.eu    → authoritative only
[company_lookup.py]    → UAE registries, Zawya, official filings             → unverified if not official registry
```

Final deliverables: **only `authoritative_citations` permitted**. General sources included in research but carry disclaimer in deliverable.

---

## Integration Points

| External System | Protocol | Direction | Purpose |
|----------------|----------|-----------|---------|
| Anthropic API (Claude) | HTTPS / anthropic SDK | Outbound | All agent calls (Haiku/Sonnet/Opus per model routing) |
| Tavily API | HTTPS / tavily-python | Outbound | General web research (general_search.py only) |
| cb.gov.ae, dfsa.ae, adgm.com, sca.gov.ae, fsra.ae | HTTPS (scrape/fetch) | Outbound | Authoritative UAE regulatory lookup |
| ofac.treas.gov, un.org/securitycouncil, sanctions.ec.europa.eu | HTTPS (scrape/fetch) | Outbound | Authoritative sanctions list lookup |
| python-docx | Local library | Internal | .docx generation for deliverables and proposals |
| python-pptx | Local library | Internal | .pptx generation (Phase 6+) |

**Not integrated (explicitly out of scope):**
- WorldCheck / WorldCompliance — licensed DB; not accessible; gap disclosed in all DD/Sanctions outputs
- External email or filing systems — no automated transmission
- Cloud storage — all data local

---

## Security / Auth Model

- **Authentication:** None — single-user local install. No network exposure.
- **API keys:** Stored in `.env` (excluded from git via `.gitignore`). Loaded at startup via `python-dotenv`.
- **Data boundaries:**
  - Case data → `cases/{case_id}/` (local only, never transmitted except as model prompt)
  - Firm credentials and historical library → `firm_profile/` (local only)
  - Historical index entries → PII-stripped at ingest (HARD GATE: SanitisationError blocks write if PII detected)
- **PII handling:**
  - `sanitize_pii` pre-hook strips raw account/passport numbers before agent call
  - DDIntake PII fields (name, DOB, passport number) stored in `cases/{id}/intake.json` only — never written to historical index
  - `KnowledgeLibrary.sanitise()` validates stripped output before any index write — partial strip triggers SanitisationError, not silent partial write
- **Audit logging:** `audit_log.jsonl` is append-only per case; every agent run, state transition, revision, override, and final approval recorded
- **Web content safety:** HTML and script tags stripped from all web-sourced research; truncated to 2000 chars before model call (anti prompt-injection)
- **File parsing:** Uploaded documents parsed by python-docx / PyPDF2 only — no shell execution from user input
- **Abuse surface — model output:** Schema validation in post-hook blocks malformed model output before artifact write

---

## Deployment Model

- **Environment:** Developer machine (Mac or Windows terminal)
- **Entry point:** `python run.py` (Phase 1–8) → `streamlit run app.py` (Phase 8+, browser at localhost)
- **Dependencies:** Python 3.11+, pip packages in `requirements.txt`
- **Setup:** One-time guided wizard creates `.env`, populates `firm_profile/`
- **Infrastructure:** None — local only
- **CI/CD:** None required for single-user install
- **Packaging:**
  - Phase 7: `scripts/create_blank_instance.py` — strips GoodWork knowledge, resets firm profile, outputs zip for white-label distribution
  - Phase 8: Streamlit (`streamlit run app.py`) runs in browser at localhost; no cloud deployment needed

---

## Model Routing

| Tier | Junior | PM | Partner | Persona |
|------|--------|----|---------|---------| 
| economy | Haiku | Haiku | Sonnet | Haiku |
| balanced | Haiku | Sonnet | Sonnet | Sonnet |
| premium | Sonnet | Sonnet | Opus | Sonnet |

Workflow overrides: `frm_risk_register` and `expert_witness_report` → Partner = Opus regardless of tier.

Fallback chain: Opus → Sonnet → Haiku. Max 3 retries with backoff [1, 3, 10]s.

---

## Phase 10–13 Architecture Decisions

### FRM Exercise Engine
- **Decision:** Option A — refactor `workflows/frm_risk_register.py` in place (not a new generic exercise engine).
- **Rationale:** Lowest regression risk; guided exercise pattern is FRM-specific; generic engine is premature abstraction.
- **Gate:** FRM-R-01..08 must be built behind a baseline comparison — P7-GATE smoke test must establish a working baseline before redesign merges.

### New Service Lines (DD, Sanctions, Transaction Testing)
- **Decision:** Mode B first (single-pass Sonnet); upgrade path to full pipeline later (C-01b pattern).
- **Rationale:** Faster to ship; real GoodWork delivery doesn't require multi-agent review for DD screening memos.
- **Gate:** ARCH-S-02 (DDIntake schemas) and respective knowledge files gate each workflow.

### Transaction Testing State
- **Decision:** Add `SCOPE_CONFIRMED` between `INTAKE_CREATED` and `DELIVERABLE_WRITTEN`.
- **Rationale:** Testing plan must be locked before document ingestion begins (BA-009). State transition enforces this sequencing structurally.

### Workflow Chaining
- **Decision:** `core/chain_router.py` provides the 11-chain CHAIN_MAP; chaining UI is Phase 9 (CH-01..04).
- **Rationale:** Clean separation — routing logic in core/, UI in run.py/app.py.
- **Gate:** Chaining gated on Phase 8 Streamlit (UI surface required for smooth chain UX).

### Historical Knowledge Library
- **Decision:** `tools/knowledge_library.py` with `SanitisationError` as a HARD GATE.
- **Rationale:** PII leakage from historical reports into new engagement outputs is the highest-consequence failure mode (R-011). Hard gate is non-negotiable.
- **SanitisationError location:** `tools/knowledge_library.py` (module-level exception, not schemas/).
- **Index entry schema:** `SanitisedIndexEntry` in `schemas/artifacts.py` — no PII fields by model definition.

### Engagement Scoping Workflow
- **Decision:** Problem-first entry point ("Scope New Engagement") added as optional item 0 before the 10-item menu. Existing menu unchanged.
- **Rationale:** 30% of GoodWork engagements start ambiguous; existing menu handles the other 70%.
- **Gate:** `knowledge/engagement_taxonomy/framework.md` (KF-NEW) must exist before workflow ships.

---

## Risks and Constraints

| Risk | Impact | Mitigation |
|------|--------|-----------|
| R-001 Tavily free tier (1000/month) | Medium | Cache results locally per case_id; `use_cached` flag |
| R-003 Arabic rendering in terminals | Low | Test early; plain-text fallback |
| R-004 PPT external tool dependency | Low | Output as prompt files only; document in README |
| R-009 No live FRM smoke test | High | P7-GATE required before FRM redesign merges |
| R-010 FRM redesign regression risk | High | Feature-flag or new workflow path until baseline passing |
| R-011 PII in historical library | High | SanitisationError HARD GATE in KnowledgeLibrary.sanitise() |
| R-012 Scope creep (35+ new tasks) | Medium | Critical path enforced; start with ARCH-S-01 + KF-00 only |

---

## Out-of-Scope for This Design

- Multi-user access or role-based permissions
- Cloud storage or remote sync
- WorldCheck / WorldCompliance integration (licensed DB)
- HUMINT execution (scoping output only)
- Automated email/filing submission
- Statistical sampling computation (advisory guidance only)
- Urdu-language adverse media search (sub-contractor dependency)
