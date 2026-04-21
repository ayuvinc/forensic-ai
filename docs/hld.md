---
Status: active
Source: code-observed + user-confirmed
Last confirmed with user: 2026-04-21
Owner: Architect
Open questions: 0
---

# High-Level Design — GoodWork Forensic AI

## System Overview

GoodWork Forensic AI is a single-user, local-install Python application that simulates a forensic consulting firm's internal review hierarchy for a solo practitioner. It produces structured, audit-trailed, CXO-grade forensic deliverables across multiple service lines by routing work through a three-agent pipeline (Junior Analyst → Project Manager → Partner) backed by the Anthropic Claude API and Tavily research.

The consultant (Maher) organises all work into **Projects**. Each Project maps to one engagement and can contain 1–N independent workflow runs (workstreams). Two arcs exist: the **Proposal arc** (pre-engagement: scope → proposal deck) and the **Engagement arc** (root entity: project → multiple workstreams → combined deliverable). Maher assembles the final client-facing deliverable himself from the workflow outputs.

**Entry points:**
- `streamlit run app.py` — primary UI (browser at localhost, Streamlit 1.56.0)
- `python run.py` — CLI fallback (original terminal menu, still functional)

---

## Major Components

| Module | Purpose | Key Dependencies |
|--------|---------|-----------------|
| `app.py` | Streamlit entry point; st.navigation() 5-section sidebar; bootstrap + session init | streamlit_app/shared/session.py |
| `run.py` | CLI entry point; 10-item menu dispatcher (fallback/developer mode) | All workflows, config, ui/ |
| `config.py` | API keys, model routing, budget mode, paths | .env, instance_config/firm.json |
| `streamlit_app/shared/session.py` | Bootstrap: readiness check, session state init, setup redirect | streamlit_app/shared/readiness.py |
| `streamlit_app/shared/pipeline.py` | Streamlit-side pipeline runner; connects pages to orchestrator | core/orchestrator.py |
| `streamlit_app/shared/intake.py` | Guided intake conversation panel (Streamlit) | schemas/ |
| `streamlit_app/shared/aic.py` | AI-assisted intake completion | core/orchestrator.py |
| `streamlit_app/shared/done_zone.py` | Deliverable display and download panel | tools/file_tools.py |
| `streamlit_app/shared/evidence_chat_panel.py` | Conversational evidence review panel | workflows/evidence_chat.py |
| `streamlit_app/shared/template_selector.py` | Template selection UI | tools/template_manager.py |
| `pages/` (18 pages) | One Streamlit page per feature; all use bootstrap pattern | streamlit_app/shared/session.py |
| `core/state_machine.py` | CaseStatus enum + VALID_TRANSITIONS enforcement | schemas/case.py |
| `core/agent_base.py` | Agentic loop: tool dispatch, guardrails, MAX_TURNS, TIMEOUT | core/tool_registry.py, core/hook_engine.py |
| `core/orchestrator.py` | Pipeline sequencer: Junior→PM→Partner; revision loops; resume | core/agent_base.py, core/state_machine.py |
| `core/hook_engine.py` | Chain-of-responsibility pre/post hook runner | hooks/pre_hooks.py, hooks/post_hooks.py |
| `core/tool_registry.py` | Central tool dispatch; enforces ALLOWED_TOOLS per manifest | tools/ |
| `core/plugin_loader.py` | Loads agents/personas from manifest.json files | schemas/plugins.py |
| `core/setup_wizard.py` | First-time setup: .env creation, firm_profile collection | firm_profile/ |
| `core/activity_logger.py` | Structured activity log writer; feeds 15_Activity_Log.py | logs/activity/ |
| `core/embedding_engine.py` | Semantic embedding for case documents and knowledge retrieval | sentence-transformers |
| `core/project_manager.py` | Project/engagement CRUD: create, load, list, slug generation | schemas/project.py, cases/ |
| `core/template_manager.py` | .docx template resolution: GW_ styles, fallback chain | firm_profile/templates/ |
| `core/report_builder.py` | BaseReportBuilder: .md + .docx generation, GW_ style preference | python-docx, core/template_manager.py |
| `core/knowledge_library.py` | Historical report/register ingestion; SanitisationError HARD GATE | firm_profile/historical_*/ |
| `core/knowledge_retriever.py` | Retrieves relevant knowledge from knowledge/ and case history | core/embedding_engine.py |
| `schemas/project.py` | ProjectState: project_name, slug, client, cases dict (workflow→case_id) | pydantic |
| `schemas/case.py` | CaseStatus enum, CaseIntake, per-case state | pydantic |
| `schemas/artifacts.py` | All artifact models: junior output, PM review, partner approval, SanitisedIndexEntry | pydantic |
| `schemas/research.py` | ResearchResult, CitationsIndex, trust levels | pydantic |
| `schemas/dd.py` | DDIntake, DDReport | pydantic |
| `schemas/transaction_testing.py` | TTIntake, TTReport, TTScope | pydantic |
| `schemas/evidence.py` | EvidenceClassification, EvidenceItem | pydantic |
| `schemas/engagement_scope.py` | EngagementScopeIntake, ScopeOutput | pydantic |
| `schemas/presentation.py` | ProposalDeckSchema | pydantic |
| `agents/junior_analyst/` | First-pass draft writer; 10-turn limit; Haiku/Sonnet | knowledge/, tools/research/ |
| `agents/project_manager/` | Review for completeness and quality; 6-turn limit; Sonnet | schemas/artifacts.py |
| `agents/partner/` | Regulatory sign-off; evidence chain review; always approves with disclaimers where standards not met — never blocks; Opus/Sonnet | tools/research/regulatory_lookup.py |
| `personas/` | Client-perspective reviewers (CFO, Lawyer, Regulator, Adjuster) | schemas/artifacts.py |
| `workflows/` (16 modules) | All service line workflow logic | core/orchestrator.py, schemas/ |
| `tools/research/` | 4 research classes with trust-level separation | Tavily API, authoritative sources |
| `tools/document_manager.py` | Case document ingestion, indexing, bounded retrieval | cases/{id}/document_index.json |
| `tools/file_tools.py` | Atomic artifact writes; .docx/.md generation | python-docx |
| `tools/output_generator.py` | Output formatting and section assembly | schemas/artifacts.py |
| `tools/frm_excel_builder.py` | FRM risk register .xlsx generation | openpyxl |
| `tools/evidence/` | Excel analyser, email parser, evidence classifier | pandas, python-docx |
| `hooks/pre_hooks.py` | validate_input, normalize_language, sanitize_pii, attach_case_metadata | schemas/ |
| `hooks/post_hooks.py` | validate_schema, persist_artifact, append_audit_event, extract_citations, render_markdown | cases/{id}/ |
| `ui/` | Rich terminal menu, progress spinners, bilingual display (CLI mode) | rich |
| `knowledge/` | Static domain knowledge: FRM, investigation, policy_sop, DD, sanctions, tx_testing, engagement_taxonomy | (text files) |
| `firm_profile/` | Firm credentials, pricing, T&C, templates, historical library | tools/knowledge_library.py |
| `cases/{slug}/` | All per-project artifacts: state.json, audit_log.jsonl, A–F folder structure | tools/file_tools.py |
| `logs/` | activity/ (structured activity log), mcp/ (server logs) | core/activity_logger.py |

