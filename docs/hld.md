# High-Level Design — GoodWork Forensic AI

> Sections marked [DERIVED] are based on CLAUDE.md and confirmed code.
> Sections marked [TO VERIFY VIA /architect SESSION] require a discovery conversation before finalising.

---

## Architecture Overview [DERIVED]

CLI application. Python 3.11+. No web server, no database. All state is local file-based.

```
User
  └── run.py (entry point)
        ├── core/setup_wizard.py       (first-run: firm profile, API keys)
        ├── ui/menu.py                 (10-item Rich terminal menu)
        ├── ui/guided_intake.py        (conversational input → Pydantic schemas)
        └── workflows/                 (10 workflow modules)
              ├── [Mode A] investigation_report.py, frm_risk_register.py
              │     └── core/orchestrator.py
              │           ├── agents/junior_analyst/
              │           ├── agents/project_manager/
              │           └── agents/partner/
              └── [Mode B] client_proposal.py, proposal_deck.py, policy_sop.py, training_material.py
                    └── (single-model, direct API call)
```

## Data Flow [DERIVED]

```
Intake (guided conversation)
  → CaseIntake (Pydantic schema)
  → Pre-hooks: validate → normalize_language → sanitize_pii → attach_metadata
  → Agent pipeline (Mode A) or direct generation (Mode B)
  → Post-hooks: validate_schema → enforce_evidence_chain → persist_artifact
               → append_audit_event → extract_citations → render_markdown
  → cases/{case_id}/ (local filesystem)
```

## Agent Pipeline (Mode A only) [DERIVED]

```
State: INTAKE_CREATED
  → Junior Analyst (Haiku/Sonnet)  → JUNIOR_DRAFT_COMPLETE
  → Project Manager (Haiku/Sonnet) → PM_REVIEW_COMPLETE | PM_REVISION_REQUESTED
      [revision loop: max 3 junior rounds, 2 PM rounds]
  → Partner (Sonnet/Opus)          → PARTNER_REVIEW_COMPLETE | PARTNER_REVISION_REQ
  → OWNER_READY → OWNER_APPROVED | OWNER_REJECTED
```

Each agent is loaded from a plugin manifest (`agents/{name}/manifest.json`) defining:
- Allowed tools, max turns, timeout, revision capability, input/output schemas

## Key Integrations [DERIVED]

| Integration | Purpose | Trust Level |
|---|---|---|
| Anthropic API | All LLM calls (Claude Haiku/Sonnet/Opus) | Internal |
| Tavily | General web research | External — low-trust flag on results |
| UAE regulatory APIs (cb.gov.ae, dfsa.ae, adgm.com, sca.gov.ae) | Authoritative regulatory lookup | Authoritative only |
| OFAC / UN / EU sanctions | Authoritative sanctions check | Authoritative only |
| python-docx / python-pptx | .docx and .pptx generation | Local |

## State Machine [DERIVED]

See `core/state_machine.py`. Full transition graph in CLAUDE.md under "State Machine".
Terminal states: OWNER_APPROVED, OWNER_REJECTED, PIPELINE_ERROR.
Resume: if state.json has non-terminal status, orchestrator offers resume on next run.
Resume only available for Mode A workflows (investigation_report, frm_risk_register).

## Hook Chain [DERIVED]

Pre-hooks (5, in order): validate_input (blocking) → normalize_language → sanitize_pii → attach_case_metadata
Post-hooks (6, in order): validate_schema (blocking) → enforce_evidence_chain (blocking, Mode A only) → persist_artifact → append_audit_event → extract_citations → render_markdown

Hooks are pure functions: (payload, context) → payload. HookVetoError blocks the pipeline.

## File Conventions [DERIVED]

- Artifact naming: `{agent}_{artifact_type}.v{N}.json`
- Case folder: `cases/{case_id}/state.json`, `audit_log.jsonl`, `citations_index.json`, per-agent outputs
- Audit log: `tasks/audit-log.jsonl` (machine) + `releases/audit-log.md` (human)
- Firm data: `firm_profile/` (excluded from git)

## Gaps / To Verify [TO VERIFY VIA /architect SESSION]

- Exact data flow for Mode B workflows (no hook chain confirmed for these yet — C-01c open)
- Document ingestion flow end-to-end (C-04 partially wired — not user-reachable yet)
- Bilingual pipeline: how Arabic translation is triggered and when content_ar is populated vs null
- Proposal deck: exact chaining between client_proposal (Option 7) and proposal_deck (Option 8)
- Multi-module FRM dependency enforcement: exact runtime check for Module 3 requiring Module 2
