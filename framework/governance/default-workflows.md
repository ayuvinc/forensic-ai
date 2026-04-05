# Default Workflows — AK Cognitive OS v3.0
# Standard execution paths per project type
# Owner: Architect
# Depends on: framework/governance/delivery-lifecycle.md, framework/governance/stage-gates.md

---

## Overview

This document defines the standard stage configuration for four common project types. For each workflow, the stage map shows which lifecycle stages are required, optional, or skipped; which gate type applies at each stage transition; and the recommended operating tier.

Stage names match `framework/governance/delivery-lifecycle.md` exactly.
Gate names (Pre-Implementation Gate, Pre-Release Gate, Pre-Closeout Gate) match `framework/governance/stage-gates.md` exactly.

**Column definitions:**
- **Stage Status** — `required` / `optional` / `skip`
- **Gate Type** — `hard` (blocking) / `soft` (advisory) / `none` (no gate)
- **Recommended Tier** — the operating tier for this workflow type (same for all rows in a given table)

---

## Workflow 1 — Greenfield SaaS

A net-new software product built from scratch with a user-facing interface and external users. Standard tier applies.

| Stage | Stage Status | Gate Type | Recommended Tier |
|---|---|---|---|
| intake | required | hard | Standard |
| discovery | required | hard | Standard |
| scope | required | hard | Standard |
| architecture | required | hard | Standard |
| design | required | hard | Standard |
| implementation | required | hard | Standard |
| QA | required | hard | Standard |
| security/compliance | required | soft | Standard |
| release | required | hard | Standard |
| lessons | required | soft | Standard |
| framework improvement | optional | none | Standard |

**Notes:**
- All three mandatory gates (Pre-Implementation, Pre-Release, Pre-Closeout) are active.
- `security/compliance` gate is soft — unresolved findings generate warnings; HIGH findings escalate to HARD.
- `design` stage is required because Greenfield SaaS always has a user interface.
- `framework improvement` is optional — only triggered if `framework-improvements.md` has entries.

---

## Workflow 2 — AI/RAG Project

An AI-augmented or retrieval-augmented generation system. Discovery and security are elevated due to data dependency and model trust boundaries. Standard tier applies.

| Stage | Stage Status | Gate Type | Recommended Tier |
|---|---|---|---|
| intake | required | hard | Standard |
| discovery | required | hard | Standard |
| scope | required | hard | Standard |
| architecture | required | hard | Standard |
| design | optional | soft | Standard |
| implementation | required | hard | Standard |
| QA | required | hard | Standard |
| security/compliance | required | hard | Standard |
| release | required | hard | Standard |
| lessons | required | soft | Standard |
| framework improvement | optional | none | Standard |

**Notes:**
- All three mandatory gates (Pre-Implementation, Pre-Release, Pre-Closeout) are active.
- `security/compliance` gate is **hard** (not soft) — AI/RAG projects carry data privacy risk by default; a security sweep is a blocking requirement before release.
- `design` stage is optional — many AI/RAG projects are API-only; activate if a user interface is in scope.
- `discovery` gate is hard — data source mapping, model selection, and retrieval strategy must be documented before architecture begins.

---

## Workflow 3 — Regulated App

A project operating under regulatory obligations (HIPAA, pharma GxP, fintech compliance, GDPR-sensitive processing). All stages required. High-Risk tier applies.

| Stage | Stage Status | Gate Type | Recommended Tier |
|---|---|---|---|
| intake | required | hard | High-Risk |
| discovery | required | hard | High-Risk |
| scope | required | hard | High-Risk |
| architecture | required | hard | High-Risk |
| design | required | hard | High-Risk |
| implementation | required | hard | High-Risk |
| QA | required | hard | High-Risk |
| security/compliance | required | hard | High-Risk |
| release | required | hard | High-Risk |
| lessons | required | hard | High-Risk |
| framework improvement | required | soft | High-Risk |

**Notes:**
- All three mandatory gates (Pre-Implementation, Pre-Release, Pre-Closeout) are active and strictly hard.
- No stage may be skipped or marked optional without an explicit AK approval and a decision-log entry.
- `security/compliance` gate is hard at all severity levels — S1 findings require AK decision before proceeding.
- `lessons` gate is hard — regulated projects must produce a documented retrospective before session close.
- `framework improvement` stage is required because regulatory findings often surface framework policy gaps.

---

## Workflow 4 — Internal Tool

An internal-facing tool, script, or automation with no external users and low regulatory exposure. MVP tier applies.

| Stage | Stage Status | Gate Type | Recommended Tier |
|---|---|---|---|
| intake | required | hard | MVP |
| discovery | optional | none | MVP |
| scope | required | soft | MVP |
| architecture | required | soft | MVP |
| design | skip | none | MVP |
| implementation | required | hard | MVP |
| QA | required | soft | MVP |
| security/compliance | optional | none | MVP |
| release | required | soft | MVP |
| lessons | optional | none | MVP |
| framework improvement | skip | none | MVP |

**Notes:**
- Pre-Implementation Gate is active but reduced — only `docs/problem-definition.md` and basic task breakdown are required; `scope-brief.md` and `hld.md` are recommended, not mandatory.
- Pre-Release Gate is active but reduced — Codex review and QA_APPROVED are required; security sweep is optional.
- Pre-Closeout Gate is fully active — SESSION STATE and BOUNDARY_FLAG checks always apply regardless of tier.
- `design` stage is skipped — internal tools do not require UX specs or design system.
- `security/compliance` stage is optional — activate if the tool handles PII, PHI, or credentials.
- `framework improvement` stage is skipped — framework changes require Standard or High-Risk tier context.

---

## Tier Summary

| Workflow Type | Recommended Tier | Security/Compliance Gate |
|---|---|---|
| Greenfield SaaS | Standard | soft (escalates to hard on HIGH) |
| AI/RAG Project | Standard | hard |
| Regulated App | High-Risk | hard |
| Internal Tool | MVP | optional |

---

*See `framework/governance/delivery-lifecycle.md` for full stage definitions.*
*See `framework/governance/stage-gates.md` for gate enforcement details.*
*See `framework/governance/operating-tiers.md` for tier gate requirements (STEP-32 — pending).*