---

## Architecture and Data Flow

### Two-Arc Product Model

```
ARC 1 — PROPOSAL (pre-engagement, no ProjectState)
  01_Scope.py   → engagement scoping conversation → scope output
  07_Proposal.py → proposal deck generation → .pptx saved to firm_profile/proposals/
  [manual: client signs engagement letter]
         │
         └──► Maher creates Project in Arc 2

ARC 2 — ENGAGEMENT (ProjectState, 1–N workstreams)
  01_Engagements.py → create/select Project → ProjectState written
         │
         ├── Run Workstream A → workflow pipeline → cases/{slug}/{type}/
         ├── Run Workstream B → workflow pipeline → cases/{slug}/{type}/
         └── Run Workstream N → workflow pipeline → cases/{slug}/{type}/
         │
  16_Workspace.py → shows all workstream outputs under active project
  Maher assembles final combined deliverable manually
```

### Full-Pipeline Workstreams (Investigation Report, FRM Risk Register, Expert Witness)

```
[Maher] → [Streamlit page or run.py menu]
              ↓
         [Workflow module] (e.g. frm_risk_register.py)
              ↓
         [streamlit_app/shared/intake.py] — guided intake → CaseIntake (Pydantic)
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
              → cases/{slug}/{type}/junior_output.v{N}.json
              ↓
         [AgentBase: Project Manager] — same hook chain
              → cases/{slug}/{type}/pm_review.v{N}.json
              ↓ (if revision: loop back to Junior)
         [AgentBase: Partner] — evidence chain enforcement + regulatory sign-off
              → cases/{slug}/{type}/partner_approval.v{N}.json
              ↓
         [report_builder.write_final_report()] → F_Final/final_report.en.md + .en.docx
              ↓ (if Arabic requested)
              → F_Final/final_report.ar.md
```

