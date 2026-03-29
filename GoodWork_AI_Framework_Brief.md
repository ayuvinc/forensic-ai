# GoodWork AI Forensic Framework
## Executive Brief for Maher — Managing Director, GoodWork LLC

---

## What We Are Building

A private, local AI system that runs the internal operations of a forensic consulting firm — from first client conversation to signed deliverable.

It is not a chatbot. It is not a document template tool.

It is a **role-simulated forensic workbench** that mirrors how a real forensic team operates:
a Junior Analyst researches and drafts, a Project Manager reviews and challenges,
a Partner signs off — all governed by ACFE standards, UAE regulatory requirements,
and a full audit trail.

Everything runs on your laptop. No client data leaves your machine.

---

## The Problem It Solves

| Today (manual) | With the Framework |
|----------------|-------------------|
| Junior writes first draft — hours to days | AI Junior drafts in minutes using research tools |
| PM reviews, redlines, sends back | AI PM reviews, flags issues, requests revision automatically |
| Partner checks regulatory alignment manually | AI Partner validates against UAE/GCC regulatory sources |
| Research done ad-hoc, inconsistently | Research is structured, cited, and archived per case |
| Proposal writing takes half a day | 7-section forensic proposal generated in under 5 minutes |
| No audit trail unless manually kept | Every action timestamped and logged automatically |
| Arabic deliverables require separate translation step | Arabic version generated automatically when selected |

---

## What It Produces

| Menu Option | What You Get |
|-------------|-------------|
| **FRM Risk Register** | Full Fraud Risk Management Register — 8 modules, risk-rated table, regulatory citations, mapped to COSO / ISO 37001 / ACFE |
| **Investigation Report** | Forensic investigation report — 7 investigation types, 4 audiences (management / board / legal / regulatory), expert witness standard when needed |
| **Client Proposal** | 7-section proposal with your firm's branding, team credentials, and fee structure |
| **PPT Prompt Pack** | Slide-by-slide prompt kit to build the proposal deck in Claude Projects |
| **Policy / SOP Generator** | Internal compliance policy or procedure document, jurisdiction-aware |
| **Training Material** | Staff training content from a case or compliance topic |
| **Persona Review** | How a CFO / Lawyer / UAE Regulator / Insurance Adjuster would challenge your report |
| **Case Tracker** | Live status of all open and completed cases |

---

## How It Works — The Internal Hierarchy

Every serious workflow (Investigation, FRM Risk Register) runs through a three-level internal team:

```
CONSULTANT INPUT
       │
       ▼
┌─────────────────────────────────────┐
│  JUNIOR ANALYST  (Claude Haiku)     │
│                                     │
│  • Searches regulatory databases    │
│  • Checks sanctions lists           │
│  • Looks up company registrations   │
│  • Reads uploaded case documents    │
│  • Produces structured first draft  │
└─────────────────────────────────────┘
       │
       ▼ (revision loop if needed)
┌─────────────────────────────────────┐
│  PROJECT MANAGER  (Claude Sonnet)   │
│                                     │
│  • Reviews draft for completeness   │
│  • Checks citation quality          │
│  • Requests revision if issues found│
│  • Approves when standard is met    │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  PARTNER  (Claude Opus)             │
│                                     │
│  • Validates regulatory alignment   │
│  • Checks evidence permissibility   │
│    (ACFE standard)                  │
│  • Signs off on final deliverable   │
│  • Flags escalation if needed       │
└─────────────────────────────────────┘
       │
       ▼
  FINAL REPORT  →  cases/{case_id}/
```

The system knows which Claude model to use for each role based on the budget mode you set:
- **Economy** — Haiku for junior work, Sonnet for partner sign-off
- **Balanced** — Haiku for research, Sonnet for reviews and sign-off
- **Premium** — Sonnet for all research, Opus for partner (FRM and expert witness always use Opus)

---

## Research — Where the AI Looks

The AI does not make things up. Every factual claim must come from a verified source.

| Research Tool | What It Searches | Trust Level |
|---------------|-----------------|-------------|
| Regulatory Lookup | UAE Central Bank, DFSA, ADGM, SCA, FSRA — official sites only | Authoritative |
| Sanctions Check | OFAC SDN List, UN Security Council, EU Sanctions | Authoritative |
| Company Lookup | UAE company registries, official filings | Authoritative |
| Web Search | General web via Tavily | General — flagged as unverified |

