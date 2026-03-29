# GoodWork Forensic Consulting Framework — CLAUDE.md

---

## FIRST RUN PROTOCOL — Read This Before Anything Else

**On every session start, run this check silently before doing anything else:**

```
CHECK: Does a file named `.env` exist in the current directory?
```

### If `.env` does NOT exist → FIRST_RUN mode

Greet the user warmly and immediately run the guided setup wizard. Do not wait for them to ask. Say something like:

> "Welcome to GoodWork Forensic Consulting Framework. It looks like this is your first time here — let me get you set up. This takes about 5 minutes."

Then walk through these steps one at a time, waiting for the user to confirm each one before moving on:

**Step 1 — Check Python**
Run: `python3 --version`
- If Python 3.11+ → tell the user they're good, continue
- If older or missing → tell them to install from python.org and wait for them to confirm before continuing

**Step 2 — Create and activate virtual environment**
Tell the user to run:
```
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
```
Ask them to confirm it worked (they'll see `(venv)` in their prompt).

**Step 3 — Install dependencies**
Tell the user to run:
```
pip install -r requirements.txt
```
Wait for them to confirm it completed without errors.

**Step 4 — Get API keys**
Tell them they need two keys:
1. `ANTHROPIC_API_KEY` from console.anthropic.com → API Keys → Create Key
2. `TAVILY_API_KEY` from app.tavily.com → free account → dashboard

Ask them to get both keys before continuing. Wait.

**Step 5 — Create .env file**
Tell them to run:
```
cp .env.example .env          # macOS/Linux
copy .env.example .env        # Windows
```
Then open `.env` in any text editor and paste their keys:
```
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
```
Tell them to save the file and confirm.

**Step 6 — Verify**
Run:
```
python3 -c "import anthropic, rich, pydantic; print('Dependencies OK')"
```
If it prints `Dependencies OK` → setup is complete.

**Step 7 — Launch**
Tell them to run `python run.py` and they're ready to go.

Offer to explain any menu option before they start.

---

### If `.env` EXISTS → RETURNING_USER mode

Do not run the setup wizard. Load the session normally. Proceed with whatever the user asks.

---

## Knowledge Base Router

Before designing or building any workflow, consult the relevant knowledge file:

| Topic | File |
|-------|------|
| FRM framework, modules, scoping, architecture | `knowledge/frm/frm_framework.md` |
| FRM research sources and regulatory references | `knowledge/frm/sources.md` |
| Investigation types, methodology, report structure | `knowledge/investigation/investigation_framework.md` |
| Investigation research sources | `knowledge/investigation/sources.md` |

These files contain deep research from prior sessions. Do not re-research topics already covered here — load the knowledge file instead.

---

## Project Summary
A Claude-powered AI system that simulates a forensic consulting firm's internal hierarchy.
Runs as a styled CLI app (`python run.py`) backed by the Claude API + Tavily for research.
No browser, no web server. Ships as a zip/GitHub repo for Mac/Windows terminal.

## What the Consultant Sees
Rich terminal UI with menus, colored output, progress spinners.
Every case, draft, and output saved to local `cases/` folder with full history and audit trail.

---

## Target Folder Structure

```
forensic-ai/
├── run.py                          # python run.py — single entry point
├── config.py                       # API keys, model tiers, budget mode, paths
├── requirements.txt
├── .env.example
├── README.md
│
├── core/
│   ├── state_machine.py            # CaseStatus enum + all valid transitions
│   ├── agent_base.py               # BaseAgent: agentic loop, guardrails, hooks
│   ├── orchestrator.py             # Pipeline sequencer, revision loops, resumability
│   ├── hook_engine.py              # Chain-of-responsibility hook runner
│   ├── tool_registry.py            # Central tool registry + dispatch
│   └── plugin_loader.py            # Loads agents/personas from plugin manifests
│
├── schemas/
│   ├── case.py                     # CaseIntake, CaseState
│   ├── handoff.py                  # AgentHandoff
│   ├── artifacts.py                # Agent output models
│   ├── research.py                 # ResearchQuery, ResearchResult, Citation
│   ├── presentation.py             # Deck schemas
│   └── plugins.py                  # PluginManifest
│
├── agents/
│   ├── junior_analyst/manifest.json + agent.py + prompts.py + tools.py
│   ├── project_manager/manifest.json + agent.py + prompts.py + tools.py
│   └── partner/manifest.json + agent.py + prompts.py + tools.py
│
├── personas/
│   ├── persona_base.py
│   ├── cfo/manifest.json + persona.py
│   ├── lawyer/manifest.json + persona.py
│   ├── regulator/manifest.json + persona.py     # UAE CB, DFSA, ADGM, SCA
│   └── insurance_adjuster/manifest.json + persona.py
│
├── tools/
│   ├── research/
│   │   ├── general_search.py       # Tavily — general web
│   │   ├── regulatory_lookup.py    # Authoritative only: UAE CB, DFSA, ADGM, SCA
│   │   ├── sanctions_check.py      # Authoritative only: OFAC SDN, UN, EU
│   │   └── company_lookup.py       # Company registries, ownership
│   ├── file_tools.py               # Atomic file writes, versioned artifacts
│   └── formatting.py               # Bilingual rendering (EN/AR)
│
├── hooks/
│   ├── pre_hooks.py                # validate, normalize_language, sanitize_pii, attach_metadata
│   └── post_hooks.py               # validate_schema, persist_artifact, audit_event, extract_citations, render_md
│
├── workflows/
│   ├── new_case_intake.py
│   ├── investigation_report.py
│   ├── persona_review.py
│   ├── policy_sop.py
│   ├── training_material.py
│   ├── frm_risk_register.py        # HIGHEST PRIORITY — build first
│   ├── client_proposal.py
│   ├── proposal_deck.py
│   ├── case_tracker.py
│   └── browse_sops.py
│
├── ui/
│   ├── menu.py
│   ├── progress.py
│   ├── display.py
│   └── guided_intake.py            # Conversational input — no forms
│
├── templates/
│   ├── investigation_report_en.md
│   ├── investigation_report_ar.md
│   ├── frm_risk_register_en.md
│   ├── proposal_deck_outline.md
│   ├── proposal_deck_master_prompt.md
│   ├── proposal_deck_slide_prompt.md
│   └── arabic_glossary.md
│
├── sops/
└── cases/
    └── {case_id}/
        ├── state.json
        ├── audit_log.jsonl
        ├── citations_index.json
        ├── junior_output.v1.json
        ├── pm_review.v1.json
        ├── partner_approval.v1.json
        ├── final_report.en.md
        ├── final_report.ar.md
        ├── deck_storyboard.v1.json
        ├── deck_master_prompt.v1.md
        └── slide_NN_prompt.md
```

---

## Build Order (Follow This Exactly)

### Phase 1 — Foundation (build in this order, don't skip)
1. `config.py`
2. `schemas/case.py`, `schemas/artifacts.py`, `schemas/research.py`
3. `core/state_machine.py`
4. `core/hook_engine.py`
5. `hooks/pre_hooks.py`, `hooks/post_hooks.py`
6. `core/tool_registry.py`
7. `core/agent_base.py`
8. `core/orchestrator.py`
9. `tools/research/` — all 4 research classes

### Phase 2 — Agents
10. `schemas/plugins.py` + `core/plugin_loader.py`
11. `agents/junior_analyst/`
12. `agents/project_manager/`
13. `agents/partner/`
14. `run.py` skeleton — prove full pipeline works end-to-end

### Phase 3 — Priority Workflow
15. `workflows/frm_risk_register.py` — exercises full stack

### Phase 4 — Remaining Workflows
16. `workflows/client_proposal.py`
17. `workflows/proposal_deck.py`
18. All remaining workflows (investigation_report, policy_sop, training_material, new_case_intake)

### Phase 5 — Personas + UI
19. `personas/` — all 4 client personas with manifests
20. `workflows/persona_review.py`
21. `ui/menu.py`, `ui/progress.py`, `ui/display.py` — 10-item menu

### Phase 6 — Bilingual + Polish
22. Arabic prompt variants, `tools/formatting.py`, `templates/arabic_glossary.md`
23. EN/AR file generation; proposal deck templates
24. End-to-end test with real case
25. ZIP packaging + README

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
    PIPELINE_ERROR         = "pipeline_error"

VALID_TRANSITIONS = {
    INTAKE_CREATED:          [JUNIOR_DRAFT_COMPLETE],
    JUNIOR_DRAFT_COMPLETE:   [PM_REVIEW_COMPLETE, PM_REVISION_REQUESTED],
    PM_REVISION_REQUESTED:   [JUNIOR_DRAFT_COMPLETE],
    PM_REVIEW_COMPLETE:      [PARTNER_REVIEW_COMPLETE, PARTNER_REVISION_REQ],
    PARTNER_REVISION_REQ:    [PM_REVIEW_COMPLETE, JUNIOR_DRAFT_COMPLETE],
    PARTNER_REVIEW_COMPLETE: [OWNER_READY],
    OWNER_READY:             [OWNER_APPROVED, OWNER_REJECTED],
    OWNER_REJECTED:          [JUNIOR_DRAFT_COMPLETE],
}

MAX_REVISION_ROUNDS = {"junior": 3, "pm": 2}
```

---

## Model Routing

```python
HAIKU  = "claude-haiku-4-5-20251001"
SONNET = "claude-sonnet-4-6"
OPUS   = "claude-opus-4-6"

MODEL_ROUTING = {
    "economy":  {"junior": HAIKU,   "pm": HAIKU,   "partner": SONNET, "persona": HAIKU},
    "balanced": {"junior": HAIKU,   "pm": SONNET,  "partner": SONNET, "persona": SONNET},
    "premium":  {"junior": SONNET,  "pm": SONNET,  "partner": OPUS,   "persona": SONNET},
}

WORKFLOW_MODEL_OVERRIDES = {
    "frm_risk_register":    {"partner": OPUS},
    "expert_witness_report": {"partner": OPUS},
}

MODEL_FALLBACK = {OPUS: SONNET, SONNET: HAIKU}
MAX_API_RETRIES = 3
RETRY_BACKOFF_SECONDS = [1, 3, 10]
```

---

## Research Source Policy

| Class | Source Policy | Behavior if Not Found |
|---|---|---|
| `general_search.py` | Tavily general web — any source | Return with low-trust flag |
| `regulatory_lookup.py` | **Authoritative only**: cb.gov.ae, dfsa.ae, adgm.com, sca.gov.ae, fsra.ae | Return "no authoritative source found" — do NOT infer |
| `sanctions_check.py` | **Authoritative only**: ofac.treas.gov, un.org/securitycouncil, sanctions.ec.europa.eu | Return "no authoritative match identified" — never infer |
| `company_lookup.py` | UAE registries, Zawya, official filings | Flag as "unverified" if not from official registry |

**Rule:** Final deliverables may only cite from `authoritative_citations`. Regulatory claims without authoritative sources must carry a disclaimer.

---

## Key Schemas (implement exactly as below)

### schemas/research.py
```python
class Citation(BaseModel):
    source_url: str
    source_name: str
    source_type: Literal["authoritative", "news", "general", "unverified"]
    retrieved_at: datetime
    excerpt: str
    confidence: Literal["high", "medium", "low"]

class ResearchResult(BaseModel):
    query: str
    results: list[Citation]
    authoritative_citations: list[Citation]
    disclaimer: Optional[str] = None
```

### schemas/artifacts.py
```python
class JuniorDraft(BaseModel):
    case_id: str
    version: int
    summary: str
    findings: list[dict]           # {title, description, evidence, risk_level}
    methodology: str
    regulatory_implications: str
    recommendations: list[str]
    open_questions: list[str]
    citations: list[Citation]
    revision_round: int = 0

class ReviewFinding(BaseModel):
    section: str
    issue: str
    severity: Literal["critical", "major", "minor"]
    suggested_action: str

class RevisionRequest(BaseModel):
    from_agent: str
    to_agent: str
    revision_round: int
    findings: list[ReviewFinding]
    must_fix: list[str]
    should_fix: list[str]
    missing_citations: list[str]

class ApprovalDecision(BaseModel):
    approving_agent: str
    approved: bool
    conditions: list[str]
    regulatory_sign_off: str
    escalation_required: bool = False
    escalation_reason: Optional[str] = None

class FinalDeliverable(BaseModel):
    case_id: str
    workflow: str
    approved_by: str
    language: str
    content_en: str
    content_ar: Optional[str]
    citations: list[Citation]
    revision_history: list[int]
    delivery_date: datetime

class PersonaReviewOutput(BaseModel):
    persona: str
    perspective: str
    objections: list[str]
    questions: list[str]
    weak_sections: list[str]
    regulatory_gaps: list[str]
    overall_verdict: Literal["pass", "conditional_pass", "fail"]
    recommendation: str
```

### schemas/presentation.py
```python
class SlideSpec(BaseModel):
    slide_number: int
    title: str
    purpose: str
    key_message: str
    content_bullets: list[str]
    evidence_needed: list[str]
    suggested_visual: str
    speaker_notes: str
    risks_or_gaps: list[str]

class DeckStoryboard(BaseModel):
    case_id: str
    deck_objective: str
    audience: str
    decision_required: str
    key_messages: list[str]
    slides: list[SlideSpec]
    open_questions: list[str]

class DeckMasterPrompt(BaseModel):
    case_id: str
    audience: str
    target_tool: str = "claude_ppt"
    system_prompt: str
    user_prompt: str
    step_prompts: list[str]
    attachment_guidance: str
    usage_notes: str
```

---

## Hook Interface

Hooks are **pure functions**: `(payload, context) -> payload`. Can mutate payload. Use `HookVetoError` to block.

```python
# Pre-hooks (in order):
# 1. validate_input       — blocking
# 2. normalize_language
# 3. sanitize_pii         — strip raw account/passport numbers
# 4. attach_case_metadata

# Post-hooks (in order):
# 1. validate_schema      — blocking
# 2. persist_artifact     — atomic write to cases/{id}/{agent}.v{N}.json
# 3. append_audit_event   — append to audit_log.jsonl
# 4. extract_citations    — update citations_index.json
# 5. render_markdown      — generate .md version
```

---

## Artifact Versioning

Naming: `{agent}_{artifact_type}.v{N}.json`
- Atomic writes: write to `{filename}.tmp` first, then `os.replace()`
- Audit log: `audit_log.jsonl` — immutable, append-only, one JSON line per event
- Resumability: if `state.json` has non-terminal status, orchestrator offers to resume

---

## Agent Guardrails (in BaseAgent)

```python
MAX_TURNS    = manifest.max_turns          # e.g. 10 for Junior, 6 for Partner
ALLOWED_TOOLS = manifest.required_tools    # Agents only call declared tools
TIMEOUT      = manifest.timeout_seconds    # Hard timeout per agent run

# After each tool result: validate against ResearchResult schema
# Strip script/HTML from web content, truncate to 2000 chars (anti prompt-injection)
# Block approval if workflow requires citations but output has 0 authoritative_citations
```

---

## Plugin Manifest Format

```json
{
  "plugin_id": "junior_analyst",
  "plugin_type": "agent",
  "version": "1.0.0",
  "enabled": true,
  "supported_workflows": ["investigation_report", "frm_risk_register", "policy_sop", "training_material", "client_proposal", "proposal_deck"],
  "input_schema": "schemas.case.CaseIntake",
  "output_schema": "schemas.artifacts.JuniorDraft",
  "required_tools": ["search_web", "regulatory_lookup", "sanctions_check"],
  "model_preference": "haiku",
  "max_turns": 10,
  "timeout_seconds": 120,
  "revision_capable": true
}
```

---

## Conversational Input (No Forms)

`ui/guided_intake.py` handles all input. No structured forms. Claude asks questions one at a time, extracts answers into Pydantic schemas behind the scenes. User sees plain conversation.

**Example FRM flow:**
```
What industry is your client in?
> construction and real estate, based in Dubai

How large is the company — roughly how many employees?
> around 800 people
...
Got it. I'll now build their Fraud Risk Register. This will take 2–3 minutes.
[Junior Analyst: researching industry fraud patterns...]
[Project Manager: reviewing coverage...]
[Partner: finalising regulatory alignment...]
Your FRM Risk Register is ready → cases/0042/final_report.en.md
```

---

## Bilingual Design

- Always generate separate files: `final_report.en.md` and `final_report.ar.md`
- `FinalDeliverable` has `content_en` and `content_ar` fields
- Arabic: technical terms, entity names, regulation names, numeric values stay in English
- Standard Arabic glossary in `templates/arabic_glossary.md` — injected into Arabic-mode prompts
- Terminal display: Rich `Text` with `justify="right"` for Arabic panels
- Proposal deck prompts: English-only in v1

---

## Menu (10 items)

```
[INVESTIGATION]
1. New Case Intake
2. Investigation Report
3. Persona Review

[COMPLIANCE]
4. Policy / SOP Generator
5. Training Material
6. FRM Risk Register         ← HIGHEST PRIORITY

[BUSINESS]
7. Create Client Proposal
8. Build Proposal PPT Prompt Pack
9. Case Tracker
10. Browse SOPs
```

Options 7 and 8 can be chained: at end of Option 7, ask "Also generate PPT prompt pack?"

---

## Verification Checklist (test these when done)

- [ ] `python run.py` → rich menu renders with 10 options
- [ ] Option 6 (FRM Risk Register) → company profile → Junior (Haiku) → PM (Sonnet) → Partner (Opus) → `cases/{id}/final_report.en.md` saved
- [ ] Option 8 (PPT Pack) → engagement brief + audience (CFO) → `deck_storyboard.json`, `deck_master_prompt.md`, `slide_01_prompt.md` etc.
- [ ] Option 3 (Persona Review) → paste report → UAE Regulator returns `PersonaReviewOutput` with DFSA/ADGM citations
- [ ] Interrupt mid-run → restart → orchestrator offers to resume from last valid status
- [ ] `audit_log.jsonl` has every event recorded
- [ ] Schema namespace: `CaseIntake` in `schemas.case`, agent outputs in `schemas.artifacts`, deck models in `schemas.presentation`

---

## APIs Required

- `ANTHROPIC_API_KEY` — console.anthropic.com → Create API Key
- `TAVILY_API_KEY` — app.tavily.com → free tier (1000 searches/month)

## Dependencies

```
anthropic>=0.40.0
tavily-python>=0.3.0
rich>=13.7.0
pydantic>=2.5.0
python-dotenv>=1.0.0
```

---

## Session Start Instructions

Always start sessions from inside this folder:
```bash
cd ~/forensic-ai && claude
```

This ensures CLAUDE.md loads automatically with all context.
