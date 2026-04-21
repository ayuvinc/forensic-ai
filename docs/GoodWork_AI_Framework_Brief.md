# GoodWork AI Forensic Framework
## Executive Brief — GoodWork LLC

---

## What It Is

A private, local AI system that runs the complete internal operations of a forensic consulting firm — from the first scoping conversation with a prospect to the signed final deliverable.

It is not a chatbot. It is not a document template tool. It is not a generic AI assistant.

It is a **role-simulated forensic workbench** that mirrors how a real staffed forensic firm operates: a Junior Analyst researches and drafts, a Project Manager reviews and challenges, a Partner signs off — all governed by ACFE standards, UAE and GCC regulatory requirements, and a full immutable audit trail. The consultant drives every decision. No output leaves the system without his review and approval.

Everything runs on the consultant's laptop. No client data leaves the machine.

---

## The Problem It Solves

| Without the Framework | With the Framework |
|---|---|
| Junior writes first draft — 3–5 hours | AI Junior drafts in minutes using live research tools |
| PM reviews, redlines, sends back | AI PM reviews for gaps and citation quality, requests revision automatically |
| Partner checks regulatory alignment manually | AI Partner validates against UAE/GCC authoritative regulatory sources |
| Research done ad hoc, inconsistently | Research is structured, cited, trust-rated, and archived per case |
| Proposal writing takes half a day | 7-section forensic proposal generated in under 5 minutes |
| No audit trail unless manually kept | Every action timestamped and logged automatically — immutable |
| Arabic deliverables require a separate translation step | Arabic version generated automatically when selected |
| Each new case starts from scratch | Case memory persists across sessions; resume from last state at any time |

The business case is capacity expansion. A solo practitioner who produces associate-quality first drafts in hours instead of days can take more cases, respond faster, and maintain margins without headcount.

---

## How Work is Organised

All work is organised into **Projects**. A Project is a client engagement. Each Project can contain one or more **workstreams** — a workstream is one service line run against that client (Investigation Report, FRM Risk Register, Due Diligence, and so on). A Project must have at least one workstream. There is no upper limit.

Two arcs exist in the product:

**Arc 1 — Proposal** is used before the consultant is formally retained. It covers scoping conversations and proposal deck generation. No case files are created. Once the client signs the engagement letter, the consultant creates a Project and Arc 2 begins.

**Arc 2 — Engagement** is the main working environment. The consultant creates a Project, runs the relevant workstreams, and assembles the final client document from the outputs. All workstream outputs accumulate in the same Project folder.

---

## The Internal Review Hierarchy

Every serious workstream runs through a simulated three-level team:

```
CONSULTANT INPUT
       │
       ▼
┌─────────────────────────────────────────┐
│  JUNIOR ANALYST                         │
│                                         │
│  • Searches UAE/GCC regulatory sites    │
│  • Checks OFAC, UN, EU sanctions lists  │
│  • Looks up company registrations       │
│  • Reads uploaded case documents        │
│  • Produces structured first draft      │
└─────────────────────────────────────────┘
       │
       ▼  (revision loop if PM requests changes)
┌─────────────────────────────────────────┐
│  PROJECT MANAGER                        │
│                                         │
│  • Reviews draft for completeness       │
│  • Checks citation quality and gaps     │
│  • Requests specific revisions or       │
│    approves when standard is met        │
└─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  PARTNER                                │
│                                         │
│  • Validates UAE/GCC regulatory align.  │
│  • Reviews evidence chain (ACFE std.)   │
│  • Always signs off — never blocks      │
│  • Where standards not met: approves    │
│    with explicit section disclaimers    │
│  • Flags escalation requirements        │
└─────────────────────────────────────────┘
       │
       ▼
  FINAL REPORT  →  Project / F_Final /
  final_report.en.docx + final_report.en.md
```

The consultant can accept, override, or reject any agent output at any point. The pipeline records every decision in an immutable audit log.

---

## Service Lines

| Service Line | Review Depth | Output |
|---|---|---|
| **Investigation Report** | Full 3-agent pipeline | Forensic investigation report — 9 types (including AUP and Custom), 4 audience versions |
| **FRM Risk Register** | Full 3-agent pipeline | Risk register — 8 modules, UAE regulatory citations, COSO/ISO 37001/ACFE mapped |
| **Due Diligence** | Assisted single-pass | DD screening memo — individual or entity |
| **Sanctions Screening** | Assisted single-pass | Sanctions screening report — OFAC, UN, EU |
| **Transaction Testing** | Assisted single-pass | Testing plan and findings |
| **Policy / SOP** | Assisted single-pass | Internal compliance policy or procedure |
| **Training Material** | Assisted single-pass | Staff training content |
| **Client Proposal** | Assisted single-pass | 7-section proposal with firm branding and fee structure |
| **Proposal Deck** | Assisted single-pass | Slide-by-slide prompt kit for PowerPoint build |
| **Engagement Scoping** | Assisted single-pass | Scope of work document |
| **Individual Due Diligence - Background checks** | Standalone | CFO / Lawyer / Regulator / Insurer perspective challenge |

**Full pipeline** workstreams include revision loops, evidence chain validation, and partner sign-off. **Assisted** workstreams produce a complete deliverable in one AI pass. Both produce .docx and .md output with full audit trail.

---

## Research Standards

The framework does not allow the AI to make things up. Every factual claim must come from a verified source.

