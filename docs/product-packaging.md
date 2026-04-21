---
Status: active
Source: user-confirmed
Last confirmed with user: 2026-04-21
Owner: Architect
Open questions: 0
---

# Product Packaging — Shipping Models

## Overview

GoodWork Forensic AI is designed as a portable, private forensic workbench. The core architecture is local-first: no cloud dependency, no mandatory authentication, no shared infrastructure. This makes it easy to ship to individual practitioners but requires deliberate architectural work before it can serve teams or multiple firms.

**Currently shipping:** Models 1 and 2.
**Designed but not built:** Models 3–5.
**Speculative:** Model 6.

---

## Model 1 — Solo Install (GoodWork Edition)

**What it is:** The product as built. GoodWork LLC branding, Maher's firm profile, GoodWork knowledge base pre-loaded.

**Target buyer:** Maher Hashash / GoodWork LLC — internal use.

**What the user gets:**
- Full product: all 11+ service line workflows, Streamlit browser UI, CLI fallback
- GoodWork firm profile and credentials pre-configured
- GoodWork knowledge base (FRM, Investigation, DD, Sanctions, TT frameworks)
- Local data storage — nothing leaves the machine

**Commercial model:** Internal use only. Not sold.

**Architecture readiness:** Complete. Ships today.

**What needs to be built:** Nothing for this model.

---

## Model 2 — White-Label Solo Install

**What it is:** The same product, stripped of GoodWork branding and knowledge, repackaged for a different solo forensic consultant or boutique firm. The buyer installs it on their own laptop and configures it with their own firm identity.

**Target buyer:** Solo forensic consultants or small (1–3 person) boutique firms in UAE/GCC/India who want the same capacity multiplication that GoodWork gets, under their own brand.

**What the user gets:**
- Full product: all service line workflows, Streamlit UI, CLI fallback
- Blank firm profile — setup wizard collects their firm name, logo, credentials, pricing, T&C at first launch
- Blank knowledge base — they can populate it with their own domain research
- Local data storage — their client data never leaves their machine
- GoodWork branding completely absent from all outputs

**Commercial model:**
- One-time licence fee (software purchase) — buyer owns their install
- Optional: annual support/update subscription
- Optional: knowledge base customisation service (GoodWork populates the knowledge files for their jurisdiction/industry)

**Architecture readiness:** Core platform complete. Packaging script (Phase 7) in progress.

**What needs to be built:**
- `scripts/create_blank_instance.py` — strips GoodWork knowledge content, resets firm_profile/, resets instance_config/firm.json, outputs distributable zip
- `instance_config/firm.json` — per-instance configuration file (firm_name, firm_type, primary_jurisdiction, enabled_workflows)
- `INSTANCE_GUIDE.md` — 6-step onboarding for the buyer
- Replace all hardcoded "GoodWork" strings with `config.FIRM_NAME` (4 locations identified)

**Delta from Model 1:** Content only — no architecture change. Same code, different firm profile and knowledge base.

---

## Model 3 — Co-Work Install (2–5 consultants, same firm)

**What it is:** A shared install used by a small team working on the same engagements. Two to five consultants in the same firm can access the same project folder, run workstreams, and see each other's outputs. All work is still done on-premises — no cloud required.

**Target buyer:** A boutique forensic firm that has grown beyond one person but is not ready to pay for full enterprise infrastructure. The team may share a network drive or a synced folder (OneDrive, Dropbox, internal server share).

**What the user gets:**
- All Model 2 capabilities
- Multiple named users — each session records who did what
- Shared project folder — all consultants see the same engagements and outputs
- Per-user audit trail — the audit log identifies the acting user on every event
- Lightweight access control — Admin (configures firm profile), Partner (can sign off), Consultant (can run and draft), Viewer (read-only)

**Commercial model:**
- Per-seat licence (e.g. base fee + per-additional-user fee)
- Shared folder setup requires buyer's own infrastructure (network share, OneDrive, etc.) — not provided

**Architecture readiness:** Not built. Moderate architectural changes required.

**What needs to be built:**
- User identity in session — current sessions have no user concept; every action is anonymous
- Audit trail user field — `audit_log.jsonl` events need a `user_id` field
- State file locking — `state.json` has no write lock; concurrent writes from two users corrupt it; needs file-level advisory locking or write-queue pattern
- Firm profile access control — currently any user can overwrite firm_profile/; needs Admin-only write gate
- Lightweight auth — username + PIN or passphrase at session start; no external auth provider required
- Shared project index — currently each user's projects are discovered by scanning cases/; needs a shared projects/index.json visible to all users

**Delta from Model 2:** Session user identity, audit trail user field, state file locking, lightweight auth, shared project index. No cloud infrastructure required — designed to run on a shared network folder.

---

## Model 4 — Enterprise On-Premises (staffed firm, role-based access)

**What it is:** A full deployment for a forensic practice with a structured team — juniors, seniors, managers, partners, and an IT admin. Runs on the firm's internal server. Each person has a login. Role determines what they can see and do.

**Target buyer:** A mid-size forensic consulting firm (10–50 staff) that handles multiple client engagements simultaneously across a team and needs centralised case management, role-appropriate access, and firm-wide audit visibility.

**What the user gets:**
- All Model 3 capabilities
- Full RBAC (Role-Based Access Control): Admin, Partner, Senior Consultant, Consultant, Viewer
- Partners can see and approve all active engagements
- Juniors only see their assigned engagements
- Central case repository on the firm's internal server
- Firm-wide audit dashboard
- Admin panel: user management, firm profile, knowledge base, API key management