### Mode B Workstreams (Due Diligence, Sanctions, Transaction Testing, Policy/SOP, Training, Proposal)

```
[Maher] → [Workflow module]
              ↓
         [guided intake] → validated intake schema
              ↓
         [Single Anthropic API call — Sonnet or Haiku]
              ↓
         [report_builder.write_final_report()] → .md + .docx
              ↓
         [append_audit_event] + [_mark_deliverable_written()] → state.json: DELIVERABLE_WRITTEN
```

### AUP Workstream (Agreed-Upon Procedures — Investigation type 8)

Same as Full-Pipeline but with modified agent behavior:
- Intake captures numbered procedures list — scope locks at intake
- Junior output: one section per procedure (procedure → work performed → factual finding)
- No conclusions section, no recommendation section
- Partner enforces hard no-opinion rule before approval

### FRM Guided Exercise (Phase 13 redesign — pending)

```
[Maher] → intake → module selection → plan summary confirmation
    FOR EACH MODULE:
        → show sub-areas → Maher confirms scope
        FOR EACH SUB-AREA:
            → 4 questions → RiskContextItem
            → model generates ONE RiskItem → Maher: Approve / Edit / Skip
    → Register assembled from approved items only
    → Full pipeline: PM review → Partner sign-off
```

### Research Tool Trust Hierarchy

```
[general_search.py]    → Tavily (any source)                              → low-trust flag
[regulatory_lookup.py] → cb.gov.ae, dfsa.ae, adgm.com, sca.gov.ae, fsra.ae → authoritative only
[sanctions_check.py]   → ofac.treas.gov, un.org, sanctions.ec.europa.eu   → authoritative only
[company_lookup.py]    → UAE registries, Zawya, official filings           → unverified if not registry
```

Final deliverables prefer `authoritative_citations`. Where authoritative sources are unavailable, the Partner appends a disclaimer to the affected section — it does not block sign-off. General sources always carry an unverified disclaimer.

---

## Service Lines

| Service Line | Mode | Pipeline |
|---|---|---|
| Investigation Report (types 1–7) | Full pipeline | Junior → PM → Partner |
| Agreed-Upon Procedures / AUP (type 8) | Full pipeline, no-conclusions mode | Junior → PM → Partner |
| Other / Custom Investigation (type 9) | Full pipeline, structure-confirmed mode | Junior → PM → Partner |
| FRM Risk Register | Full pipeline | Junior → PM → Partner |
| Due Diligence | Mode B | Single-pass Sonnet |
| Sanctions Screening | Mode B | Single-pass Sonnet |
| Transaction Testing | Mode B | Single-pass Sonnet |
| Policy / SOP | Mode B | Single-pass Sonnet |
| Training Material | Mode B | Single-pass Sonnet |
| Client Proposal | Mode B | Single-pass Sonnet |
| Proposal Deck (PPT) | Mode B | Single-pass Sonnet |
| Engagement Scoping | Mode B | Single-pass Sonnet |
| Evidence Chat | Conversational | Single-pass with document context |
| Individual Due Diligence - Background checks | Standalone | Single-pass Sonnet/Opus |

**Planned (not yet built):** Expert Witness Report (model routing exists, workflow page pending), AML Program Review, Regulatory Response Report.

---

## Integration Points

