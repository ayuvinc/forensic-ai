# Release Truth — GoodWork Forensic AI

Honest assessment of feature status. Updated at each session close.
Last updated: Session 006 (2026-04-04).

---

## Legend

| Status | Meaning |
|--------|---------|
| REAL | Implemented and verified end-to-end with live API |
| STRUCTURAL | Code present, all imports clean, static/structural tests pass — NOT live-tested |
| PARTIAL | Code present but not fully wired into the user journey |
| STUB | File exists with section headers only |
| MISSING | Not yet created |

---

## Core Infrastructure

| Module | Status | Notes |
|--------|--------|-------|
| config.py | STRUCTURAL | Model routing, budget mode, paths all coded |
| core/state_machine.py | STRUCTURAL | QR-03 PASS — transitions verified statically |
| core/hook_engine.py | STRUCTURAL | QR-04 PASS — chain verified statically |
| hooks/pre_hooks.py | STRUCTURAL | 5-stage chain verified QR-04 |
| hooks/post_hooks.py | STRUCTURAL | 6-stage chain (incl. enforce_evidence_chain) verified QR-04, QR-16 |
| core/tool_registry.py | STRUCTURAL | QR-05 PASS + BUG-01 fix applied |
| core/agent_base.py | STRUCTURAL | Agentic loop, guardrails, timeout coded |
| core/orchestrator.py | STRUCTURAL | QR-06, QR-07, QR-08 PASS — revision loop + resume verified statically |
| core/plugin_loader.py | STRUCTURAL | Manifest loading coded |
| core/setup_wizard.py | STRUCTURAL | Wizard flow coded; not run with real env |

## Research Tools

| Module | Status | Notes |
|--------|--------|-------|
| tools/research/general_search.py | STRUCTURAL | QR-09 PASS — domain filter, trust flag verified |
| tools/research/regulatory_lookup.py | STRUCTURAL | Authoritative-only domain filter coded |
| tools/research/sanctions_check.py | STRUCTURAL | OFAC/UN/EU authoritative-only coded |
| tools/research/company_lookup.py | STRUCTURAL | UAE registry lookup coded |

## Schemas

| Module | Status | Notes |
|--------|--------|-------|
| schemas/case.py | STRUCTURAL | QR-02 PASS |
| schemas/artifacts.py | STRUCTURAL | QR-02 PASS |
| schemas/research.py | STRUCTURAL | QR-02 PASS |
| schemas/presentation.py | STRUCTURAL | QR-02 PASS |
| schemas/documents.py | STRUCTURAL | QR-02 PASS |
| schemas/evidence.py | STRUCTURAL | QR-02 PASS, QR-15 PASS |
| schemas/handoff.py | STRUCTURAL | QR-02 PASS |
| schemas/plugins.py | STRUCTURAL | QR-02 PASS |

## Agents

| Module | Status | Notes |
|--------|--------|-------|
| agents/junior_analyst/ | STRUCTURAL | Manifest + prompts + tools coded; no live run |
| agents/project_manager/ | STRUCTURAL | Manifest + prompts + tools coded; no live run |
| agents/partner/ | STRUCTURAL | _enforce_evidence_chains() coded + QR-16 PASS; no live run |

## Workflows

| Workflow | Mode | Status | Notes |
|----------|------|--------|-------|
| frm_risk_register.py | A (Full Pipeline) | STRUCTURAL | QR-13 PASS; 8-module structure verified; no live run |
| investigation_report.py | A (Full Pipeline) | STRUCTURAL | Evidence chain wired (C-03); no live run |
| client_proposal.py | B (Assisted) | PARTIAL | Coded; firm profile loading untested; PQA-01..12 not run |
| proposal_deck.py | B (Assisted) | PARTIAL | Coded; PQA-07..12 not run |
| policy_sop.py | B (Assisted) | REAL | Smoke test PASSED Session 009 — Whistleblower Policy generated, 4 citations, final_report.en.md written |
| training_material.py | B (Assisted) | STRUCTURAL | Coded; no live run |
| new_case_intake.py | Utility | STRUCTURAL | Coded; not tested |
| persona_review.py | Standalone | STRUCTURAL | Coded; not tested |
| case_tracker.py | Utility | PARTIAL | C-02 open: only discovers orchestrated cases correctly |
| browse_sops.py | Utility | STRUCTURAL | Coded; sops/ directory empty |

## Personas

| Persona | Status | Notes |
|---------|--------|-------|
| personas/cfo/ | STRUCTURAL | Manifest + persona coded |
| personas/lawyer/ | STRUCTURAL | Manifest + persona coded |
| personas/regulator/ | STRUCTURAL | Manifest + persona coded; DFSA/ADGM citations referenced |
| personas/insurance_adjuster/ | STRUCTURAL | Manifest + persona coded |

## UI & Tools

| Module | Status | Notes |
|--------|--------|-------|
| ui/menu.py | STRUCTURAL | Mode labels (Assisted/Full pipeline) present |
| ui/guided_intake.py | STRUCTURAL | Conversational input coded |
| ui/progress.py | STRUCTURAL | Rich spinner coded |
| ui/display.py | STRUCTURAL | Rich panels coded |
| tools/document_manager.py | PARTIAL | QR-14 PASS; wired into options 2+6 (F-EXT-03) but not user-reachable via menu (C-04 open) |
| tools/formatting.py | STRUCTURAL | Arabic translation coded; not tested |
| tools/output_generator.py | STRUCTURAL | .docx/.pptx generation coded; not tested |
| tools/evidence/* | STRUCTURAL | QR-15, QR-16 PASS on classifier; email/excel parsers coded |
| tools/file_tools.py | STRUCTURAL | QR-10 PASS — atomicity + envelope confirmed |

## Infrastructure / Docs

| Artifact | Status | Notes |
|----------|--------|-------|
| tasks/audit-log.jsonl | REAL | Machine audit log actively written by all agents |
| releases/audit-log.md | REAL | Human-readable mirror; created Session 005 |
| .gitignore | REAL | covers cases/, firm_profile/, .env, venv/, etc. |
| README.md | PARTIAL | C-05 partially fixed; resumability section still implies all workflows resume |
| docs/ | STUB | 7 stub files created Session 006; content pending /ba + /architect sessions |
| releases/session-001..005.md | REAL | Created Session 006 (001–004) + Session 005 by session-close |
| templates/ | PARTIAL | arabic_glossary.md present; 6 report/deck templates missing |
| sops/ | MISSING | Directory not created; browse_sops.py has nothing to browse |
| firm_profile/ | MISSING | Created at first-time setup via wizard; not committed to git |
| cases/ | MISSING | Created at runtime; not committed to git |

---

## Summary

- **57 Python modules**: all import-clean (QR-01 PASS)
- **QR gates passed**: QR-01..16 (static + structural)
- **Live end-to-end test**: NOT RUN (R-002 open)
- **Real features** (REAL status): audit-log.jsonl, releases/audit-log.md, .gitignore, session summaries
- **Biggest gap**: C-04 (document ingestion not user-reachable), C-06 (zero integration tests), R-002 (no smoke test)
