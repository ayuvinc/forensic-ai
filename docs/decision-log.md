# Decision Log — GoodWork Forensic AI

Append-only. Each entry: date | decision | rationale | alternatives considered.

---

## Confirmed Architectural Decisions

| Date | Decision | Rationale | Alternatives Considered |
|------|----------|-----------|------------------------|
| 2026-03-29 | Model routing via economy/balanced/premium tiers | Lets user control cost vs quality; FRM and expert witness auto-upgrade Partner to Opus | Fixed model per agent; per-request selection |
| 2026-03-29 | Artifact writes: atomic (.tmp → os.replace()) | Prevents partial writes from leaving corrupt state.json or agent outputs | Direct write; database |
| 2026-03-29 | Evidence-chain enforcement: code-level gate, not prompt | Prompt-only enforcement was C-03 finding — LLM can silently ignore it; hard gate is non-negotiable for admissibility | Prompt-only (rejected after C-03) |
| 2026-03-29 | Mode A/B split: Full Pipeline vs Assisted Generation | Investigation and FRM are high-stakes, multi-reviewer; other workflows are lower-risk drafting aids | Uniform pipeline for all (too slow/expensive for low-stakes tasks) |
| 2026-03-29 | No RAG — documents read in full with hierarchical index | Zero technical setup for user; model can navigate large docs via index; avoids retrieval quality issues | Vector DB / RAG (rejected: requires setup, adds failure mode) |
| 2026-03-29 | Global jurisdiction support | UAE/Saudi primary markets but consultant may have global clients; regulatory mapping is dynamic | UAE-only hardcoded (rejected: too limiting) |
| 2026-03-29 | English primary, Arabic post-delivery | Arabic is contextual translation, not a parallel workflow; avoids dual-maintenance of prompts | Arabic-first; fully parallel bilingual (both rejected: complexity vs value) |
| 2026-03-29 | No forms — conversational intake only | Guided conversation extracts structured Pydantic schemas transparently; better UX for non-technical users | Web form; YAML config file |
| 2026-03-29 | Output as .docx/.pptx + Markdown backup | Client-facing deliverables must be editable in Word/PowerPoint; Markdown as fallback | PDF-only; Markdown-only |
| 2026-03-29 | Firm profile collected once at setup | Prevents re-entering credentials, pricing, team bios on every proposal | Per-proposal entry; config file only |
| 2026-04-02 | Partner approval blocked at code level on LEAD_ONLY/INADMISSIBLE evidence | HookVetoError raised regardless of LLM output — ACFE admissibility standard enforced by runtime, not instruction | Prompt-only enforcement (rejected per C-03) |

---

| 2026-04-04 | Two-layer architecture: Engine (generic) + Instance Pack (firm-specific) | Enables blank framework packaging for other consulting firms without refactoring the engine; GoodWork is the first instance | Single-repo monolith (rejected: ties engine to GoodWork); separate repos (rejected: dependency management overhead for solo practitioner) |
| 2026-04-04 | Blank framework gated on GoodWork smoke test | Cannot sell a blank framework derived from code that has never executed end-to-end; smoke test is the proof of concept | Build in parallel (rejected: risk of selling an unvalidated product) |
| 2026-04-04 | instance_config/firm.json as the instance boundary | Single config file defines what's firm-specific; engine reads it at startup; new firm edits this file only | Per-file config (rejected: too scattered); environment variables (rejected: too technical for non-dev firms) |

## Open Decisions
<!-- Decisions not yet made. Capture here to track. -->

- C-01b: Should client_proposal be upgraded to the full orchestrated pipeline (Junior→PM→Partner)? Currently Mode B. High effort but closes quality gap for highest-value workflow.
- C-02a: Which terminal status should Mode B workflows use when complete? OWNER_APPROVED (reuse existing) or a new DELIVERABLE_WRITTEN state?