| External System | Protocol | Direction | Purpose |
|----------------|----------|-----------|---------|
| Anthropic API (Claude) | HTTPS / anthropic SDK | Outbound | All agent calls (Haiku/Sonnet/Opus per model routing) |
| Tavily API | HTTPS / tavily-python | Outbound | General web research (general_search.py only) |
| cb.gov.ae, dfsa.ae, adgm.com, sca.gov.ae, fsra.ae | HTTPS (scrape/fetch) | Outbound | Authoritative UAE regulatory lookup |
| ofac.treas.gov, un.org/securitycouncil, sanctions.ec.europa.eu | HTTPS (scrape/fetch) | Outbound | Authoritative sanctions list lookup |
| python-docx | Local library | Internal | .docx generation |
| python-pptx | Local library | Internal | .pptx generation |
| openpyxl | Local library | Internal | FRM .xlsx register generation |
| sentence-transformers | Local library | Internal | Semantic embeddings for document retrieval |

**Not integrated (explicitly out of scope):**
- WorldCheck / WorldCompliance — licensed DB; gap disclosed in all DD/Sanctions outputs
- External email or filing systems
- Cloud storage — all data local

---

## Security and Auth Model

- **Authentication:** None — single-user local install. No network exposure. Streamlit binds to localhost only.
- **API keys:** Stored in `.env` (excluded from git). Loaded at startup via `python-dotenv`.
- **Data boundaries:**
  - Case/project data → `cases/{slug}/` (local only, never transmitted except as model prompt)
  - Firm credentials and historical library → `firm_profile/` (local only)
  - Historical index entries → PII-stripped at ingest (HARD GATE: SanitisationError blocks write)
- **PII handling:**
  - `sanitize_pii` pre-hook strips raw account/passport numbers before agent call
  - DDIntake PII fields stored in `cases/{id}/intake.json` only — never written to historical index
  - `KnowledgeLibrary.sanitise()` validates stripped output before any index write
- **Audit logging:** `audit_log.jsonl` is append-only per case; every agent run, state transition, revision, override, and final approval recorded
- **Web content safety:** HTML and script tags stripped from all web-sourced research; truncated to 2000 chars before model call (anti prompt-injection)
- **File parsing:** Uploaded documents parsed by python-docx / PyPDF2 only — no shell execution from user input
- **Abuse surface — model output:** Schema validation in post-hook blocks malformed model output before artifact write

---

## Deployment Model

- **Environment:** Developer machine (Mac or Windows)
- **Primary entry point:** `streamlit run app.py` → browser at localhost (Streamlit 1.56.0)
- **CLI fallback:** `python run.py` — full terminal menu, all workflows accessible
- **Dependencies:** Python 3.11+, pip packages in `requirements.txt`
- **Setup:** First-time guided wizard (`core/setup_wizard.py`) creates `.env`, populates `firm_profile/`
- **Infrastructure:** None — local only
- **CI/CD:** None required for single-user install
- **White-label packaging:** `scripts/create_blank_instance.py` (Phase 7) — strips GoodWork knowledge, resets firm profile, outputs zip for distribution

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

## Project / Engagement Data Model

```python
class ProjectState(BaseModel):
    project_name: str           # human-readable name set at creation
    slug: str                   # filesystem identifier (derived from project_name)
    client_name: str
    service_type: str           # primary workstream type (metadata, not a restriction)
    cases: dict[str, str]       # workflow_type → case_id (1–N entries, min 1)
    status: str
    created_at: str
```

Constraint: `len(cases) >= 1` enforced at project creation. `project_name` defaults to slug for backward compatibility with existing state.json files.

Case artifacts per workstream stored at: `cases/{case_id}/` with A–F folder structure:
```
cases/{case_id}/
  A_Engagement_Management/    intake, state, audit log
  B_Planning/                 research plan, scope notes
  C_Fieldwork/                workpapers, interview notes
  D_Evidence/                 indexed documents, evidence register
  E_Drafts/                   agent outputs (versioned)
  F_Final/                    final_report.en.md, final_report.en.docx, final_report.ar.md
```

---

## State Machine

```python
class CaseStatus(str, Enum):
    INTAKE_CREATED         = "intake_created"
    JUNIOR_DRAFT_COMPLETE  = "junior_draft_complete"
    PM_REVIEW_COMPLETE     = "pm_review_complete"
    PM_REVISION_REQUESTED  = "pm_revision_requested"
    PARTNER_REVIEW_COMPLETE= "partner_review_complete"
    PARTNER_REVISION_REQ   = "partner_revision_requested"
    OWNER_READY            = "owner_ready"
    OWNER_APPROVED         = "owner_approved"
    OWNER_REJECTED         = "owner_rejected"
    DELIVERABLE_WRITTEN    = "deliverable_written"
    PIPELINE_ERROR         = "pipeline_error"

MAX_REVISION_ROUNDS = {"junior": 3, "pm": 2}
```

