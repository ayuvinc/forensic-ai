---
file: knowledge/frm/frm_framework.md
quality_tier: B
last_reviewed: 2026-04-07
reviewer: session-011
open_claims: 0
---

<!-- Sources: knowledge/frm/sources.md — see that file for full URLs -->
<!-- Claim labels: [LAW] [BEST_PRACTICE] [PRODUCT_RULE] [ADVISORY] — see docs/lld/knowledge-quality-standard.md -->

# FRM Framework Knowledge Base

## What is FRM?

Fraud Risk Management (FRM) is not just a risk register. It spans up to **8 modules** and can range from a basic register snapshot to a full multi-phase engagement. Each module can be delivered standalone or in combination.

---

## The 8 FRM Modules

| # | Module | Description |
|---|--------|-------------|
| 1 | Fraud Risk Governance & Policy | Framework, policies, roles, oversight |
| 2 | Fraud Risk Assessment (Risk Register) | Identifying and assessing fraud risks specific to the organization |
| 3 | Control Design | Preventive and detective controls to mitigate identified risks |
| 4 | Investigation Protocols & Procedures | Formal investigation procedures and response protocols |
| 5 | Whistleblower Hotline Setup | Anonymous reporting mechanisms |
| 6 | Employee Training & Awareness | Staff education on fraud risks and reporting |
| 7 | Monitoring & Data Analytics | Continuous monitoring and analytical procedures |
| 8 | Insurance Coverage Recommendations | Fraud and crime insurance assessment |

**Module dependencies:** Control Design (Module 3) requires a completed Risk Register (Module 2).

---

## FRM Risk Register — Detailed

### Who uses it
Management, Board, or Audit Committee wanting to understand their fraud exposure.

### Output structure
- Executive summary
- Risk universe table: Risk | Category | Likelihood | Impact | Rating | Regulatory ref
- Per-risk detail: description, red flags, existing controls, gaps, recommendations
- Regulatory mapping appendix

### Risk rating methodology
Can come from the client (their own 1–5 scale, RAG, etc.) or standardized. The register should include an owner column (who in the client org is responsible for each risk). Recommendations can map to specific control frameworks (COSO, ISO 37001).

---

## Three-Layer Knowledge Architecture

### Layer 1 — Core Framework Knowledge (static, ships with tool)
- FRM frameworks: ACFE/COSO structure
- UAE regulatory context: CBUAE Chapter 11, DFSA AML requirements
- Module definitions and regulatory requirements by industry/jurisdiction
- Never re-searched from scratch

### Layer 2 — Accumulated Knowledge (grows over time)
- As cases complete, patterns, lessons, common findings, regulatory updates get written back
- Industry-specific fraud typologies accumulate
- Tool becomes smarter with use

### Layer 3 — Case-Specific Knowledge (per case)
- Research memory lives at the case level
- Research from Module 2 (Risk Assessment) is shared with Module 3 (Control Design)
- Prevents duplication across modules in the same engagement

---

## Research Memory Split

### Always from the client (uploaded/pasted)
- Existing risk registers, policies, SOPs
- Org charts, process maps
- Interview transcripts, minutes of meetings
- Transaction data, evidence files
- Previous audit or assessment reports

### Always researched from internet (Consultant fetches)
- Industry fraud typologies for the sector (e.g. construction fraud patterns in UAE)
- Applicable UAE regulations for their industry + regulator
- Sanctions screening on named entities
- Benchmarks — what does a company of this size/industry typically have in place

### Depends / grey area
- Company ownership and structure — client may provide, or Consultant looks it up
- Competitor incidents — internet only if client wants benchmarking
- Control frameworks (COSO, ACFE, ISO 37001) — reference material, fetched once and reused

---

## Case Scope Determination Flow

```
Consultant: What is the client's name and industry?
> Al Noor Construction LLC, real estate and construction, Dubai

Consultant: Do you have any existing FRM documents for this client?
           (policies, previous risk assessments, SOPs)
> Yes — uploading their AML policy and procurement SOP

Consultant: What is the scope of this engagement?
           1. Risk Register only
           2. Select modules (I'll show you the list)
           3. Full FRM program
           4. Proposal only — scope and price the engagement
> 2

Consultant: Here are the 8 FRM modules. Which do you need?
           [1] Governance & Policy
           [2] Risk Assessment / Risk Register  (required if no existing register)
           [3] Control Design
           [4] Investigation Protocols
           [5] Hotline Setup
           [6] Training & Awareness
           [7] Monitoring & Analytics
           [8] Insurance Recommendations
> 2, 3, 6

Consultant: Module 3 (Control Design) requires a completed Risk Register.
           You selected Module 2, so I'll build the register first.
           For Module 6 (Training), do you want role-specific modules
           or a single all-staff program?
> role-specific for finance and procurement teams only
```

---

## UAE Regulatory Context

| Regulator | Full Name | Scope |
|-----------|-----------|-------|
| CBUAE | Central Bank of UAE | Chapter 11 AML — all licensed financial institutions |
| DFSA | Dubai Financial Services Authority | DIFC-licensed firms |
| ADGM | Abu Dhabi Global Market | ADGM-licensed firms (FSRA) |
| SCA | Securities and Commodities Authority | Capital markets, listed companies |

---

## Control Frameworks Referenced

- **COSO** — Committee of Sponsoring Organizations (internal control & ERM)
- **ACFE** — Association of Certified Fraud Examiners (fraud risk standards)
- **ISO 37001** — Anti-bribery management systems

---

## Modular Architecture Design Principles

- Each FRM module is an independent skill with its own schema, hooks, agent prompt, and output
- A shared **research memory** lives at the case level
- The Consultant dynamically selects and sequences modules based on client needs
- Same case can run in multiple sessions, picking up where it left off
- Works both ways: build FRM from scratch OR pick up from existing client documents
