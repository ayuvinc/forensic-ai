# BA Logic — GoodWork Forensic AI

_Populated via /ba discovery session — 2026-04-04_

---

## Business Logic Decisions

[2026-04-04] Decision: Tool is a writing and organization aid, not an investigator.
Rationale: Maher provides facts, evidence, and analytical conclusions. The tool structures, drafts, and standardizes — it does not reach conclusions independently. Any output that presents a "finding" is structured from Maher's input, not generated as independent analysis.

[2026-04-04] Decision: Sole practitioner model — all roles collapse to one user.
Rationale: Maher IS the junior analyst, project manager, and partner. The multi-agent pipeline simulates the review hierarchy a staffed firm would have. Maher can accept, override, or ignore any agent review output.

[2026-04-04] Decision: Multi-session case work is the primary usage pattern.
Rationale: Cases run 3–8 weeks. Maher works on a case across multiple days and sessions. State must persist reliably. Resume-from-last-state is not a nice-to-have — it is required for the tool to be usable on real engagements.

[2026-04-04] Decision: CXO is the default audience for all deliverables.
Rationale: GoodWork's clients are CXOs. All language, structure, and framing defaults to executive-appropriate. Technical or regulatory depth is present but subordinated to clarity and executive relevance.

[2026-04-04] Decision: No output is client-facing without Maher's review.
Rationale: Tool produces drafts. Maher reviews, edits, and approves before anything goes to a client. The tool does not send emails, submit filings, or publish anything.

[2026-04-04] Decision: Intake questions vary by case type.
Rationale: Investigation intake is different from FRM intake, which is different from proposal intake. Each workflow has its own guided intake conversation. There is no universal intake form.

[2026-04-04] Decision: Value = time saved on grunt work, money saved vs. hiring associates.
Rationale: The business case is not quality improvement alone — it is capacity expansion. A solo practitioner who can produce associate-quality first drafts in hours rather than days can take more cases, respond faster, and keep margins without headcount.

---

## Acceptance Rules

_What must be true for a feature to be considered done._

- Guided intake: produces a Pydantic-validated CaseIntake object from a conversation — no form fields presented to user
- Investigation report: Junior draft → PM review → Partner sign-off → final_report.en.md written to cases/{id}/
- FRM Risk Register: all 8 modules run (within scope); module dependency rules enforced; final_report.en.md written
- Policy/SOP, Training, Proposal: single-pass draft written to cases/{id}/ with audit event recorded
- Resume: if state.json is non-terminal, orchestrator detects and offers resume on next run — no data loss
- Evidence tracking: every document registered via document_manager has a retrievable index entry; model can re-read on demand
- All deliverables: language calibrated for CXO audience; no raw regulatory citations without plain-English explanation
- Audit trail: every agent run, review decision, and state transition appended to audit_log.jsonl
- No client-facing output generated without a human-readable review step in the pipeline

---

## Data Rules

- All case data stored locally in `cases/{case_id}/` — never transmitted without Maher's action
- `audit_log.jsonl` is append-only — no entry is modified or deleted after write
- Artifact writes are atomic: `.tmp` → `os.replace()` — no partial writes
- `state.json` reflects the current pipeline status of the case at all times
- `firm_profile/` stores Maher's firm credentials, pricing, and T&C — loaded at proposal time, not re-entered
- Evidence documents registered in `document_manager` are indexed with bounded retrieval — model reads sections on demand, not the whole document on every call
- Final deliverables: `final_report.en.md` always generated; `final_report.ar.md` generated when language = ar at intake
- Case IDs follow format `{YYYYMMDD}-{6-char alphanumeric}` (e.g. `20260101-A3B4C5`) — generated at intake via uuid4 truncated to 6 chars uppercased

---

## Edge Cases

[2026-04-04] Session interrupted mid-pipeline:
→ state.json holds last valid status; orchestrator detects non-terminal state on next run; offers resume; loads last persisted artifact as starting point. No data loss expected if artifact writes were atomic.

[2026-04-04] Maher disagrees with agent review output:
→ He can override any PM or Partner finding. Approval decisions are his to make. The pipeline records his override in the audit log but does not block on it.

[2026-04-04] Case involves jurisdictions outside UAE:
→ Regulatory mapping is dynamic. Model identifies applicable regulators from client's operating jurisdictions at intake — not hardcoded to UAE. If no authoritative source found for a jurisdiction, disclaimer added to deliverable.