---

## Architecture Decisions

### Two-Arc Product Model (Session 036)
- **Decision:** Engagement/Project is the root entity. Two arcs: Proposal (pre-engagement, stateless) and Engagement (root, 1–N workstreams).
- **Rationale:** 30% of GoodWork engagements start with a proposal. The other 70% start directly as engagements. Both patterns must be supported without forcing one into the other.
- **LLD:** `docs/lld/product-ia-design.md`

### Navigation Model — st.navigation() (Session 036)
- **Decision:** Replace Streamlit pages/ auto-registration with explicit `st.navigation()` in `app.py`. Five sections: MAIN, PROPOSALS, MONITOR, SETTINGS, WORKFLOWS.
- **Rationale:** pages/ auto-registration causes naming collisions and gives no control over sidebar grouping or display names.

### Multi-Workflow Per Project (Session 036)
- **Decision:** A Project can run any combination of workflow types. `service_type` is metadata, not a restriction. `ProjectState.cases` dict already supports this.
- **Rationale:** Real forensic engagements frequently combine Investigation + FRM + DD on one client matter.

### Hybrid Intake Design (Session 036 — Sprint-IA-02)
- **Decision:** Replace fully conversational intake with hybrid model: structured fields (dropdowns/checkboxes) for scope-defining parameters + optional Remarks cell per field that triggers targeted conversation (max 2 questions) when non-empty.
- **Rationale:** Fully conversational intake requires model inference for scope-defining fields. Inference produces inconsistent scoping. Structured fields map directly to agent behavior; free text is only needed for narrative context.

### FRM Exercise Engine (Session 036 design, Sprint-10D)
- **Decision:** Option A — refactor `workflows/frm_risk_register.py` in place.
- **Rationale:** Lowest regression risk; guided exercise pattern is FRM-specific.

### Mode B First for New Service Lines
- **Decision:** DD, Sanctions, TT — Mode B single-pass Sonnet. Upgrade path to full pipeline later.
- **Rationale:** Faster to ship; real GoodWork delivery does not require multi-agent review for screening memos.

### Historical Knowledge Library
- **Decision:** `tools/knowledge_library.py` with `SanitisationError` as HARD GATE.
- **Rationale:** PII leakage from historical reports into new engagement outputs is the highest-consequence failure mode (R-011).

---

## Risks and Constraints

| Risk | Impact | Mitigation |
|------|--------|-----------|
| R-001 Tavily free tier (1000/month) | Medium | Cache results locally per case_id |
| R-003 Arabic rendering in terminals | Low | Plain-text fallback; Streamlit renders correctly |
| R-009 No live FRM smoke test | High | P7-GATE required before FRM redesign merges |
| R-010 FRM redesign regression risk | High | Feature-flag or new workflow path until baseline passing |
| R-011 PII in historical library | High | SanitisationError HARD GATE in KnowledgeLibrary.sanitise() |
| R-012 Scope creep | Medium | Critical path enforced |

---

## Shipping Models

Six shipping models are defined for this product. Currently shipping: Models 1 (solo GoodWork install) and 2 (white-label solo install). Full specifications for all models, including architecture deltas and commercial models, are in `docs/product-packaging.md`.

| Model | Description | Status |
|---|---|---|
| 1 — Solo GoodWork Edition | Maher's own install, GoodWork branded | Shipping |
| 2 — White-Label Solo | Rebranded solo install for another practitioner | Phase 7 |
| 3 — Co-Work | 2–5 consultants, shared folder, lightweight auth | Future |
| 4 — Enterprise On-Premises | Staffed firm, RBAC, server deployment | Future |
| 5 — Multi-Tenant SaaS | GoodWork hosts, multiple firm subscribers | Separate product track |
| 6 — Managed Service | Client submission portal on top of solo install | When needed |

The pipeline, agents, hooks, and schemas are model-agnostic and reusable across all shipping models.

---

## Out-of-Scope for This Design

- Multi-user access or role-based permissions
- Cloud storage or remote sync
- WorldCheck / WorldCompliance integration
- HUMINT execution (scoping output only)
- Automated email/filing submission
- Statistical sampling computation (advisory only)
- Urdu-language adverse media search