| Research Tool | Sources | Trust Level |
|---|---|---|
| Regulatory Lookup | UAE Central Bank, DFSA, ADGM, SCA, FSRA — official sites only | Authoritative |
| Sanctions Check | OFAC SDN List, UN Security Council, EU Consolidated Sanctions | Authoritative |
| Company Lookup | UAE company registries, official filings | Authoritative |
| Web Search | General web via Tavily | Flagged as unverified |

Final deliverables prefer authoritative sources. General web results always carry an unverified disclaimer. Where authoritative sources cannot be found for a topic, the Partner signs off and appends a specific disclaimer to the affected section — it does not block the delivery. The consultant decides whether to address the gap or proceed with the disclaimer. Blocking sign-off would stall engagements; transparent disclaimers preserve both delivery and professional integrity.

---

## Evidence Standards — ACFE Compliant

Every investigation finding follows the forensic narrative structure:

```
Procedure performed  →  "We reviewed vendor invoices for the period..."
Factual finding      →  "We noted that..."
Implication          →  "This indicated / suggested..."
Conclusion           →  "Based on our review of X, Y, Z, we conclude..."
```

Evidence is classified at intake. Only permissible evidence (accounting records, bank statements, contracts, signed interview notes) can be cited in the report. Lead-only evidence (hearsay, unverified tips) directs the investigation but cannot be cited. Inadmissible evidence (no chain of custody) is blocked entirely.

---

## Document Handling

When the consultant uploads case documents, the system:

1. Extracts text — PDF, Word, Excel, email (.eml, .msg), CSV
2. Builds a hierarchical index — short documents summarised; large documents broken into sections with titles and page references so agents can navigate without re-reading everything
3. Reads sections on demand during drafting — agents request specific parts, never loading the full file into one prompt
4. Analyses Excel — detects duplicate payments, round numbers, split transactions, vendor concentration, timing patterns, sequence gaps, journal entry overrides
5. Parses emails — extracts metadata, body, attachments; links parent emails to child attachments
6. Builds a timeline — extracts dated events from all documents as they are read; referenced automatically during drafting

---

## Output Files

Every workstream produces its own case folder:

```
cases/{case_id}/
  A_Engagement_Management/   intake, state, audit trail
  B_Planning/                research plan, scope notes
  C_Fieldwork/               workpapers, notes
  D_Evidence/                indexed documents, evidence register
  E_Drafts/                  all agent outputs, versioned
  F_Final/                   final_report.en.docx
                             final_report.en.md
                             final_report.ar.md  (when Arabic selected)
```

If a run is interrupted (power cut, network issue, exit), the next run detects the incomplete state and resumes from where it stopped. No work is lost.

---

## Firm Profile — Set Once, Used Everywhere

On first launch, the setup wizard collects:
- Firm name and logo path
- Team member names, roles, and credential bios
- Pricing model (hourly, daily, lump sum, retainer) and rates
- Standard terms and conditions

Stored in `firm_profile/` locally. Loaded automatically into every proposal, report header, and team section. No re-entry per engagement.

---

## Current Build Status

| Component | Status |
|---|---|
| Core framework (schemas, state machine, hooks, orchestrator) | Complete |
| Research tools (regulatory, sanctions, company, web) | Complete |
| Document manager (extraction, indexing, retrieval) | Complete |
| Evidence tools (Excel analyser, email parser, classifier) | Complete |
| Semantic embeddings (document similarity and retrieval) | Complete |
| Agent pipeline (Junior, PM, Partner) | Complete |
| Template manager (.docx GW_ styles) | Complete |
| Activity logger | Complete |
| All service line workflows (11 active) | Complete |
| 4 client personas (CFO, Lawyer, Regulator, Insurer) | Complete |
| Bilingual output (English / Arabic) | Complete |
| Firm profile setup wizard | Complete |
| Streamlit browser UI (18 pages) | Complete — 5-section st.navigation() sidebar |
| Product IA redesign (two-arc model, st.navigation()) | Complete — Sprint-IA-01 merged 2026-04-21 |
| Hybrid intake (structured dropdowns + remarks conversation) | Designed — Sprint-IA-02 |
| Expert Witness workflow | Planned |
| FRM guided exercise redesign | Planned |
| White-label packaging | Planned — Phase 7 |

---

## How It Can Be Sold

The product is designed to be distributed in multiple forms. Two are available today.

**Solo Install — GoodWork Edition:** Maher's own copy, GoodWork branded, pre-configured with GoodWork knowledge and firm profile. Internal use.

**White-Label Solo Install:** The same product stripped of GoodWork branding and repackaged for another solo forensic consultant or small boutique firm. They install it on their own laptop, run the setup wizard with their own firm details, and use it entirely under their own brand. Sold as a one-time licence with optional annual support.

**Coming later:** Co-Work (shared folder for a small team), Enterprise On-Premises (staffed firm with role-based access), and Multi-Tenant SaaS (GoodWork hosts, multiple firms subscribe). Each model builds on the same pipeline — the workflow engine, agents, and research tools are identical across all versions. What changes is who can access the system and how data is stored.

Full details on all shipping models and what each requires architecturally: see `docs/product-packaging.md`.

---

## What It Is Not

- Not a cloud service — runs entirely on the consultant's machine
- Not a generic AI assistant — every workflow is purpose-built for forensic consulting
- Not a replacement for professional judgment — the Partner AI recommends; the consultant decides
- Not connected to WorldCheck or WorldCompliance — licensed database access is not included; this gap is disclosed in all DD and sanctions outputs
- Not an automated filing system — no output is transmitted anywhere without the consultant's action

---

*GoodWork LLC — Confidential. White-label distribution available.*