[2026-04-04] Client documents not yet uploaded at intake:
→ Model prompts for documents after intake; Maher can upload later. Case stays at INTAKE_CREATED until documents are available and Maher triggers the pipeline.

[2026-04-04] Firm profile not set up (first run):
→ Setup wizard runs before first menu; collects firm name, team bios, pricing model, T&C. Stored in `firm_profile/`. If skipped, proposal fee section generates with blank rates — pricing completeness check warns Maher before drafting begins (PGP-01).

---

## Open Decisions

[2026-04-04] Should client_proposal be upgraded to full pipeline (Junior → PM → Partner) or remain Mode B (single-pass)?
→ Proposal is the highest-value commercial deliverable. Mode B is faster but has no review layer. Decision pending — see C-01b in tasks/todo.md.

[2026-04-04] What state should Mode B workflows write to state.json on completion?
→ RESOLVED Session 007 (2026-04-04): DELIVERABLE_WRITTEN added to CaseStatus enum and TERMINAL_STATUSES.
  _mark_deliverable_written() called in run.py after choices 4,5,7,8 complete.
  case_tracker renders DELIVERABLE_WRITTEN as green (terminal). See C-02a in tasks/todo.md.

---

## Session 010 Decisions — 2026-04-06

---

### BA-002 — FRM Guided Exercise Step Flow
- Status: CONFIRMED
- Scope: FRM Risk Register workflow redesign — Phase 13 (FRM-R-01 through FRM-R-08)

**User outcome:** Maher co-creates the risk register through a structured conversation instead of reviewing a one-shot AI generation. Output reflects client-specific context, not generic regulatory boilerplate.

**Business rules:**
  - Step 1: Model presents scope plan — modules in scope, sub-areas to cover. Maher confirms before any risk items are generated.
  - Step 2: Per module, per risk sub-area — model presents the sub-area and asks if it applies to this client (Y/N/Partial).
  - Step 3: Per applicable sub-area — model asks 4 structured questions: known incidents? existing controls? probability (1–5)? impact (1–5)?
  - Step 4: Model generates ONE risk item at a time from Maher's answers + regulatory baseline. Model leads with recommendations on ALL parameters: risk title, risk scenario, impact rating, probability rating, residual risk. Maher accepts or adjusts each — model does not wait for Maher to draft the item.
  - Step 5: Maher reviews each item — Approve / Edit / Skip. Edit triggers a structured model conversation (not a text-box); model asks follow-up questions and re-recommends revised parameters. One revision cycle per item.
  - Step 6: Register assembled from approved items only. Skipped items not included.
  - BASELINE flag: items pre-filled from industry knowledge in zero-info mode are labelled BASELINE (unverified) in state.json and audit_log. Maher's approval removes the flag from the deliverable — item becomes confirmed, indistinguishable from consultant-input items in final_report.
  - Audit trail: each item's provenance (consultant-input vs BASELINE vs FROM_SIMILAR_ENGAGEMENT) stored in state.json, never surfaced to client.

**Edge cases:**
  - Zero-info mode: if Maher skips all Step 3 questions, model pre-fills with industry-baseline answers labelled BASELINE. Maher still reviews each item before it enters the register — never auto-approved.
  - Maher skips entire sub-area (Step 2 = N): sub-area excluded from register; recorded in state.json as explicitly excluded.
  - All items skipped: model warns "register is empty" before allowing final assembly.
  - Edit loop: after one model revision, if Maher still disagrees, he can manually override parameters directly. Override recorded in audit_log.

**Out of scope:** Auto-approving any item without Maher review. Generating the full register in a single model call.

**Open questions for Architect:** How does the per-item conversation loop integrate with the existing orchestrator pipeline? FRM currently runs Junior → PM → Partner in sequence. The new design replaces Junior with an interactive loop. PM and Partner review still apply to the assembled register, not individual items.

---

### BA-003 — Historical Register and Report Knowledge Base
- Status: CONFIRMED
- Scope: Firm-level knowledge library built from Maher's historical work product

**User outcome:** Zero-information drafts draw from GoodWork's actual past work, not just generic regulatory baselines. Quality of baseline drafts improves as the library grows.

