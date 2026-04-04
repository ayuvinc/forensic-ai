# Scope Brief — GoodWork Forensic AI

_Populated via /ba discovery session — 2026-04-04_

---

## Must-Have

_Features that define the product. Non-negotiable for any usable version._

- **Case-type-specific guided intake** — different question sets for investigation vs FRM vs training vs proposal
- **Investigation report pipeline** — full three-stage review (draft → PM review → partner sign-off), evidence organization, findings language
- **FRM Risk Register** — 8-module risk identification pipeline, regulatory mapping, UAE-aware
- **Policy / SOP drafting** — single-pass assisted generation with regulatory references
- **Training material drafting** — role-specific, single-pass assisted generation
- **Client proposal drafting** — 7-section engagement proposal; loads firm profile (pricing, team, T&C)
- **Multi-session case resumability** — Maher works cases over multiple days; state must persist between sessions
- **Executive-ready language** — all output calibrated for CXO audience by default
- **Local artifact storage** — all case files saved to machine; nothing leaves without Maher's action
- **Full audit trail** — every event, decision, and revision recorded in `audit_log.jsonl`
- **Evidence / exhibit tracking** — documents registered, indexed, and referenced during drafting

## Should-Have

_High-value additions intended for v1 but not blocking launch._

- **Persona review** — CFO, Lawyer, UAE Regulator, Insurance Adjuster challenge perspective on any deliverable
- **Proposal deck (PPT prompt pack)** — storyboard + per-slide prompts for PowerPoint build
- **Arabic deliverables** — `final_report.ar.md` generated alongside English; Gulf-dialect appropriate
- **Case tracker** — view status and history of all cases
- **Browse SOPs** — review saved policies and procedures from prior cases

## Cut

_Items explicitly scoped out during planning._

- Automated eDiscovery integration (Outlook PST parsing, eDiscovery tool connectors) — Maher reviews raw evidence himself; tool works from his extracted exhibits, not raw data sources
- Automated financial data analysis (Excel model building, ratio analysis) — Maher does the analysis; tool structures the output

## Out-of-Scope

_Never to be built without a formal scope change._

- Performing investigations, drawing analytical conclusions, or making judgments — tool organizes and articulates Maher's conclusions only
- Legal opinions or expert witness output
- Multi-user / firm-wide system — single user (Maher) only
- Web interface or browser-based access — CLI only
- Cloud storage or remote sync — all data local
- Third-party CRM, billing, or practice management integrations
- Client portal or direct client access to the tool
- Automated filing with regulators