**Commercial model:**
- Annual enterprise licence (site licence or per-seat)
- Optional: professional services for server setup, knowledge base population, onboarding

**Architecture readiness:** Not built. Significant architectural changes required.

**What needs to be built:**
- Authentication system — proper login with hashed passwords, session tokens; can use internal LDAP/AD or standalone auth
- RBAC — role definitions, permission enforcement on every route and action
- Central data store — move from per-user local filesystem to shared server path or lightweight DB (SQLite → PostgreSQL depending on scale)
- Server deployment — Streamlit bound to internal network, not localhost; reverse proxy (nginx) for access control
- Admin panel — user management, role assignment, firm profile management
- Per-role UI adaptation — juniors see a subset of pages; partners see approval queue
- Concurrent access handling — all Model 3 locking requirements, at higher scale

**Delta from Model 3:** Auth system, RBAC, server deployment, admin panel, central data store. This is a meaningful re-architecture of the data and access layers. The workflow and agent pipeline are unchanged.

---

## Model 5 — Multi-Tenant SaaS (GoodWork hosts, multiple firm subscribers)

**What it is:** GoodWork operates a hosted version of the platform. Multiple forensic firms subscribe and access it through a browser. Each firm is a separate tenant — their data, firm profile, and knowledge base are completely isolated from every other tenant.

**Target buyer:** Solo practitioners or small firms who do not want to manage their own installation. Pay monthly, log in from a browser, get all the capabilities.

**What the buyer gets:**
- All product capabilities via browser (no installation required)
- Their own tenant: isolated firm profile, knowledge base, case data
- Managed infrastructure — GoodWork handles updates, backups, availability
- Usage-based billing that covers underlying API costs (Anthropic, Tavily)

**Commercial model:**
- Monthly subscription per firm (not per user — small firm model)
- Tiered: Starter (1 user, limited workflows), Professional (3 users, all workflows), Firm (5+ users, white-label output option)
- GoodWork absorbs API costs and prices them into the subscription

**Architecture readiness:** Not built. Requires substantial re-architecture. The current local-first, flat-file design must be replaced at the data and infrastructure layers.

**What needs to be built:**
- Cloud infrastructure — hosting platform (AWS/GCP/Azure or managed Streamlit hosting)
- Tenant isolation — every data object (cases, firm_profile, knowledge base, audit logs) scoped to a tenant_id
- Cloud storage — replace local filesystem with cloud object storage (S3/GCS) per tenant
- Authentication — proper multi-user auth with email/password, MFA, password reset
- Billing integration — subscription management, usage metering, payment processing
- API key management — pooled Anthropic/Tavily keys with per-tenant cost tracking, or per-tenant keys
- Data backup and recovery — automated backups per tenant
- Availability and scaling — the local-install assumption of one user at a time breaks; needs async job queuing for pipeline runs
- Admin and support tooling — GoodWork needs to manage tenants, handle support tickets, process refunds

**Delta from Model 4:** Cloud infrastructure, tenant data isolation at storage layer, billing, SaaS operations. This is effectively a new product built on top of the same workflow and agent logic. The pipeline, agents, hooks, and workflows are reusable. Everything around them must be rebuilt.

**Important:** Shipping Model 5 requires answering a regulatory question — if client data flows through GoodWork's cloud infrastructure, there are data residency, confidentiality, and professional standards implications. Some forensic clients will not permit their matter data to sit on a third-party server. This must be addressed in the commercial terms before launch.

---

## Model 6 — Managed Service (Maher processes cases for clients via a portal)

**What it is:** Maher runs a single hosted instance. His clients submit matters through a portal, Maher processes them using the tool, and returns the deliverables. The client never touches the software — they interact through a submission/delivery interface.

**Target buyer:** Maher's clients who want a tech-enabled forensic service without managing the tool themselves. GoodWork as a tech-enabled boutique.

**Architecture note:** This is a lightweight variant of Model 5 with one tenant (GoodWork) and multiple client-facing submission slots. Requires a client portal (matter submission, status tracking, deliverable download) layered on top of the existing product.

**Commercial model:** Maher charges per engagement as he does today — the tech is invisible to the client. The portal improves client experience, not the pricing model.

**Architecture readiness:** Not designed. Lower complexity than Model 5 — no multi-tenancy, just a client-facing submission layer on top of the existing single-tenant product.

**Verdict:** Worth designing when Maher wants to scale intake, not before.

---

## Decision Summary

| Model | Ships When | Architecture Change | Commercial Model |
|---|---|---|---|
| 1 — Solo GoodWork Edition | Now | None | Internal use |
| 2 — White-Label Solo | Phase 7 complete | Content only (no code change) | One-time licence |
| 3 — Co-Work | Future sprint | Moderate (auth, locking, user identity) | Per-seat licence |
| 4 — Enterprise On-Premises | Future sprint | Significant (RBAC, server, central store) | Annual enterprise licence |
| 5 — Multi-Tenant SaaS | Separate product track | Major (cloud, tenant isolation, billing) | Monthly subscription |
| 6 — Managed Service | When intake scale requires | Low-moderate (client portal only) | Per-engagement (existing) |

---

## Architecture Principle Across All Models

The workflow engine, agent pipeline, hooks, schemas, and research tools are **model-agnostic**. They do not change between shipping models. What changes is the layer around them: who can access the system, how data is stored, and how it is delivered.

This means any investment in the pipeline — new service lines, better prompts, improved research tools — applies to every shipping model without rework. The commercial value of the pipeline compounds across all models.