**Business rules:**
  - Library is firm-level, not per-engagement. Stored at firm_profile/historical_registers/ (FRM) and firm_profile/historical_reports/{service_type}/ (DD, Sanctions, Transaction Testing, etc.).
  - Upload at any time — during firm setup or after completing new engagements.
  - Per upload: model runs a structured intake conversation to understand the document (industry, jurisdiction, company size, modules/scope covered, date, completeness).
  - Index file created/updated per service type: firm_profile/historical_registers/index.json, firm_profile/historical_reports/due_diligence/index.json, etc.
  - At new engagement intake: model maps current engagement parameters against index. Pulls most relevant historical items as starting draft labelled FROM_SIMILAR_ENGAGEMENT.
  - Two labels in zero-info drafts: BASELINE (from regulatory knowledge) and FROM_SIMILAR_ENGAGEMENT (from historical library). Both are draft status — require Maher review before entering deliverable.
  - Sanitisation is mandatory at ingestion: strip all client names, entity names, individual names, passport/registration numbers, case IDs. Only patterns, categories, ratings, and methodology structures are indexed. Model must never surface identifying details from historical work into new engagement outputs.
  - Real GoodWork seed data: CE Creates DD reports (3 individual/entity reports) are the first entries for firm_profile/historical_reports/due_diligence/. CE Creates proposals seed firm_profile/historical_reports/proposals/. Existing FRM registers seed firm_profile/historical_registers/.

**Edge cases:**
  - No historical entries yet: system falls back to BASELINE (regulatory knowledge) only. No error.
  - Historical entry from very different industry: model flags low similarity match; Maher confirms whether to use or ignore.
  - Conflict between BASELINE and FROM_SIMILAR_ENGAGEMENT: both shown to Maher with source label; Maher chooses.

**Out of scope:** Sharing historical data across different Maher installations. Automated sync to cloud. Using client names from historical reports in new engagement outputs.

---

### BA-004 — Zero-Information Content Floors
- Status: CONFIRMED
- Scope: All workflows — minimum output when consultant provides zero client documents and minimal intake

**User outcome:** Every workflow always returns a usable starting-point draft. Maher never sees a blank deliverable when domain knowledge exists to populate it.

**Business rules — content floor per workflow:**
  - FRM: ~10 industry-baseline risks from knowledge file, sector-specific (e.g. UAE fintech → AML/KYC, transaction monitoring gaps, PEP onboarding, sanctions exposure, insider fraud, bribery/ABC, cyber fraud, regulatory reporting gaps). Labelled BASELINE.
  - Investigation Report: Typology-based findings structure + open_questions list for Maher to answer. No invented facts — framework and methodology pre-populated; findings section is empty until Maher provides evidence.
  - Policy / SOP: Regulatory framework defaults for jurisdiction (UAE Labour Law, DIFC/ADGM employment rules, ACFE reporting standards, UAE data protection). Gaps clearly flagged.
  - Proposal: Structure template (7 sections) pre-populated with firm_profile credentials, placeholder rates. Never blank.
  - Due Diligence: 5-phase methodology structure pre-populated; subject profile fields blank — model cannot fabricate identity data. Sources list pre-loaded by jurisdiction.
  - Sanctions Screening: All 5 screening lists pre-loaded (OFAC/UN/EU/UK OFSI/UAE Local); subject fields blank — ready to screen on receipt of subject name.
  - Transaction Testing: ACFE-methodology test objectives for the stated fraud type (e.g. procurement fraud → three-way matching test plan, duplicate payment test, vendor concentration analysis). Data fields blank until Maher uploads data.
  - System prompt instruction (all agents): "Never return empty findings/risks — populate with industry baseline if no client-specific evidence is available, clearly labelled as BASELINE (unverified) for Maher review."

**Edge cases:**
  - Maher provides partial intake: use what is provided + fill gaps with BASELINE. Do not ask for more information before producing a draft — produce the draft and note what is missing.
  - Unknown jurisdiction: fall back to UAE regulatory context + flag that jurisdiction-specific review is needed.

**Out of scope:** Auto-finalising any BASELINE content without Maher review.

---

### BA-005 — Service Line Priorities — Phase 10–12
- Status: CONFIRMED
- Scope: Three new service lines to build first from the Phase 10 list of 7

**Business rules:**
  - Priority 1: Due Diligence (SL-02) — highest frequency UAE engagement type; clear deliverable structure; real GoodWork reports exist as templates.
  - Priority 2: Sanctions Screening (SL-04) — sanctions_check.py already built; fastest to wire into a full workflow; repeatable revenue per onboarding; UAE/ME market priority.
  - Priority 3: Transaction Testing (SL-01) — complements existing investigation workflow; reuses junior agent + evidence handling infrastructure.
  - Deferred: Fraud Audit (SL-03), ESI Review (SL-05), Expert Witness (SL-06), HUMINT (SL-07).
  - Build order within the three: Due Diligence → Sanctions Screening → Transaction Testing.