Deliverables may only cite authoritative sources. General web results that cannot be verified carry an automatic disclaimer.

---

## Evidence Standards — ACFE Compliant

Every finding follows the forensic narrative structure:

```
Procedure performed  →  "We reviewed vendor invoices for period X to Y..."
Factual finding      →  "We noted that..."
Implication          →  "This indicated / led us to..."
Conclusion           →  "Based on our review of X, Y, Z, we conclude..."
```

Evidence is classified at intake:

| Classification | Examples | Can cite in report? |
|----------------|----------|---------------------|
| Permissible | Accounting records, bank statements, contracts, signed interview notes | Yes |
| Lead-only | Hearsay, tips, unverified allegations | No — used only to locate permissible evidence |
| Inadmissible | No chain of custody, not from documented procedures | Never |

---

## Memory — How It Gets Smarter Over Time

The framework builds knowledge at three levels:

**Level 1 — Static knowledge base** (in `knowledge/`)
Pre-loaded research on FRM methodology, investigation frameworks, UAE regulatory sources.
This is written once and improves between sessions.

**Level 2 — Case-level memory** (in `cases/{id}/`)
Every case builds its own file: intake, research, drafts, audit log, citations index.
When a case is resumed, the system reloads exactly where it left off.

**Level 3 — Cross-module research memory** (FRM only)
As the FRM pipeline runs each module, completed research is passed forward.
Module 3 (Procurement Risk) already knows what Module 2 (AML Risk) found — no re-research,
no repetition.

---

## Document Handling — How It Reads Your Files

When a consultant uploads case documents, the system:

1. **Extracts text** — PDF, Word, Excel, email (.eml, .msg), CSV
2. **Builds an index** — small documents summarised; large documents broken into sections with titles and page references
3. **Reads on demand** — AI agents request specific sections when drafting, never loading the full file into a single prompt
4. **Analyses Excel** — detects duplicate payments, round numbers, split transactions, vendor concentration, timing patterns, sequence gaps, journal overrides
5. **Parses emails** — extracts metadata, body, attachments; links parent emails to child attachments
6. **Builds timeline** — extracts dated events from all documents automatically as cases are read

---

## What It Produces — Deliverable Files

Every case gets its own folder:

```
cases/20260329-A1B2C3/
  intake.json               ← client and engagement details
  state.json                ← current pipeline status
  audit_log.jsonl           ← every action, timestamped, immutable
  citations_index.json      ← all research sources cited
  junior_output.v1.json     ← junior draft (versioned)
  pm_review.v1.json         ← PM review notes
  partner_approval.v1.json  ← partner sign-off decision
  final_report.en.md        ← English deliverable
  final_report.ar.md        ← Arabic deliverable (when selected)
```

If anything interrupts mid-run (power cut, network issue, user exits), the next run detects
the unfinished state and resumes from exactly where it stopped.

---

## Your Firm Profile — Set Once, Used Everywhere

On first launch, the system collects:

- Firm name and logo path
- Team member names, roles, and bios
- Pricing model (hourly / daily / lump sum / retainer) and rates
- Standard terms and conditions

This is stored locally in `firm_profile/` and loaded automatically into every proposal,
report header, and team section — no re-entering the same information.

---

## Current Status

| Layer | Status |
|-------|--------|
| Core framework (schemas, state machine, hooks, orchestrator) | Complete, QA-verified |
| Research tools (regulatory, sanctions, company, web) | Complete |
| Document manager (extraction, indexing, bounded retrieval) | Complete |
| Evidence tools (Excel analyser, email parser, classifier) | Complete |
| Agent pipeline (Junior, PM, Partner) | Complete |
| All 10 workflows | Complete |
| 4 client personas (CFO, Lawyer, Regulator, Insurance Adjuster) | Complete |
| Bilingual output (EN / Arabic) | Complete |
| Firm profile setup wizard | Complete |
| End-to-end smoke test | Pending — requires API keys |

The system is ready to run. Once API keys are configured (`ANTHROPIC_API_KEY` and `TAVILY_API_KEY`),
`python run.py` launches the full 10-option menu.

---

## What It Is Not

- Not a cloud service — runs entirely on your machine
- Not a generic AI assistant — every workflow is purpose-built for forensic consulting
- Not a replacement for professional judgment — the Partner AI recommends, the consultant decides
- Not connected to the internet except for research tool calls (Tavily, regulatory sites)

---

*Built for GoodWork LLC — Confidential*
