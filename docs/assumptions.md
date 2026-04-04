# Assumptions — GoodWork Forensic AI

---

## Confirmed
<!-- Assumptions explicitly agreed with AK and reflected in the build. -->

- Single user, multiple roles — one consultant runs the full case; can act as junior (adding material) or senior reviewer depending on context.
- No RAG — documents read in full; model builds a hierarchical directory index per case; zero technical setup for document handling.
- Local storage only — all case artifacts written to `cases/` on the user's machine; nothing stored server-side.
- English is always the primary deliverable; Arabic is a post-processing translation step, not a parallel workflow.
- CLI-only — no web interface, no browser; Rich terminal UI.
- Single-instance — one case at a time; no multi-user concurrency.
- Output formats: `.docx` and `.pptx` via python-docx / python-pptx; Markdown saved as backup.
- Engagement contract/scope letter required at intake for all case types — governs scope, limitations, and authorizations.
- Firm profile (team, pricing, T&C) collected once at first-time setup; stored in `firm_profile/`; loaded at proposal time.

## Inferred
<!-- Assumptions made during design that were not explicitly confirmed but are load-bearing. Verify with AK. -->

- Anthropic API cost per case is acceptable to the user at balanced/premium tier rates (~$0.20–$2.50 per FRM run).
- Tavily free tier (1000 searches/month) is sufficient for typical case volume.
- Users have Python 3.11+ and can follow a terminal-based setup wizard.
- Arabic deliverables are Gulf-dialect-appropriate MSA, not literal translation.

## Unresolved
<!-- Open questions that could change architecture or scope. Resolve before v1 release. -->

- What happens when a case involves multiple jurisdictions not covered by the four UAE regulators?
- Is there a defined SLA / turnaround time expectation that constrains model tier selection?
- Should the tool ever operate in a fully offline mode (no API calls)?