---

### BA-006 — Due Diligence Intake — Individual Branch
- Status: CONFIRMED
- Scope: Intake questionnaire for DD engagements where the subject is a natural person

**Business rules:**
  - Step 0 (branch gate): first question is always "Is the subject an Individual or an Entity?" This determines which branch to follow. Individual branch = this entry.
  - 14 intake questions (in order):
    1. Full legal name (as on passport)
    2. Date of birth
    3. Place of birth
    4. Nationality / nationalities
    5. Passport number (if available — drives sanctions fuzzy match accuracy)
    6. Known corporate affiliations (companies they direct or own)
    7. Purpose of the DD (onboarding, investment, partnership, employment, acquisition)
    8. Level of screening required: Standard Phase 1 (sanctions/PEP/adverse media) or Enhanced Phase 2 (HUMINT, deeper corporate mapping, board-ready narrative)
    9. Which screening lists apply (OFAC / EU / UN / UK OFSI / UAE Local / all)
    10. Screen associated individuals too? (family members, known associates)
    11. Jurisdictions the subject operates in or has connections to
    12. Specific concerns or red flags that triggered this DD
    13. Is the subject aware this DD is being conducted?
    14. Timeline and deliverable format (screening memo / full report / regulatory submission / board pack)
  - Standard report structure (from real CE Creates reports): Executive Summary → Subject Profile → Methodology & Sources → Sanctions Results → PEP Results → Adverse Media → Conclusion & Risk Classification.
  - Risk classification output: LOW / MEDIUM / HIGH + CLEAR or FLAG.

**Edge cases:**
  - Subject has multiple nationalities: screen under all. Fuzzy matching applied for name variants.
  - Enhanced DD requested but HUMINT required: model scopes the HUMINT requirements in the deliverable and flags for manual execution. AI tool does not perform HUMINT.
  - Passport number not available: proceed without it; flag that match accuracy is reduced.

**Out of scope:**
  - HUMINT execution (scoping only)
  - WorldCheck / WorldCompliance screening (tool limited to free official list lookups; licensed DB screening is manual)
  - Urdu-language adverse media for Pakistani databases (sub-contractor dependency)
  - Legal advice or formal risk determination

---

### BA-007 — Due Diligence Intake — Entity Branch
- Status: CONFIRMED
- Scope: Intake questionnaire for DD engagements where the subject is a legal entity

**Business rules:**
  - Step 0 (branch gate): triggered when Maher selects "Entity" at the Individual/Entity decision.
  - 14 intake questions (in order):
    1. Full registered legal name
    2. Company / registration number
    3. Jurisdiction of incorporation
    4. Principal operating jurisdictions
    5. Business activity description
    6. Key principals to screen: directors, shareholders, UBOs (names + roles)
    7. Purpose of the DD (acquisition, investment, vendor onboarding, JV, partnership)
    8. Level of screening: Standard Phase 1 or Enhanced Phase 2
    9. Which screening lists apply
    10. Screen all beneficial owners above 25% threshold, or named individuals only?
    11. Is the entity part of a group? (triggers group-level corporate mapping)
    12. Specific concerns or red flags
    13. Is the target aware?
    14. Timeline and deliverable format
  - Standard report structure: Executive Summary → Entity Profile → Methodology & Sources → Sanctions Results → Beneficial Ownership Analysis → Adverse Media → Regulatory Compliance Status → Conclusion.
  - CE Creates DD reports (GiveBrite entity + 3 individual reports) are the seed data for firm_profile/historical_reports/due_diligence/ and the template source for knowledge/due_diligence/.

**Edge cases:**
  - Group structure identified: model maps known entities in the group; flags that full group mapping may require additional research time.
  - UBO below 25% but strategically significant: Maher can add them manually to the screening list.

**Out of scope:** Same as BA-006 (HUMINT execution, WorldCheck, Urdu databases, legal advice).

---

### BA-008 — Sanctions Screening Intake
- Status: CONFIRMED
- Scope: Intake questionnaire for standalone Sanctions Screening engagements

