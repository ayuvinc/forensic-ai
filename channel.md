# CHANNEL — Session Broadcast

## Current State
- Sessions completed: 001, 002, 003
- Last closed: 2026-03-29
- Framework status: structurally complete (57 modules), QA-verified, pending smoke test

## What Was Built (cumulative)
- Sprint-01: Phase 1 Foundation — 18 files (config, schemas, core, hooks, tools)
- Sprint-02: Phases 2–6 — 49 modules (agents, workflows, UI, personas, bilingual, run.py)
- Sprint-03: Bug fixes + external findings resolved (F-EXT-01..03), Codex review findings logged

## Findings Log (all sessions)

### Sprint-01 Codex Findings — ALL RESOLVED
| ID | Finding | Fix |
|----|---------|-----|
| F1 | plugin_id conflicts with model routing | Added role: str to PluginManifest |
| F2 | Agent output contract misaligned with resume | ArtifactEnvelope (persist) vs AgentHandoff (in-memory) |
| F3 | Full-read document approach not viable | Bounded retrieval: read_excerpt/read_pages/read_section |
| F4 | operating_jurisdictions loses primary venue | Added primary_jurisdiction: str = "UAE" |
| F5 | Tool names drift from registry | Canonical IDs frozen in plan |
| F6 | Evidence permissibility under-modeled | DocumentProvenance + EvidenceClassifier |
| F7 | Setup wizard expanded too early | Firm profile moved to Phase 2 |

### Sprint-02 Codex Findings — ALL RESOLVED
| ID | Sev | Finding | Fix |
|----|-----|---------|-----|
| P3 | S2 | RiskItem.model_post_init uses object.__setattr__ | @model_validator(mode="after") |
| P4 | S1 | _sanitize() truncates doc tools (nullifies bounded retrieval) | _WEB_TOOLS frozenset, doc tools skip truncation |
| P5 | S2 | orchestrator._load_last_output() bypasses load_envelope() | Rewrote to use load_envelope() + _ARTIFACT_ROLES |
| P6 | S2 | PermissibilityStatus is plain str subclass | class PermissibilityStatus(str, Enum) |
| BUG-01 | — | ToolRegistry.call(name=...) kwarg collision | Renamed param to tool_name |

### Sprint-03 External Review Findings — ALL RESOLVED
| ID | Sev | Finding | Fix |
|----|-----|---------|-----|
| F-EXT-01 | Med | Guided intake paths (options 2–8) never wrote intake.json/state.json | _persist_intake() in run.py |
| F-EXT-02 | Med | README claimed EN+Arabic by default; generate_arabic flag never set | README corrected; flag wired from intake.language=="ar" |
| F-EXT-03 | Low | DocumentManager not instantiated in run.py | Options 2 and 6 now instantiate DocumentManager |

### Sprint-03 Codex Review Findings — LOGGED TO TODO (pending)
| ID | Sev | Finding | Todo items |
|----|-----|---------|-----------|
| C-01 | Med | Two quality standards: full pipeline vs single-model generators | C-01a/b/c |
| C-02 | Med | Mode B workflows don't update state.json after completion | C-02a/b |
| C-03 | Med | Evidence-chain validation prompt-only, not code-enforced | C-03a/b/c — HIGH PRIORITY |
| C-04 | Low | No UI entry to ingest documents into a case | C-04a/b/c |
| C-05 | Low | README resumability claims broader than runtime | C-05a/b |
| C-06 | Low | No scripted integration tests | C-06a–e |
| C-07 | Low | No .gitignore | DONE this session |

## Next Session
Read tasks/todo.md → PENDING TASKS section.
Priority order: C-03 (evidence enforcement) → C-01 (workflow quality split) → PQA-01..12 (proposal QA) → C-02 (state persistence) → smoke test when API keys ready.
