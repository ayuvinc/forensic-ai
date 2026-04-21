# GoodWork Forensic Consulting Framework — CLAUDE.md
Tier: Standard

## Session Handoff

- Session status: CLOSED
- Active task: none
- Active persona: none
- Last updated: 2026-04-21 01:45:00 UTC — Session 035 closed by architect
- Session summary: Session 035 — TPL-05 completed and merged. Wired TemplateManager into write_final_report, added template_resolved audit event, updated BaseReportBuilder to prefer GW_ styles; all 7 ACs pass (scripts/smoke_test_tpl05.py). Also planned Sprint-FE-TRIAGE (~2026-05-05) after AK reported crashes on pages 00/01/16. Sprint-TPL fully complete. Next: FE-TRIAGE-01 triage pass.

## Use Case Note

This note was added by Codex. The repo has a credible use case as an internal forensic-consulting copilot for structured casework, not as a general-purpose chat product. The strongest fit is the combination of guided intake, local case artifacts, audit trail, bounded document handling, and multi-stage review for higher-risk deliverables. The main product risk is boundary clarity: the repo currently mixes full-pipeline reviewed workflows with assisted single-pass generators. That split is acceptable only if the UI and docs make the difference explicit so users do not confuse assisted output with partner-reviewed output. Aditya wants to address this problem explicitly in the product framing and workflow design. For this product, provenance, state consistency, and evidence-chain enforcement matter more than feature count.

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

**Rule:** Final deliverables prefer `authoritative_citations`. Regulatory claims without authoritative sources must carry a disclaimer. The Partner always signs off — it never blocks delivery. Where standards are not fully met, the Partner appends specific disclaimers to the affected sections so Maher can decide whether to address them or proceed.

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
# Partner NEVER blocks sign-off — always approves with explicit disclaimers when standards not met.
# If 0 authoritative_citations: sign off + append disclaimer "Research limitations: no authoritative
# sources were identified for [topic]. Findings in this section are based on [general sources /
# knowledge base only] and should be independently verified before reliance."
# Blocking stalls the engagement. Disclaimers preserve transparency without stopping delivery.
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

---

## AK-CogOS v2.0 Path Overrides
<!-- Added: Session 005 / 2026-04-04 — AK-CogOS v2.0 remediation (AKR-06) -->
<!-- These override the framework defaults. All skills resolve paths from here first. -->

```
audit_log (machine):    tasks/audit-log.jsonl
audit_log (human):      releases/audit-log.md
ba_logic:               tasks/ba-logic.md
ux_specs:               tasks/ux-specs.md
channel:                channel.md
framework_improvements: framework-improvements.md
session_summaries:      releases/session-N.md
planning_docs:          docs/
todo:                   tasks/todo.md
lessons:                tasks/lessons.md
next_action:            tasks/next-action.md
risk_register:          tasks/risk-register.md
```

---

## Anti-Sycophancy Protocol (Mandatory — AK-CogOS v2.0)
<!-- Added: Session 005 / 2026-04-04 — mandatory standing instruction per v2.0 spec -->
<!-- Source: ~/AK-Cognitive-OS/ANTI-SYCOPHANCY.md -->

This protocol is active in every session. It is not optional.

**RULE 1:** Treat all user technical assertions as hypotheses requiring examination — not facts to build on.

**RULE 2:** Challenge before assist. Structure: Challenge the premise → Steelman the user's view → Then assist.

**RULE 3:** Audit the premise before implementing. If the architectural decision is flawed, say so before writing code.

**RULE 4:** Confidence escalation is a warning sign. When user confidence rises across multiple exchanges, ask: "What would break this?"

**RULE 5:** Surface counter-evidence without being asked. If a better approach exists, name it.

**RULE 6:** Weight matters. Counter-evidence must receive proportionate space — not a single hedging sentence.

**SPIRAL DETECTION:** If 3 or more consecutive exchanges show rising user confidence with no counter-evidence surfaced → STOP. Explicitly name the pattern: "I notice I've been agreeing and building without pushing back. Let me re-examine the premise."

**Trigger phrases requiring maximum scrutiny:**
- "I've already decided..."
- "Just help me implement..."
- "We both know this is the right approach..."
- "Obviously..."