**Business rules:**
  - 12 intake questions (in order):
    1. What is the entity being screened? (company, individual, vessel, or combination)
    2. Purpose (client onboarding, transaction approval, ongoing monitoring, regulatory requirement)
    3. Which screening lists apply (OFAC SDN / UN Consolidated / EU / UK OFSI / UAE Local / all)
    4. PEP screening required?
    5. Jurisdictions the entity operates in or has connections to
    6. Known aliases, alternate spellings, or former names
    7. One-time screen or recurring monitoring requirement?
    8. Ownership structure — screen beneficial owners too?
    9. Existing relationships or prior screens to be aware of
    10. Required output format (internal clearance memo / regulatory filing / court-ready report / screening spreadsheet)
    11. Nature of the relationship (customer / vendor / counterparty / investor) — affects risk tolerance and escalation threshold
    12. Sector the entity operates in (defense / energy / financial services / real estate carry elevated sanctions exposure — determines screening depth)
  - Tool covers: OFAC SDN, UN Security Council, EU Consolidated, UK OFSI, UAE Local Terrorist List (5 lists).
  - Licensed databases (WorldCheck, WorldCompliance) are NOT accessible to this tool. Gap must be disclosed in the scope output.

**Edge cases:**
  - Batch screening requested (multiple entities): tool can process one at a time; batch processing is a manual workflow using the tool per entity.
  - Match found: tool outputs match details + false positive analysis. Escalation recommendation included. Does not constitute a formal determination.
  - Recurring monitoring: tool does not support automated recurring checks; Maher must re-run manually or set a calendar reminder.

**Out of scope:** WorldCheck/WorldCompliance screening, HUMINT, legal determination of sanctions status.

---

### BA-009 — Transaction Testing Intake
- Status: CONFIRMED
- Scope: Two-stage scoping process for Transaction Testing engagements

**User outcome:** Transaction Testing is never scoped with a flat questionnaire. Maher gets a proposed testing plan from the model before any document ingestion begins.

**Business rules:**
  - STAGE 1 — Engagement context (mandatory first question): which of the following best describes this engagement?
    A. Fraud investigation — discovery mode (does fraud exist?)
    B. Fraud investigation — quantification mode (fraud confirmed, measure the loss)
    C. Audit / compliance review (testing controls against a framework)
    D. Due diligence (financial integrity pre-acquisition / pre-investment)
    E. Regulatory requirement (regulator-mandated testing)
    Branch A/B surfaces first as the default (primary context for GoodWork).
  - STAGE 2 — Branch-specific questions:
    Branch A/B: fraud typology (procurement / payroll / expense / cash / financial statement / AML) → data inventory → population size and date range → specific suspects already identified → discovery vs quantification.
    Branch C: controls framework → specific controls under test → prior audit findings.
    Branch D: target financial systems → period → specific integrity concerns.
    Branch E: which regulator → prescribed methodology → reporting deadline.
    Common core (all branches): evidence standard required / data formats available / full population vs sampling / timeline.
  - STAGE 3 — Model proposes testing plan: "Based on your inputs, I recommend testing these areas using these methods. Population: X / Date range: Y / Method: Z." Maher reviews and confirms or adjusts scope before any document ingestion begins. Testing plan is locked in state.json before proceeding.
  - Fraud typology drives methodology entirely:
    Procurement fraud → three-way matching (PO / Invoice / Payment), vendor master analysis, split PO testing.
    Payroll fraud → ghost employee check, rate manipulation, overtime analysis.
    Expense fraud → duplicate submissions, round-dollar, weekend/holiday spend.
    Cash fraud → petty cash reconciliation, sequencing gaps.
    Financial statement fraud → journal entry testing, cut-off, revenue recognition.
    AML → pattern detection, structuring, counterparty analysis.

**Edge cases:**
  - Engagement context is ambiguous: model asks one follow-up to clarify before branching.
  - Data not yet available at intake: scope plan still generated; data fields left blank; case stays at INTAKE_CREATED until Maher uploads data.
  - Multiple fraud typologies: model proposes a combined testing plan covering all; Maher can deselect individual components.

**Out of scope:** Automated data analysis (model structures the testing plan; Maher executes or uploads the data for model-assisted analysis). Statistical sampling methodology is advisory — Maher decides final sample size.

---

### BA-010 — Engagement Scoping Workflow
- Status: CONFIRMED
- Scope: Problem-first dynamic scoping for new engagements where service type is not yet known

**User outcome:** Maher can describe a client situation in plain language and receive a structured, recommended engagement scope — without knowing in advance which GoodWork service applies.

**Business rules:**
  - Triggered by: "Start New Engagement / Scope This Case" menu item (additional to existing 10-item menu).
  - 70% of GoodWork engagements start with known scope — existing menu handles these. 30% are ambiguous — this workflow handles those.
  - 5-step flow:
    1. Baseline knowledge: model holds full taxonomy of forensic engagement types (knowledge/engagement_taxonomy/) with triggering scenarios, scope components, deliverables, frameworks, regulatory context.
    2. Contextual intake: model asks about the CLIENT'S SITUATION ("Tell me about the client and what they're facing" / "What triggered this?" / "What does the client want to walk away with?").
    3. Scope recommendation: model proposes engagement type(s), scope components, deliverables, sequencing, caveats. Presented as draft for review.
    4. Interview to refine: model asks targeted follow-ups to close gaps ("Is the client a regulated entity?" / "Do you have data access confirmed?"). Maher answers; model revises.
    5. Scope document delivered: confirmed scope with rationale. For standard engagements → routed to existing workflow. For unique/hybrid → scope document is the deliverable.
  - For known-scope cases via existing menu: lightweight intake confirmation still runs (validating scope components for this specific client, any exclusions) — not a full discovery.
  - Both paths converge at a confirmed scope document before drafting begins.
  - Maher uploads previous scope letters and engagement letters to firm_profile/historical_scopes/. Model ingests these to calibrate recommendations to GoodWork's actual practice.
  - knowledge/engagement_taxonomy/ is a new knowledge file (KF-NEW) — highest priority for Phase 12. Must cover all 18+ forensic engagement types with triggering scenarios, standard scope components, typical deliverables, applicable frameworks, regulatory context, and scope intersections.

**Edge cases:**
  - Client situation maps to multiple engagement types: model recommends a phased approach (e.g. DD first, then investigation if red flags found). Chaining rules from BA-011 apply.
  - Engagement type not in taxonomy: model flags it as outside GoodWork's standard service lines and asks Maher to define scope manually.
  - HUMINT required: scope document explicitly flags HUMINT as a manual execution requirement; tool cannot perform it.

**Out of scope:** Automated engagement routing without Maher confirmation. Replacing the existing 10-item menu.

---

### BA-011 — Workflow Chaining Rules
- Status: CONFIRMED
- Scope: Compatible follow-on workflow combinations within a single case_id

**Business rules:**
  - After any workflow completes, system asks: "Add another deliverable to this case?"
  - Compatible chains (offered):
    · Investigation Report → Persona Review
    · Investigation Report → Proposal (findings → remediation engagement)
    · FRM Risk Register → Policy / SOP
    · FRM Risk Register → Training Material
    · FRM Risk Register → Proposal
    · Due Diligence → Investigation Report (red flag escalation)
    · Due Diligence → Sanctions Screening (deeper screen on finding)
    · Due Diligence → Proposal
    · Transaction Testing → Investigation Report (fraud confirmed → full investigation)
    · Proposal → Proposal Deck (already in run.py)
    · Sanctions Screening → Investigation Report (match confirmed → escalate)
  - Blocked chains (never offered):
    · Proposal → FRM (backwards — FRM informs proposals, not the other way)
    · Training Material → Investigation Report (no logical connection)
  - All chained workflows share the same case_id. state.json updated with all workflow runs. case_tracker shows all deliverables per case_id.
  - Chaining is always opt-in — never automatic.

**Edge cases:**
  - Maher wants to chain a blocked combination: he can start a new case manually, but the system will not offer it as a follow-on.
  - Multiple chains in sequence: permitted (e.g. DD → Investigation → Proposal). Each chain step is confirmed before proceeding.

**Out of scope:** Automated chaining without Maher confirmation. Cross-case chaining (different case_ids).

---

## Architectural Constraints — Session 010

[2026-04-06] Licensed database gap: Tool is limited to free official list lookups (OFAC/UN/EU/UK OFSI/UAE). WorldCheck and WorldCompliance are NOT accessible. Every DD and Sanctions output must include a disclaimer stating this limitation. Maher uses his own licensed database subscriptions for commercial-grade screening.

[2026-04-06] HUMINT boundary: AI tool cannot perform discreet source enquiries. Tool scopes and structures HUMINT requirements in the deliverable; execution is manual (Maher or sub-contractor). Every scope output involving HUMINT must explicitly flag this.

[2026-04-06] Urdu language coverage: official Pakistani databases and Urdu-language adverse media are sub-contractor dependent. Tool covers English and Arabic only for automated research.

[2026-04-06] Historical reports import: firm_profile/historical_registers/ and firm_profile/historical_reports/{service}/ require a guided import wizard at firm setup. CE Creates reports (3 DD reports) are the seed data for the DD library. Sanitisation step is mandatory at ingestion — strip all names, IDs, case references before indexing.
