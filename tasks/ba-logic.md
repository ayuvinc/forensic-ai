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

---

## Session 011 BA — Knowledge File Audit (2026-04-07)

---

### BA-012 — Policy/SOP Knowledge File Scope Clarification
- Status: DRAFT — **OPEN QUESTION FOR AK**
- Scope: knowledge/policy_sop/framework.md (KF-00) — scope of mandatory sections

**User outcome:** Model generates correct mandatory sections for the specific policy type Maher is drafting — not a generic checklist applied regardless of policy type.

**Background:**
KF-00 (built Sprint-10A) marks 7 of its 8 sections as MANDATORY for ALL policy/SOP types.
workflows/policy_sop.py handles multiple policy types. Sections relevant to speaking-up/reporting
policies are irrelevant in other policy types:

| Section | Whistleblower Policy | Data Protection Policy | Anti-Bribery Policy | Procurement Policy |
|---------|---------------------|----------------------|--------------------|--------------------|
| Anonymous complaint handling | MANDATORY | Not applicable | Conditional | Not applicable |
| Retaliation mechanism + disciplinary matrix | MANDATORY | Not applicable | Conditional | Not applicable |
| Evidence chain of custody | MANDATORY | Conditional | Conditional | Not applicable |
| SLA for closure comms | MANDATORY | Conditional | Conditional | Not applicable |
| Malicious vs good-faith definition | MANDATORY | Not applicable | Not applicable | Not applicable |
| Data protection integration | CONDITIONAL (jurisdiction) | MANDATORY | Conditional | Conditional |
| Vendor enforcement | CONDITIONAL | Conditional | MANDATORY | MANDATORY |
| Metrics/KPI for Audit Committee | CONDITIONAL | Conditional | MANDATORY | Not applicable |

**Business rules (proposed, pending AK confirmation):**
  - Policy types are categorised at intake: "reporting_policy" (whistleblower, speak-up, fraud hotline), "compliance_policy" (ABC, AML, data protection), "operational_policy" (procurement, IT, finance), "hr_policy" (disciplinary, performance)
  - KF-00 sections tagged with applicable policy types: mandatory / conditional / not_applicable
  - Junior system prompt receives only the relevant sections for the intake policy type
  - Data protection integration (Section 6) is CONDITIONAL on jurisdiction, not policy type — it applies whenever the policy involves personal data, regardless of type

**Edge cases:**
  - Maher does not specify policy type at intake: model asks one clarifying question before drafting
  - Policy spans multiple types (e.g. Whistleblower + Data Protection merged policy): all applicable mandatory sections apply
  - New policy type not in taxonomy: model applies minimum mandatory set (data protection + vendor enforcement + audit KPIs) and flags which sections may not apply

**Out of scope:** Redesigning the entire KF-00 framework — the 8 sections are correct and complete for whistleblower policies. The only change needed is tagging each section with its applicable policy types.

**Open question for AK:**
  1. Is my categorisation above correct? Specifically: does Maher draft Anti-Bribery Policies as a standalone service, or does ABC always come bundled with FRM Module 1 (Governance & Policy)?
  2. Should policy type be captured at intake as a structured field (Maher picks from a list), or inferred by the model from the policy name/description Maher provides?
  3. Does Maher want the model to proactively suggest missing policy types when scoping? (e.g. "You're drafting a Whistleblower Policy — do you also want a Retaliation Investigation Procedure as a companion document?")

---

### BA-013 — knowledge/policy_sop/sources.md Required
- Status: CONFIRMED (no open questions — straightforward completion task)
- Scope: Companion sources file for KF-00, referenced in framework.md but not yet created

**User outcome:** Junior analyst has a curated, verified source list for regulatory citations in policy/SOP deliverables. Avoids re-searching for the same regulatory instruments in every case.

**Business rules:**
  - Same structure as knowledge/frm/sources.md and knowledge/investigation/sources.md
  - Must cover: UAE onshore (Federal laws), DIFC, ADGM, India (SEBI/POSH/DPDP), UK (FCA/ICO), international standards (ISO 37001, ACFE, IIA)
  - Each source entry: source name, jurisdiction, URL, what it covers, trust level (authoritative / reference)
  - Authoritative sources: government/regulator URLs only — cb.gov.ae, dfsa.ae, adgm.com, mohre.gov.ae, sebi.gov.in, ico.org.uk, fca.org.uk
  - Reference sources: ISO, ACFE, IIA standards (no URL — accessible via subscription or purchase; note this)

**Edge cases:**
  - URL no longer valid at research time: regulatory_lookup.py returns "no authoritative source found" — disclaimer added; sources.md is a starting-point guide, not a guarantee
  - Jurisdiction not in list: model falls back to UAE context + flags that jurisdiction-specific review needed

**Out of scope:** Populating the sources file with full text of legislation. Source list only — URLs, names, what each covers.

---

### BA-014 — knowledge/engagement_taxonomy/framework.md Content Requirements (KF-NEW)
- Status: CONFIRMED — 2026-04-07 (AK answered all 5 questions)
- Scope: Engagement taxonomy knowledge file — gates SCOPE-WF-01 (engagement scoping workflow)

**User outcome:** Model can identify the correct GoodWork service line from a plain-language client situation description, propose a structured scope, and route to the right workflow — without Maher knowing the service line name upfront.

**Business rules:**
  - File must cover every GoodWork-deliverable engagement type with enough detail for the model to distinguish between types when the situation is ambiguous
  - Per engagement type, minimum required:
    1. Triggering scenarios: what client situations lead to this engagement
    2. Standard scope components: what work is always included vs optional
    3. Typical deliverables: what Maher produces at the end
    4. Applicable frameworks: ACFE / IIA / ISO / UAE regulatory standard that governs this type
    5. Common scope combinations: which engagement types are typically paired or sequenced
    6. Exclusions: what this type does NOT cover (important for scoping conversations)
    7. Red flags that escalate: situations where this engagement type should expand to another
  - Engagement types to cover (architect-validated list from Session 010, BA confirmation pending):

| # | Type | GoodWork Active? | Notes |
|---|------|-----------------|-------|
| 1 | FRM Risk Register | YES — core | 8 modules, already built |
| 2 | Investigation Report — General | YES — core | 7 sub-types |
| 3 | Investigation Report — Procurement Fraud | YES | Sub-type of 2 |
| 4 | Investigation Report — Payroll Fraud | YES | Sub-type of 2 |
| 5 | Investigation Report — Expense Fraud | YES | Sub-type of 2 |
| 6 | Investigation Report — Financial Statement Fraud | YES | Sub-type of 2 |
| 7 | Investigation Report — AML/Financial Crime | YES | Sub-type of 2 |
| 8 | Investigation Report — Whistleblower | YES | Sub-type of 2 |
| 9 | Investigation Report — Insurance Fraud | Confirm with AK | |
| 10 | Due Diligence — Individual | YES — new | BA-006 confirmed |
| 11 | Due Diligence — Entity | YES — new | BA-007 confirmed |
| 12 | Transaction Testing | YES — new | BA-009 confirmed |
| 13 | Sanctions Screening | YES — new | BA-008 confirmed |
| 14 | Policy / SOP | YES — core | Already built |
| 15 | Training Material | YES — core | Already built |
| 16 | Client Proposal | YES — core | Already built |
| 17 | Engagement Scoping (standalone) | YES — new | Meta-service |
| 18 | Asset Tracing | Confirm with AK | Separate from investigation? |
| 19 | ABC Programme | Confirm with AK | FRM Module 1 subset or standalone? |
| 20 | Expert Witness Support | DEFERRED | Cut-for-now per scope-brief |
| 21 | ESI / e-discovery | DEFERRED | Cut-for-now |
| 22 | HUMINT | DEFERRED | Cut-for-now |

**AK confirmations (2026-04-07):**
  1. Insurance Fraud Investigation — NOT a GoodWork-active service. Exclude from taxonomy.
  2. Asset Tracing — NOT standalone; always part of investigation engagement. No separate taxonomy entry.
  3. ABC Programme — CAN BE standalone OR bundled with FRM Module 1. Both paths in taxonomy.
  4. Investigation sub-types — DISTINCT entries (7 entries, not one entry with branching).
  5. Insolvency Fraud — NOT a GoodWork service. Exclude from taxonomy.
  Also confirmed: No CE Creates reports available as reference for KF-02 — must work from standard methodology.

**Edge cases:**
  - Client situation maps to a deferred service line (ESI, Expert Witness): model acknowledges it, flags as outside current tool scope, suggests the closest available service
  - Ambiguous situation (could be investigation OR due diligence): model asks one clarifying question, presents both options with distinction
  - Novel situation not in taxonomy: model flags as outside standard service lines, offers to draft a custom scope document manually

**Open questions for AK (ALL required before KF-NEW can be authored):**
  1. Is Insurance Fraud Investigation a GoodWork-active service? Has Maher done these? If yes, what triggers the engagement and what does the deliverable look like?
  2. Is Asset Tracing a standalone GoodWork service, or is it always part of an investigation? If standalone — what's the typical deliverable (asset schedule, court-ready report, both)?
  3. Is ABC Programme a standalone service (separate from FRM Module 1), or is it only delivered as part of FRM? If standalone — what does a GoodWork ABC engagement produce?
  4. For Investigation Report taxonomy: should the 7 sub-types be distinct engagement entries in the taxonomy (so the model can distinguish "this is a payroll fraud investigation" from "this is a procurement fraud investigation"), or is one "Investigation Report" entry with sub-type branching sufficient?
  5. Does GoodWork scope Insolvency Fraud investigations? (High-frequency UAE/GCC type — involved assets hidden before insolvency filing)

---

### BA-015 — knowledge/due_diligence/framework.md Content Requirements (KF-02)
- Status: DRAFT — partial open questions for AK
- Scope: DD knowledge file — gates SL-GATE-01 (due_diligence workflow)

**User outcome:** Junior analyst drafts DD reports using GoodWork's actual methodology and report structure, not a generic template. CE Creates reports are the benchmark.

**Business rules:**
  - GoodWork's DD methodology is derived from CE Creates reports (the firm Maher came from). The knowledge file should reflect that methodology, not a generic external framework.
  - 5-phase structure (confirmed from memory — validate with AK):
    Phase 1: Subject identification and scope confirmation
    Phase 2: Open-source intelligence gathering (OSINT)
    Phase 3: Sanctions and PEP screening (5 official lists)
    Phase 4: Adverse media and regulatory record review
    Phase 5: Corporate mapping and beneficial ownership analysis (entity DD)
  - Report structure mirrors CE Creates template (confirmed BA-006/007):
    Individual: Executive Summary → Subject Profile → Methodology → Sanctions → PEP → Adverse Media → Conclusion
    Entity: Executive Summary → Entity Profile → Methodology → Sanctions → Beneficial Ownership → Adverse Media → Regulatory Compliance Status → Conclusion
  - Risk classification: LOW / MEDIUM / HIGH — criteria must be explicit (not left to model judgment):
    LOW = no sanctions match, no adverse media, no PEP, no red flags
    MEDIUM = inconclusive match, limited adverse media, tangential connection to flagged entity
    HIGH = confirmed sanctions match, confirmed PEP with unmitigated risk, significant adverse media
  - CLEAR vs FLAG binary alongside risk classification: CLEAR = no further action recommended; FLAG = escalation or further investigation recommended
  - Source list by jurisdiction: UAE (MOEC, DED, ADGM, DIFC registries), GCC, India (MCA21, CIBIL), UK (Companies House), international (OpenCorporates, Orbis)

**Edge cases:**
  - Subject has common name (high false positive risk): model notes this explicitly in methodology section; all matches listed with confidence rating
  - Subject has name variants (Arabic/English transliteration): model screens under all variants; notes them in methodology
  - No records found at all: model must distinguish "no records found" from "subject is clear" — they are not the same

**Open questions for AK:**
  1. Is the 5-phase methodology above accurate for GoodWork? Or does Maher follow a different structure? (CE Creates methodology may have evolved)
  2. Does GoodWork use a standardised engagement letter for DD, or does it vary? This determines whether there's a scope confirmation step before screening begins.
  3. What is GoodWork's standard turnaround for a Phase 1 DD? (Sets the timeline field default at intake)
  4. Can the BA access one of the CE Creates DD reports as a reference? (Maher has these on Desktop/GoodWork/ — reading one would significantly improve KF-02 accuracy)

---

### BA-016 — knowledge/sanctions_screening/framework.md Content Requirements (KF-04)
- Status: DRAFT — one open question for AK
- Scope: Sanctions screening knowledge file — gates SL-GATE-02

**User outcome:** Sanctions screening memos are produced against a consistent methodology that Maher can stand behind professionally — not ad hoc web searches.

**Business rules:**
  - 5 official screening lists (confirmed, already in sanctions_check.py): OFAC SDN, UN Security Council Consolidated List, EU Consolidated Sanctions List, UK OFSI Consolidated List, UAE Local Terrorist Designation List
  - PEP classification: model must classify PEPs by category and risk level
    Category 1 (highest): heads of state, government ministers, senior military/judiciary
    Category 2: senior government officials, state-owned enterprise executives, ambassadors
    Category 3: local/regional officials, family members of Category 1/2
    Retired PEPs: same classification as active but with time-decay on risk rating (typically 12-24 months)
  - False positive analysis: every potential match must be assessed for false positive probability before flagging
    Match confidence scoring: name similarity % + date of birth match (if available) + nationality match + known alias match
    Threshold for "inconclusive match" vs "confirmed match" must be stated in the methodology
  - Worldcheck gap disclosure: every output must include the licensed database disclaimer (ARCH-GAP-01 text) — not negotiable, not optional
  - Output format options per intake Q10: internal clearance memo / full report / regulatory filing / screening spreadsheet
    Each format has a different level of narrative — clearance memo is shortest, regulatory filing is most formal

**Edge cases:**
  - Match found but clearly different individual (same name, different DOB, different nationality): document as "false positive — same name" in the output; do not flag
  - Match found with insufficient information to confirm or exclude: "inconclusive — further information required" — model cannot make a determination; escalation recommended
  - Subject name in Arabic only (no English transliteration): model transliterates and screens under both; notes methodology
  - Batch of subjects: tool processes one at a time; model notes at intake that batch processing is manual (BA-008 edge case, already confirmed)

**Open question for AK:**
  1. Does GoodWork have a house standard for what constitutes a "CLEAR" result on a sanctions screening (e.g. no hits on any of the 5 lists = CLEAR, regardless of adverse media)? Or is CLEAR/FLAG determined holistically across sanctions + PEP + adverse media combined?

---

### BA-017 — knowledge/transaction_testing/framework.md Content Requirements (KF-01)
- Status: DRAFT — two open questions for AK
- Scope: Transaction Testing knowledge file — gates SL-GATE-03

**User outcome:** Transaction Testing engagements start with a model-proposed testing plan grounded in ACFE methodology, not invented from scratch. Maher refines rather than creates from blank.

**Business rules:**
  - ACFE methodology coverage per fraud typology (6 types confirmed in BA-009):

    Procurement fraud:
    → Three-way matching: PO date vs Invoice date vs Payment date — any out-of-sequence is an exception
    → Vendor master analysis: new vendors registered shortly before large invoices; duplicate registrations
    → Split PO testing: orders just below approval threshold; sequence of same-vendor orders on same day
    → Conflict of interest: cross-reference vendor addresses/accounts against employee records

    Payroll fraud:
    → Ghost employee: employees with no line manager, no HR file, or terminated employees still receiving pay
    → Rate manipulation: pay rate changes without HR approval record; changes effective on unusual dates
    → Overtime analysis: employees with >X% of base salary in overtime; patterns by department/supervisor

    Expense fraud:
    → Duplicate submission: same amount, same vendor, short date range — especially across periods
    → Round-dollar testing: amounts that are exactly round numbers (suspicious in genuine expense reports)
    → Weekend/holiday spend: expenses on dates when the business was closed
    → Policy compliance: maximum claim limits, prohibited categories, approver conflict

    Cash fraud:
    → Petty cash reconciliation: opening balance + receipts - disbursements ≠ closing balance
    → Sequencing gaps: missing receipt numbers in a series
    → Large round disbursements without supporting documentation

    Financial statement fraud:
    → Journal entry testing: manual JEs posted by senior personnel, at period end, to unusual accounts
    → Cut-off testing: revenue/expenses recorded in wrong period
    → Revenue recognition: shipments on last day of period; return reversals in next period

    AML:
    → Structuring detection: multiple transactions just below reporting threshold (CTR equivalent)
    → Counterparty analysis: transactions with sanctioned jurisdictions or high-risk countries
    → Velocity analysis: unusual transaction frequency changes; dormant accounts reactivating

  - Benford's Law: applicable to procurement and expense fraud testing where population is large enough
    Benford's applies to: invoice amounts, payment amounts, journal entry amounts
    Benford's does NOT apply to: payroll (amounts are set by contract), petty cash (too few transactions), rent/lease payments (fixed amounts)
    Model must note Benford's Law applicability in the testing plan when fraud typology is relevant

  - UAE regulatory testing context:
    CBUAE: AML testing requirements for licensed financial institutions (Transaction Monitoring reviews)
    DFSA: financial crime testing requirements for DIFC-regulated entities
    SCA: market manipulation testing for listed securities
    ADGM: FSRA AML testing requirements

  - Sampling guidance (advisory — Maher decides final sample size):
    Full population preferred for populations < 10,000 transactions
    Random statistical sampling (95% confidence, 5% margin) for populations > 10,000
    Judgmental sampling: always in addition to statistical sampling, not instead of — focus on high-risk periods and high-risk vendors/employees

**Edge cases:**
  - Multiple fraud typologies: model proposes a combined plan; Maher can deselect individual components before SCOPE_CONFIRMED
  - Data not in expected format: testing plan notes data format requirements; model cannot test what it cannot read (format mismatch is flagged before document ingestion)
  - Population too small for Benford's Law: model notes this and does not apply it; uses alternative procedures

**Open questions for AK:**
  1. Has Maher used Benford's Law in his actual engagements? Or is it theoretical knowledge only? This determines whether it's included in the knowledge file as a recommended procedure or just noted as an available technique.
  2. For the UAE regulatory context: does Maher deliver Transaction Testing to regulated financial institutions (banks, insurance companies) or primarily to non-regulated corporates? The regulatory framework section in KF-01 changes significantly based on the answer.

---

## BA Summary — Session 011 Knowledge Audit

**Knowledge file status:**

| File | Status | Blocker |
|------|--------|---------|
| knowledge/frm/framework.md | COMPLETE | None |
| knowledge/frm/sources.md | COMPLETE | None |
| knowledge/investigation/framework.md | COMPLETE | None |
| knowledge/investigation/sources.md | COMPLETE | None |
| knowledge/policy_sop/framework.md (KF-00) | BUILT — scope clarification needed | BA-012 open question |
| knowledge/policy_sop/sources.md | MISSING — needs creation | Straightforward; BA-013 confirmed |
| knowledge/engagement_taxonomy/framework.md (KF-NEW) | NOT STARTED | BA-014: 5 open questions for AK |
| knowledge/due_diligence/framework.md (KF-02) | NOT STARTED | BA-015: 4 open questions (1 critical) |
| knowledge/sanctions_screening/framework.md (KF-04) | NOT STARTED | BA-016: 1 open question |
| knowledge/transaction_testing/framework.md (KF-01) | NOT STARTED | BA-017: 2 open questions |

**Unblocked work (no AK input needed):**
- knowledge/policy_sop/sources.md (BA-013) — can be built now
- knowledge/sanctions_screening/framework.md (KF-04) — mostly unblocked; 1 clarification needed but file can be drafted with a placeholder
- knowledge/transaction_testing/framework.md (KF-01) — can be drafted; 2 clarifications improve depth but don't block the file
- KF-00 scope tagging (BA-012) — can be drafted pending AK confirmation on policy type categories

**AK input required before build:**
- BA-014 (KF-NEW): All 5 questions must be answered — taxonomy accuracy is the whole point of this file; wrong entries are worse than missing ones
- BA-015 (KF-02): Question 4 (CE Creates report access) is the highest-value input; the other 3 can be resolved with reasonable defaults


---

### BA-012 Update — Policy Type Questions 2 and 3 (Architect defaults, 2026-04-07)

AK answered Q1 (ABC Programme) via BA-014 confirmation: "can be any" (standalone or FRM-bundled).

Q2 — Should policy type be a structured intake field or model-inferred?
**Architect default:** Infer from policy name/description at intake. Model asks one clarifying question
only if type is genuinely ambiguous. Rationale: adding a structured pick-list adds friction to the
fastest workflow; the model has enough context to classify correctly in >90% of cases. If wrong,
Maher corrects and model re-classifies before drafting.

Q3 — Should model suggest companion documents?
**Architect default:** Yes — proactive suggestion is offered ONCE at the end of intake, not during
drafting. Example: "You're drafting a Whistleblower Policy — GoodWork typically pairs this with a
Retaliation Investigation Procedure. Want to add that as a second deliverable in this case?"
Rationale: captures upsell opportunity and closes a common scope gap without interrupting the draft.
AK can disable this per-session if it becomes noise.

**BA-012 status: CONFIRMED (with architect defaults — AK to validate on first Policy/SOP run)**


---

## BA-013 — FRM Engagement Suite (Option 6 redesign)

**Confirmed: 2026-04-07**

**Decision:** Option 6 is an FRM Engagement entry point, not just a risk register runner.
After intake, the user selects which deliverables are in scope for this engagement.

**Deliverable menu (confirmed):**
1. Risk Register (current 8-module pipeline)
2. Anti-Fraud Policy / SOP
3. Training Material

User enters numbers (e.g. `1,2` or Enter for all). All selected deliverables run under the same case ID and are saved to the same case folder.

**Sequencing rule:** Risk Register always runs first if selected (it informs the Policy and Training content). Policy runs before Training if both selected.

**UI flow:**
```
FRM Engagement — Case Intake
  [intake questions — client, industry, size, jurisdiction, scope]

  Which deliverables do you need?
    1. Risk Register
    2. Anti-Fraud Policy / SOP
    3. Training Material
  Enter numbers (e.g. 1,2 or Enter for all):
```

**Out of scope for this sprint:**
- No new module-level changes to frm_risk_register.py
- Policy/SOP and Training Material re-use existing workflows (policy_sop.py, training_material.py) — no new agent code needed

**BA-013 status: CONFIRMED**

---

## BA-014 — Industry/Function/Sub-Area Taxonomy (Structured Intake Options)

**Confirmed: 2026-04-07**

**Decision:** All intake questions that currently accept free text for industry, function, sub-area, and
service type must offer a numbered picklist with a free-text fallback option. This applies to every
workflow — FRM, Investigation, DD, Sanctions, TT, Scoping, Proposal.

**Why:** Structured intake data enables:
1. Industry-specific module pre-suggestion (e.g. Manufacturing → auto-suggest FRM Modules 3, 4, 6)
2. Case tracker filtering/grouping by industry and service type
3. Knowledge-file routing — model loads correct regulatory/risk baseline by industry automatically
4. Future: industry-specific report templates and risk benchmarks

**Taxonomy depth (v1):**
- Level 1: Industry (e.g. Manufacturing, Financial Services, Real Estate, Healthcare, Government)
- Level 2: Sub-sector (e.g. Manufacturing → Discrete / Process / FMCG / Construction)
- Free text always available as fallback — user types "Other: <custom value>"

**Taxonomy is data, not code:** Lives in `knowledge/taxonomy/industries.json`. Not hardcoded in
prompts or workflow files. Workflows load it at runtime. Adding a new industry = editing one JSON file,
no code change.

**Industry → FRM module pre-suggestion map:** Also in taxonomy data, not in frm_risk_register.py.
Example: `"Manufacturing": {"suggested_modules": [3, 4, 6], "rationale": "Procurement, HR, CapEx exposure"}`

**BA-014 status: CONFIRMED**

---

## BA-015 — True Modularity Design Principle

**Confirmed: 2026-04-07**

**Decision:** The framework must be truly modular — every axis of variation is a data/config file,
not a code branch. Adding a new industry, jurisdiction, service line, risk module, persona, or knowledge
domain must require zero changes to core Python code.

**Modularity axes (each must be a config/data file, not hardcoded):**

| Axis | Config location | Current state |
|------|----------------|--------------|
| Industries + sub-sectors | `knowledge/taxonomy/industries.json` | Hardcoded in prompts |
| FRM module definitions + dependencies | `knowledge/taxonomy/frm_modules.json` | Hardcoded in frm_risk_register.py |
| Workflow enablement per instance | `instance_config/firm.json` | Partially done (Phase 7) |
| Jurisdiction → regulator mapping | `config.py: JURISDICTION_REGISTRY` | In code — move to JSON |
| Knowledge file routing (industry × workflow) | `knowledge/taxonomy/routing_table.json` | Not yet built |
| Risk category definitions per module | `knowledge/frm/module_N_risks.json` | Embedded in knowledge .md files |
| Persona enablement | `instance_config/firm.json` | Partially done (Phase 7) |
| Agent model routing | `config.py: MODEL_ROUTING` | In code — acceptable, keep |

**Implementation principle:** Core Python reads config/data files and executes logic. Domain knowledge
(what industries exist, what modules apply, what risks are relevant) lives in data files only.
New firm = new instance config. New industry = new taxonomy entry. New service line = new knowledge dir + routing entry.

**What does NOT need to move:** Model routing, API keys, pipeline orchestration logic — these are
framework concerns, not domain knowledge.

**BA-015 status: CONFIRMED — architect to design modularity sprint after P7-GATE**

---

## Phase 9 BA Decisions — Session 021 (2026-04-18)

_AK confirmed all decisions directly in session conversation._

---

### BA-P9-01 — Project-Centric Engagement Model
- Status: CONFIRMED (AK session 021)
- Scope: Replace UUID-based case IDs with named projects; support multi-session input before final pipeline run

**User outcome:** Maher names each engagement (e.g. "Project A_FRM", "Project Alpha_DD"), can accumulate documents and notes across multiple sessions, and explicitly triggers the AI pipeline only when ready.

**Business rules:**
- Every engagement is a named Project, not a one-shot case. Project name is provided by Maher at intake.
- Naming convention is set per project at creation (e.g. "Client_ServiceType"). System suggests format; Maher confirms.
- Project slug derived from project name: lowercase, spaces → hyphens, special chars stripped. Used as folder name. Example: "Project Alpha FRM" → `project-alpha-frm`.
- Slug sanitization is mandatory before filesystem write — strip `..`, `/`, `\`, and any non-alphanumeric/hyphen character.
- Same project name + same service type = same project folder. Maher opens existing project to continue.
- At session start, Maher chooses: "Start New Project" or "Continue Existing Project".
- Two session modes:
  - **Input session**: upload documents, add working notes, record key facts / red flags. No pipeline run. Context accumulates.
  - **Final run**: explicitly triggered by Maher. Pipeline runs with full accumulated context.
- System asks at intake: "Is this an input session or a final run?" — never ambiguous.
- Old UUID-format cases (Phase 8) remain readable in Case Tracker. New projects use named slugs. Backward compatibility required.

**Edge cases:**
- Two projects resolve to the same slug: system detects collision, asks Maher to choose a different name.
- Maher attempts final run with zero documents and no working notes: system warns "No input materials found for this project. Proceed with zero-information baseline only?" Maher confirms.
- Maher attempts final run for a service type not yet set up in the project: system routes to intake for that service type first.

**Out of scope:** Cross-project linking; shared document libraries across projects.

---

### BA-P9-02 — A-F Physical Folder Structure (Industry Standard)
- Status: CONFIRMED (AK session 021)
- Scope: Forensic engagement folder structure following industry standard A–F sections

**User outcome:** Case folders are organized to match the physical file structure Maher would use on a real engagement — reviewable by regulators, auditors, or partners without re-explaining the layout.

**Business rules:**
- Every new project creates the following folder structure under `cases/{project_slug}/`:
  ```
  A_Engagement_Management/    ← scope letters, engagement contracts, authorizations
  B_Planning/                 ← testing plans, module selections, scope confirmations
  C_Evidence/                 ← client documents, source materials (date-timestamped sub-folders)
  D_Working_Papers/           ← session notes, interim analysis, key facts, red flags
  E_Drafts/                   ← agent outputs (junior_output.v*.json, pm_review.v*.json)
  F_Final/                    ← final_report.*, citations_index.json, audit_log.jsonl
  ```
- Document uploads during an input session: written to `C_Evidence/{YYYYMMDD-HHMMSS}/` (date-timestamped sub-folder per upload session).
- Existing artifacts from Phase 8 pipeline (interim/ folder) map to E_Drafts/ in the new structure.
- Maher can create custom sub-folders within any section. System does not block this.
- File Manager UI presents this structure to Maher for navigation — not just a list of all files.
- `state.json` and `audit_log.jsonl` remain at the project root (backward compat with existing tools).

**Edge cases:**
- Old UUID-format cases do not have A-F structure: Case Tracker shows them without the folder explorer panel; no migration required.
- Maher manually moves files outside the A-F structure: system accepts, no error. Folder integrity check is advisory, not enforced.

**Out of scope:** Automated document classification into A-F sections. File locking or access control.

---

### BA-P9-03 — Multi-Session Input Model
- Status: CONFIRMED (AK session 021)
- Scope: Accumulate input across multiple sessions before triggering the AI pipeline

**User outcome:** Maher can work on a case across multiple days, uploading documents and recording observations each session. The AI pipeline runs once when Maher is ready — with the full accumulated context.

**Business rules:**
- Input session capabilities (all additive, non-destructive):
  1. Upload documents → written to `C_Evidence/{timestamp}/`
  2. Add session notes (free text) → written to `D_Working_Papers/session_notes_{YYYYMMDD}.md`
  3. Record key facts (structured: fact, source, date) → appended to `D_Working_Papers/key_facts.json`
  4. Flag red flags (structured: description, severity, action) → appended to `D_Working_Papers/red_flags.json`
  5. View existing materials already registered in the project
- Final run session capabilities:
  1. Review accumulated materials summary before triggering pipeline
  2. Select which service type to run (if not pre-set)
  3. Confirm language standard, AI Review Mode setting
  4. Trigger pipeline — system passes full context (documents + notes + facts + red flags) to agents
- Session log: each session (input or final run) is timestamped and appended to `A_Engagement_Management/session_log.jsonl`.

**Edge cases:**
- Document uploaded in earlier session and now re-uploaded: system detects duplicate filename in the same project; warns and asks whether to overwrite or add as a new version.
- Final run triggered mid-input (session notes unsaved): system auto-saves pending notes before triggering pipeline.

**Out of scope:** Real-time collaborative sessions. Cloud sync between sessions on different machines.

---

### BA-P9-04 — Context Accumulation and 75% Threshold
- Status: CONFIRMED (AK session 021)
- Scope: DocumentManager context grows with uploads; near-capacity → write condensed summary

**User outcome:** Large document sets do not cause context overflow or silent truncation. Maher can work on large cases without worrying about the AI losing earlier documents.

**Business rules:**
- `DocumentManager` tracks cumulative token count across all registered documents in the project.
- Token counting uses a conservative estimate: character count / 4 (approximate Anthropic token ratio).
- Maximum context budget is derived from the active model's context window minus a 20% reserve for prompt + pipeline overhead. Configurable in `config.py` as `CONTEXT_BUDGET_CHARS`.
- At 75% of `CONTEXT_BUDGET_CHARS`: system writes `cases/{project_slug}/D_Working_Papers/interim_context.md`.
- `interim_context.md` contains: executive summary of all documents registered so far, key facts extracted per document, red flags noted, open questions. Written by the AI (Haiku for speed/cost).
- Subsequent sessions: if `interim_context.md` exists, `DocumentManager` loads it INSTEAD of re-reading all source documents. Source documents are still available for on-demand re-read if needed.
- `interim_context.md` is regenerated (overwritten) each time the threshold is crossed again (e.g. more documents added).
- Threshold trigger shown to Maher as an informational banner: "Context summary written to Working Papers — [N] documents condensed."

**Edge cases:**
- Single document exceeds 75% threshold alone: `interim_context.md` is written immediately after registration. Maher warned that the document is very large.
- `interim_context.md` itself is very long (edge case on top of edge case): it is not included in the 75% calculation — only source documents count.
- Pipeline run when `interim_context.md` exists: agents receive `interim_context.md` content plus any documents added after its creation (delta documents).

**Out of scope:** Per-agent context budgeting. Fine-grained token counting (exact Tiktoken integration).

---

### BA-P9-05 — Language Standards
- Status: CONFIRMED (AK session 021)
- Scope: Four forensic language standards applied at pipeline prompt level

**User outcome:** Maher selects the appropriate language standard at project intake. All agent-generated output automatically conforms to that standard — no manual post-editing of language style.

**Business rules:**
- Four standards, selectable at project intake and overridable per final run:
  1. **ACFE Internal Review**: narrative style, qualified findings ("it appears", "evidence suggests"), clear source attribution, structured methodology sections. Audience: internal Maher review or client internal committee.
  2. **Expert Witness**: past tense only, third person only, no pronouns, factual (no opinions, no inferences), evidence chain explicit for every finding. Court-ready. Audience: legal proceedings.
  3. **Regulatory Submission**: formal, regulatory references cited in full (Act name + section), prescribed structure matching the relevant regulator's format. Audience: regulator, statutory body.
  4. **Board Pack**: executive summary first, strategic framing, minimal technical jargon, findings expressed as business risk / business impact. Audience: board / C-suite.
- Universal rules applied to all four standards:
  - Past tense throughout (findings are stated as facts, not ongoing)
  - Third person only (no "we", "I", "our")
  - No pronouns referring to subjects (use full name/entity on first reference, abbreviated thereafter)
  - Qualified language for findings not directly evidenced (ACFE / Expert Witness standard)
- Standard selection stored in `state.json` at `language_standard` key.
- Standard is injected into all agent system prompts as a dedicated language instruction block.

**Edge cases:**
- Maher does not select a standard: system defaults to ACFE Internal Review.
- Maher changes standard mid-project (after some drafts exist): new standard applies to next final run only; previous drafts in E_Drafts/ are not retroactively rewritten.

**Out of scope:** Real-time language checking of Maher's own notes. Automated compliance checking against court-specific style guides.

---

### BA-P9-06 — AI Review Mode
- Status: CONFIRMED (AK session 021)
- Scope: Post-generation review layer that classifies evidence support, rewrites language, and detects logic gaps

**User outcome:** Before Maher reviews the draft, the AI has already flagged findings that lack direct evidence support and corrected language to match the selected standard — reducing the review burden significantly.

**Business rules:**
- AI Review Mode runs automatically after pipeline generates a draft, before Maher's review screen.
- Three review functions (all run in sequence):
  1. **Evidence support classification**: each finding is classified as:
     - `SUPPORTED` — direct, documentary evidence cited
     - `PARTIALLY SUPPORTED` — circumstantial or indirect evidence; inference required
     - `UNSUPPORTED` — analytical inference, industry knowledge, or no evidence chain
     Findings classified PARTIALLY SUPPORTED or UNSUPPORTED are flagged in Maher's review UI with the classification label. Maher can override any classification.
  2. **Language rewrite**: draft language rewritten to match the selected language standard (BA-P9-05). Rewrite is applied to the draft that Maher reviews — not a separate document.
  3. **Logic gap detection**: model identifies findings where the stated conclusion does not follow from the stated evidence. Each gap is noted inline (e.g. "Conclusion states X but no evidence of Y cited — gap flagged").
- AI Review Mode classifications are INTERNAL ONLY — never surface to client. They are stored in `D_Working_Papers/ai_review_notes_{YYYYMMDD}.md` for Maher's reference.
- Maher can disable AI Review Mode per-project in settings.

**Edge cases:**
- Finding has no citations at all: classified as UNSUPPORTED automatically — no model analysis needed.
- All findings classified SUPPORTED: review completes with a clean summary. No special action.
- Language rewrite changes a finding's meaning (edge case): Maher sees original and rewritten side by side (diff view) and can revert individual findings.

**Out of scope:** Automated citation lookup during review. Integration with external evidence databases.

---

## Session 022 Decisions — 2026-04-19

---

### BA-R-01 — Report Design Standard
- Status: CONFIRMED (AK session 022)
- Scope: All workflow final reports (DOCX + MD)

**User outcome:** Every client-facing report has a professional cover page, firm branding, standard section structure, and table of contents — regardless of which workflow produced it.

**Business rules:**
- DOCX is the primary client deliverable. MD is internal backup. No PDF for now.
- Section structure: Fixed base + workflow-specific overrides.
  - Base (all workflows): Cover Page → Table of Contents → Executive Summary → Scope & Methodology → Findings → Recommendations → Appendix
  - FRM override: replaces Findings with Risk Register Table + adds Heat Map section
  - Investigation override: 13-section forensic structure (see BA-R-05)
  - DD override: per-subject or consolidated subject profiles (see BA-R-06)
  - TT override: Population → Sample → Procedures → Exceptions Table → Extrapolation → Conclusions (see BA-R-07)
  - Sanctions override: Executive Summary → Screening Scope → Hits Detail → False Positives → Appendix (see BA-R-08)
- Cover page: firm logo, client name, report title, report date, confidentiality notice ("Prepared for [Client] — Confidential & Privileged")
- Header on every page: firm name + report title
- Footer on every page: page number (centred) + confidentiality label (right-aligned)
- Table of contents: auto-generated from DOCX heading styles — Heading 1 = section, Heading 2 = sub-section
- Fonts: Calibri body / Calibri Light headings (standard DOCX defaults if no template loaded)
- AI Review classifications: INTERNAL ONLY — never appear in client DOCX or MD

**Edge cases:**
- No logo path set: cover page renders without logo; no error.
- Template uploaded by consultant uses incompatible styles: BaseReportBuilder falls back to default styles; logs warning.

---

### BA-R-02 — Report Versioning
- Status: CONFIRMED (AK session 022)
- Scope: All final reports across all workflows

**Business rules:**
- Before writing a new final report, existing report moved to `{project_root}/Previous_Versions/`
- Filenames versioned: `final_report.v1.en.md`, `final_report.v2.en.md`, `final_report.v1.en.docx` etc.
- `F_Final/` (P9 projects) or `cases/{uuid}/` (legacy) always contains the LATEST version only
- `Previous_Versions/` subfolder holds all prior versions
- Version counter = count of files already in `Previous_Versions/` + 1

---

### BA-R-03 — Report Template Selection
- Status: CONFIRMED (AK session 022)
- Scope: First report generation per project (per workflow type)

**Business rules:**
- At report generation, if no template exists for this workflow type, offer two paths:
  1. "Use my own template" — `st.file_uploader` for .docx → saved to `firm_profile/templates/{workflow_type}.docx` → update firm.json
  2. "Build a template" — guided mini-wizard: firm name (pre-filled), logo path (pre-filled if set), primary colour (hex), secondary colour (hex), font choice (Calibri / Arial / Times New Roman) → generates and saves template.docx
- If template already exists for this workflow type: skip prompt, load silently
- Template path stored in `firm_profile/firm.json["templates"][workflow_type]`

---

### BA-R-04 — FRM Risk Register Enhanced Output
- Status: CONFIRMED (AK session 022)
- Scope: FRM workflow only

**Business rules:**
- Primary deliverable: DOCX with risk register as a formatted table
  - Columns: Risk ID | Risk Description | Likelihood (1–5) | Impact (1–5) | Rating (L×I) | Risk Level | Owner | Mitigation
  - Rows sorted by Rating descending
  - Heat Map section: 5×5 grid, risks plotted by Likelihood/Impact coordinates
  - Recommendations section: depth determined at intake
- Secondary deliverable: Excel (.xlsx) — same risk table + separate Heat Map sheet
  - Heat map sheet: 5×5 colour-coded grid (red ≥15, amber 8–14, green ≤7)
  - Requires `openpyxl` in requirements.txt
- Recommendation depth — asked at FRM intake:
  - "One-line actions": one sentence per risk (for internal/scoping engagements)
  - "Structured per risk" (DEFAULT): Immediate Action + Medium-Term Control + Responsible Party + Timeline
  - "Consolidated section": all mitigations in a summary section, not inline
  Default: structured. Override if scope indicates internal use only.

---

### BA-R-05 — Investigation Report Structure (Full Forensic Standard)
- Status: CONFIRMED (AK session 022)
- Scope: Investigation workflow only

**Report section order (forensic standard — fixed):**
1. Cover Page
2. Table of Contents
3. Background
4. Scope of Work
5. Note to Reader (limitations, qualifications, disclaimers)
6. Procedures Performed
7. Limitations to Procedures
8. Disclaimers
9. Evidence List (all exhibits, numbered, before Executive Summary)
10. Executive Summary
11. Detailed Findings (narrative; headers + subheaders; footnotes cite Exhibit N)
12. Appendix / Exhibits (uploaded evidence, labelled Exhibit 1, 2…)
13. Annexures (explanatory notes, schedules, third-party data)

**Detailed Findings section:**
- Evidence-led narrative: Procedure Performed → Evidence Observed → Finding → Implication → Conclusion
- Footnotes cite exhibits: "(refer Exhibit 3 — Bank Statement dated 15 Jan 2026)"
- No bare conclusions — every finding references at least one exhibit or stated procedure

**Evidence types (three source streams):**
1. Digital communications (emails, WhatsApp) — model extracts key statements with sender/recipient/date
2. Documentary / financial records — model extracts transactions, patterns, anomalies
3. Verbal statements / interviews:
   - If primary source: findings based on interviews alone; flagged as verbal evidence
   - If corroborating: interviews confirm documentary findings; quoted selectively inline

**Exhibit numbering:**
- Each uploaded document assigned sequential Exhibit number (Exhibit 1, Exhibit 2…)
- Stored in `D_Working_Papers/exhibit_register.json`
- Evidence List section auto-generated from exhibit_register.json

**Investigation Leads Register:**
- Structured register in `D_Working_Papers/leads_register.json`
- Fields: Lead ID, Description, Source, Status (Open/In Progress/Confirmed/Closed/Escalated), Evidence Found, Linked Finding ID
- When lead marked Confirmed: Haiku generates a draft finding narrative; appended to Working Papers
- Open leads at Final Run: listed in report as "Matters Requiring Further Investigation"

---

### BA-R-06 — Due Diligence Report Structure
- Status: CONFIRMED (AK session 022)
- Scope: DD workflow only

**Business rules:**
- At intake: "How many subjects?" + "Are they related?"
  - Single subject OR unrelated multiple: per-subject format
  - Multiple related subjects: consolidated format with Linkages Table
- Per-subject sections: Identity → Professional Background → Business Interests → Adverse Findings → Connections
- Consolidated format: same 5 elements + cross-reference Linkages Table
- Template option at intake: consultant can upload their own DD template; model calibrates to it

---

### BA-R-07 — Transaction Testing Report
- Status: CONFIRMED (AK session 022)
- Scope: TT workflow — standalone and as sub-report

**Business rules:**
- TT always produces a standalone file: `final_report_tt.en.docx` + `final_report_tt.en.md`
- When chained: standalone TT report generated + 1-page summary auto-embedded in parent report
- Sections: Executive Summary → Population Overview → Sample Selection Rationale → Testing Procedures → Exceptions Table → Extrapolation → Conclusions
- Exceptions Table exported to Excel as well (one sheet, same columns)

---

### BA-R-08 — Sanctions Screening Report
- Status: CONFIRMED (AK session 022)
- Scope: Sanctions workflow only

**Business rules:**
- Sections: Executive Summary → Screening Scope → Hits Detail (per entity) → False Positives → Appendix
- Hits Detail per entity: entity name, matching list entry, confidence level, matching criteria, disposition
- Disposition two-level:
  - Firm policy (firm_profile/sanctions_disposition_policy.json): default per confidence level
  - Per-hit consultant override in review screen: True Match / False Positive / Requires Further Investigation / Escalate
- Final disposition recorded in report and audit_log.jsonl

---

### BA-R-09 — FRM Stakeholder Input Capture
- Status: CONFIRMED (AK session 022)
- Scope: FRM workflow within Phase 9 engagement model

**Business rules:**
- Two capture modes (both in Input Session workspace):
  1. Structured form: Name, Role, Key Concern, Risk View → `D_Working_Papers/stakeholder_inputs.json`
  2. Document upload: interview notes, meeting minutes → `C_Evidence/{timestamp}/`
- Both passed to FRM pipeline context; stakeholders listed in DOCX Appendix

---

### BA-R-10 — Smart Intake Completion (AI Residual Question Pass)
- Status: CONFIRMED (AK session 022)
- Scope: All workflows — post-intake and pre-final-run

**Business rules:**
- Post-intake pass (Haiku): after intake form submit, identifies up to 3 missing/ambiguous items; asks one at a time conversationally; answers stored to `D_Working_Papers/intake_qa.json`; fully skippable
- Pre-final-run pass (Sonnet): before pipeline triggers, reviews all accumulated materials; presents 3–5 flags as warning cards; each card: "Resolve" or "Proceed anyway"; all decisions stored to `D_Working_Papers/prefinalrun_review.json`; pipeline unlocks when all cards acknowledged
- Both passes are non-blocking — consultant can skip
- Pass results injected into agent pipeline context

---

### BA-R-11 — Semantic Embeddings for Evidence Ingestion and Retrieval
- Status: CONFIRMED (AK session 022)
- Scope: All workflows — document ingestion, user review, pipeline context preparation

**Model routing rules (token efficiency):**
| Task | Model |
|------|-------|
| Document chunking + embedding | Local sentence-transformers (free, offline) |
| Per-document intake extraction | Haiku |
| User review semantic search | Local → Haiku synthesis |
| Pre-pipeline context preparation | Sonnet |
| Final report agents | Existing routing (unchanged) |

**Ingestion pipeline (on every document upload):**
1. CHUNK: ~500-token semantic chunks
2. EMBED: sentence-transformers (local, no API call)
3. INDEX: ChromaDB at `D_Working_Papers/vector_index/`
4. EXTRACT (Haiku): entities, key facts, red flags → appended to `D_Working_Papers/case_intake.md`

**Retrieval uses:**
- User review: semantic search by topic → ranked chunks with source citation
- Pipeline: Sonnet assembles targeted context per finding area from vector index

**Fallback:** If sentence-transformers not available (offline env), skip embedding; fall back to full-document context (existing behavior).

**New dependencies:** `sentence-transformers>=2.7.0`, `chromadb>=0.4.0`

---

## Session 024 BA — Sprint-EMB + Phase 9 Schemas + New Workflow Designs (2026-04-19)

---

### BA-P9-01 — ProjectIntake Schema Requirements
- Status: DRAFT
- Scope: `schemas/project.py` — ProjectIntake model; slug derivation and path-traversal guard (R-019)

**User outcome:** Maher names an engagement in plain language ("GiveBrite DD") and the system creates a safe, predictable filesystem path for it — with no risk of accidental file writes outside the `cases/` directory.

**Business rules:**
  - `project_name`: free-text string, 1–80 chars. Required. No validation on content — Maher can name projects however he likes.
  - `project_slug`: derived automatically from `project_name` at validation time (not stored separately by the user — it is a computed field):
    1. Lowercase the entire string
    2. Replace all whitespace sequences with a single hyphen
    3. Strip all characters that are not `[a-z0-9-]`
    4. Collapse consecutive hyphens to one
    5. Strip leading and trailing hyphens
    6. If the result is empty after stripping: raise `ValueError("project_name produces an empty slug — please provide at least one alphanumeric character")`
    7. Enforce maximum slug length of 60 chars (truncate before stripping trailing hyphen)
  - Path-traversal guard (R-019 — mandatory, non-negotiable): before any filesystem write, `project_slug` must be re-validated against a strict allowlist pattern `^[a-z0-9][a-z0-9-]{0,58}[a-z0-9]$` (or single char `^[a-z0-9]$`). If it fails: raise `ValueError` — do not create any directory.
  - Additionally: reject slugs that are or contain `.`, `..`, `/`, `\`, `~`, `$`, `%`, null bytes, or any Unicode character outside ASCII. These are blocked at validation, not just stripped — if the source string contains them after slugification, it means the slug is too aggressively sanitised and the name is ambiguous. Raise a clear error prompting Maher to rename.
  - `service_type`: one of the confirmed GoodWork workflow identifiers (e.g. `investigation_report`, `frm_risk_register`, `due_diligence`, `sanctions_screening`, `transaction_testing`, `policy_sop`, `training_material`, `client_proposal`). Required.
  - `created_at`: UTC datetime, set at intake.
  - `primary_jurisdiction`: string, default `"UAE"`.
  - `operating_jurisdictions`: list of strings, default `["UAE"]`.
  - `language_standard`: one of `["acfe_internal", "expert_witness", "regulatory_submission", "board_pack"]`, default `"acfe_internal"` (per BA-P9-05).
  - `client_name`: string, required. Used for cover page and context only — not part of slug derivation.
  - `industry`: string, optional. Pre-populated via taxonomy picker if available.
  - `language`: `"en"` or `"ar"`, default `"en"`.
  - `engagement_letter_registered`: bool, default `False`. Set to `True` when `register_engagement_letter()` is called on this project. Pipeline cannot run until this is `True` (existing gate, carried forward).
  - Slug collision detection: before creating the project directory, check whether `cases/{slug}/` already exists. If it does: surface to Maher — "A project at `cases/{slug}/` already exists. Open it or choose a different name?" Do not silently overwrite.
  - Backward compatibility: existing `CaseIntake` UUID-based cases are not affected. `ProjectIntake` is additive — both models coexist. `CaseTracker` renders both.

**Edge cases:**
  - `project_name` is entirely non-ASCII (e.g. Arabic): slug becomes empty after stripping → raise `ValueError` with message "Project name must contain at least one Latin alphanumeric character for the filesystem path. Please provide a short English identifier."
  - `project_name` is a single space or only special chars: same as above.
  - Two different project names produce the same slug (e.g. "GiveBrite DD" and "GiveBrite-DD"): collision detected at filesystem check; Maher prompted to distinguish them.
  - Maher provides a name with `../` in it (deliberate or accidental): stripped during slug derivation; but the path-traversal guard validates the final slug independently and would catch any residual traversal patterns.

**Out of scope:** Slug validation of `client_name` (used for display only, never written to filesystem directly). Renaming a project after creation (no rename workflow in v1).

**Open questions for AK:**
  - Should `service_type` be set at project creation, or can a project be created without a service type and have it selected at first final run? (Matters for whether `ProjectIntake` has `service_type` as required or optional.)
  - Should a single project support multiple service types simultaneously (e.g. DD + Sanctions on the same project), or is it always one service type per project slug? The BA-P9-01 session decision said same project_name + same service_type = same folder, implying service_type is part of the key — clarify whether the slug encodes the service type.

---

### BA-P9-02 — InputSession Schema Requirements
- Status: DRAFT
- Scope: `schemas/project.py` — InputSession model; lifecycle states from creation through final-run trigger

**User outcome:** Every time Maher opens a project to add materials (without running the pipeline), a session record is created automatically. He can see a history of what was added in each session and when.

**Business rules:**
  - `InputSession` represents one working session where Maher adds materials to a project but does not trigger the AI pipeline. It is NOT a pipeline run — it is a pre-pipeline accumulation record.
  - Fields:
    - `session_id`: UUID4, generated at session start.
    - `project_slug`: FK to `ProjectIntake.project_slug`. Required.
    - `session_type`: `Literal["input", "final_run"]`. Set at session start. An `input` session adds materials; a `final_run` session triggers the pipeline.
    - `started_at`: UTC datetime.
    - `ended_at`: UTC datetime, optional. Set when session is explicitly closed or when `session_type == "final_run"` completes.
    - `documents_added`: list of `doc_id` strings (registered via `DocumentManager` during this session).
    - `notes_added`: list of note file paths written during this session (relative to project root).
    - `key_facts_added`: integer count of new key facts appended to `key_facts.json` during this session.
    - `red_flags_added`: integer count of new red flags appended to `red_flags.json` during this session.
    - `pipeline_triggered`: bool, default `False`. Set `True` when `session_type == "final_run"` and pipeline is actually invoked.
    - `pipeline_run_id`: optional string, populated when pipeline is triggered. References the orchestrator run record.
    - `status`: `Literal["open", "closed", "pipeline_complete", "pipeline_failed"]`.
  - Lifecycle:
    1. `open` — session created; Maher is actively working. Materials added here are logged.
    2. `closed` — input session ended without pipeline trigger. All materials persisted. Session can be resumed (creates a new `InputSession`, not reopens the old one).
    3. `pipeline_complete` — `final_run` session; pipeline ran to completion.
    4. `pipeline_failed` — `final_run` session; pipeline failed before completion. Error stored in associated `CaseState.error`.
  - Session log persistence: each `InputSession` is serialised to `A_Engagement_Management/session_log.jsonl` (append-only, one line per session close event). This is distinct from `audit_log.jsonl` which records agent-level events.
  - Auto-save on close: if Maher closes the app without explicitly ending the session, the session is auto-saved with `status = "closed"` and `ended_at = now()`. Unsaved text notes are flushed to `D_Working_Papers/session_notes_{YYYYMMDD_HHMMSS}.md` before close.
  - Transition to formal Case: when `pipeline_triggered = True`, the orchestrator creates a `CaseState` object with a new `case_id` (UUID format) linked to the `project_slug`. The `InputSession` becomes the provenance record for that case run. Multiple `final_run` sessions can exist for the same project (e.g. first run produces a draft; Maher adds more documents and runs again — second `final_run` session, new `CaseState`).
  - A project can have many `InputSession` records. The most recent `final_run` session with `pipeline_complete` is the "current version" of the project.

**Edge cases:**
  - App crash during an `open` session: on next launch, detect `open` sessions in `session_log.jsonl`. Offer to review what was added. Session status updated to `closed` with a `crash_recovery` flag.
  - `final_run` session with `pipeline_failed`: session status set to `pipeline_failed`. Maher can retry — creates a new `final_run` session (does not reopen the failed one). All materials from prior sessions remain accumulated.
  - Maher opens a `final_run` session but decides not to trigger: allowed. `session_type` can be changed before pipeline trigger. Ends as `closed`.
  - Zero materials in project, `final_run` attempted: blocked with warning (BA-P9-01 edge case carried forward). Maher must acknowledge "zero-information baseline only" before proceeding.

**Out of scope:** Session sharing between users. Real-time sync of session state to cloud. Session comments or annotations on individual documents within the session record (those go in notes).

**Open questions for AK:**
  - Should `InputSession` be visible in the Streamlit UI as a history tab, or is it purely a machine record for resumability and audit? (Affects whether it needs display fields like `session_title` or `summary`.)
  - When a `final_run` session completes, should the previous pipeline outputs (E_Drafts/) be automatically versioned, or does Maher manually trigger versioning? (Relates to BA-R-02.)

---

### BA-P9-03 — ProjectState Schema Requirements
- Status: DRAFT
- Scope: `schemas/project.py` — ProjectState model; relationship to existing `CaseState`

**User outcome:** Maher can see the full status of a named project — how many sessions it has had, which pipeline runs have completed, which are in progress, and what the overall project health is — without having to cross-reference multiple JSON files manually.

**Business rules:**
  - `ProjectState` is the project-level aggregation over one or more `CaseState` records and multiple `InputSession` records. It does NOT replace `CaseState` — it wraps it.
  - Fields:
    - `project_slug`: string. Primary key. Must match `ProjectIntake.project_slug`.
    - `project_name`: string. Display name (denormalised from `ProjectIntake` for convenience).
    - `service_type`: string. From `ProjectIntake`.
    - `created_at`: UTC datetime.
    - `last_updated`: UTC datetime. Updated on every input session close and every pipeline state transition.
    - `total_input_sessions`: integer. Count of all `InputSession` records for this project.
    - `total_pipeline_runs`: integer. Count of all `CaseState` records linked to this project.
    - `latest_case_id`: optional string. The `case_id` of the most recent pipeline run (most recent `CaseState`).
    - `latest_pipeline_status`: optional `CaseStatus`. Denormalised from the most recent `CaseState.status`.
    - `latest_final_report_path`: optional string. Relative path to the most recent final report (`.docx` or `.md`). Populated by post-hook `persist_artifact`.
    - `document_count`: integer. Total documents registered across all sessions. Sourced from `DocumentIndex`.
    - `has_engagement_letter`: bool. Denormalised from `ProjectIntake.engagement_letter_registered`.
    - `language_standard`: string. From `ProjectIntake`.
    - `case_ids`: list of strings. All `case_id` values linked to this project (all pipeline runs, in chronological order).
    - `project_health`: `Literal["no_materials", "materials_only", "pipeline_running", "draft_ready", "final_approved", "error"]`. Computed field — not stored by Maher, derived at read time:
      - `no_materials` — project created, zero documents, zero notes
      - `materials_only` — documents/notes present, no pipeline run yet
      - `pipeline_running` — a `CaseState` with non-terminal status exists
      - `draft_ready` — latest `CaseState.status` is `PARTNER_REVIEW_COMPLETE` or `OWNER_READY`
      - `final_approved` — latest `CaseState.status` is `OWNER_APPROVED` or `DELIVERABLE_WRITTEN`
      - `error` — latest `CaseState.status` is `PIPELINE_ERROR`
  - Persistence: `ProjectState` is serialised to `cases/{project_slug}/project_state.json`. This file is the single source of truth for the project-level status that the Case Tracker reads.
  - Update triggers: `ProjectState` is updated (recomputed + overwritten atomically) after:
    1. Any `InputSession` closes
    2. Any `CaseState` transition (hooked via `post_hooks.append_audit_event`)
    3. Any document registration
  - Relationship to `CaseState`: one project → many `CaseState` records. Each `CaseState` has a `case_id` (UUID) and a `project_slug` field (new field to add to `CaseState`). `ProjectState.case_ids` lists all of them.
  - Case Tracker rendering: Case Tracker reads `project_state.json` for new-format projects. For legacy UUID cases (no `project_state.json`), it reads `state.json` directly. Both paths must produce a renderable row in the tracker table.
  - Audit trail: `audit_log.jsonl` at the project root records all events across all pipeline runs in this project. It is project-scoped, not case-scoped, in the new model.

**Edge cases:**
  - Project with no pipeline runs: `latest_case_id = None`, `latest_pipeline_status = None`, `project_health = "materials_only"` (or `"no_materials"` if nothing uploaded).
  - Pipeline run fails and Maher retries: `case_ids` has two entries; `latest_case_id` points to the retry; `latest_pipeline_status` reflects the retry's current status.
  - `project_state.json` is missing but project folder exists (e.g. manual creation or corruption): Case Tracker detects missing file, logs a warning, renders the row with `project_health = "error"` and a "Repair" action that regenerates `project_state.json` from existing `state.json` and `document_index.json`.
  - Legacy UUID case opened: no `ProjectState` for it. Case Tracker renders it directly from `state.json`. No migration required.

**Out of scope:** Cross-project aggregation (no firm-level summary schema in v1). Project archiving or deletion. `ProjectState` as a user-editable file (it is machine-written only).

**Open questions for AK:**
  - Should `CaseState` gain a `project_slug` field in this sprint, or is the link maintained only in `ProjectState.case_ids`? (Bidirectional link vs one-directional.) Architect preference affects schema diff.
  - Should `project_health` be a computed Pydantic property (derived at model construction) or a stored field updated by hooks? Stored is more resilient across restarts; computed is always fresh. Trade-off is resumability vs consistency.

---

### BA-EMB-01 — EmbeddingEngine Business Rules
- Status: DRAFT
- Scope: `tools/embedding_engine.py` — EmbeddingEngine class; wiring into `DocumentManager.register_document()`

**User outcome:** When Maher uploads a document, it is automatically embedded so that later, when the AI pipeline drafts findings, it can retrieve only the relevant 3–5 chunks for each finding area — instead of forcing the full document into every agent call.

**Business rules:**

**When to embed:**
  - Embedding runs as a step inside `DocumentManager.register_document()`, after text extraction and section indexing, before returning the `DocumentEntry`.
  - Embedding is always async from the user's perspective — it must not block the "document registered" confirmation Maher sees. Implementation: run embedding synchronously but after the index save, so the UI is unblocked.
  - Only embed documents where text extraction succeeded. If `text == "[EXTRACTION FAILED: ...]"`, skip embedding and log a warning to `audit_log.jsonl`.
  - Duplicate documents (detected by hash): do not re-embed. The existing vector entries are still valid.

**Chunking rules:**
  - Target chunk size: 500 tokens (~2,000 chars). Use a sliding window with 10% overlap (~50 tokens) to preserve context across chunk boundaries.
  - Split on sentence boundaries where possible (do not cut mid-sentence). Fallback: split on paragraph breaks. Final fallback: hard split at char limit.
  - Each chunk carries metadata: `doc_id`, `project_slug`, `case_id`, `chunk_index` (integer), `section_id` (from `DocumentSection` if available), `filename`, `source_excerpt` (first 100 chars of chunk for display in search results).
  - Minimum chunk size: 100 chars. Chunks shorter than this are merged into the previous chunk.
  - Excel files: each sheet is treated as a separate chunk group. Row data is chunked by row batches (50 rows per chunk) rather than by character count.

**Model and index:**
  - Embedding model: `all-MiniLM-L6-v2` (default sentence-transformers model, ~80MB download). This model downloads automatically on first use via `sentence-transformers` library. The download is ~90MB and requires internet connectivity.
  - Vector store: ChromaDB, persistent collection at `cases/{project_slug}/D_Working_Papers/vector_index/` (P9 projects) or `cases/{case_id}/vector_index/` (legacy).
  - Collection name: `case_{project_slug}` (or `case_{case_id}` for legacy). One collection per project.
  - Each document adds its chunks to the project's shared collection — not a separate collection per document.

**Fallback behaviour (R-NEW-07 — mandatory):**
  - On `EmbeddingEngine` instantiation: attempt to import `sentence_transformers` and `chromadb`. If either import fails: set `self.available = False`. Log once to stderr: "sentence-transformers or chromadb not available — falling back to full-document context". Do not raise an exception.
  - If `self.available = False`: `embed_document()` is a no-op. `retrieve_chunks()` returns `None`. Callers must check the return value and fall back to full-document reading via `DocumentManager`.
  - If model download fails (network unavailable): catch the download exception, set `self.available = False` with the same fallback behaviour. Log: "sentence-transformers model download failed — offline mode detected, falling back to full-document context".
  - Fallback is silent to Maher — he should never see an error from the embedding system. It either works or it does not; the pipeline continues either way.
  - `DocumentEntry` gains an `embedding_status` field: `Literal["embedded", "skipped_extraction_failed", "skipped_fallback", "pending"]`. Set at registration. Used by pipeline to decide retrieval strategy.

**Retrieval contract — what the agent receives:**
  - Entry point: `EmbeddingEngine.retrieve_chunks(query: str, project_slug: str, n_results: int = 5, doc_ids: list[str] | None = None) -> list[ChunkResult] | None`
  - Returns `None` if `self.available = False` (caller falls back to full-document context).
  - `ChunkResult` fields: `chunk_text` (the chunk), `doc_id`, `filename`, `section_id` (optional), `chunk_index`, `distance` (ChromaDB cosine distance), `source_citation` (formatted string: `"{filename} — {section_title or 'Section unknown'}, chunk {chunk_index}"`).
  - Results are ranked by distance (ascending — lower = more similar). Top `n_results` returned.
  - Optional `doc_ids` filter: restricts retrieval to chunks from specified documents only (for when the pipeline knows which documents are relevant).
  - Maximum total chars returned across all chunks: 8,000 chars (configurable via `config.EMBEDDING_RETRIEVE_MAX_CHARS`). If top-N chunks exceed this limit, truncate the lowest-ranked chunks (not the text within a chunk — drop whole chunks).
  - Agent-facing context format: the pipeline wraps `ChunkResult` list into a formatted context block before injecting into the agent prompt:
    ```
    [RELEVANT EVIDENCE — retrieved from vector index]
    Source: {source_citation}
    ---
    {chunk_text}
    ---
    [END EVIDENCE BLOCK]
    ```
  - Provenance preserved: `source_citation` is included so the agent can attribute findings to the correct document and section.

**What gets indexed:**
  - All document types that produce extractable text: `.txt`, `.md`, `.pdf`, `.docx`, `.csv`, `.eml`, `.msg`.
  - Excel (`.xlsx`, `.xls`): indexed in row-batch chunks (see chunking rules above).
  - Engagement letter: indexed like any other document — no special exemption.
  - Documents where extraction fails (`[EXTRACTION FAILED: ...]`): not indexed. `embedding_status = "skipped_extraction_failed"`.

**Edge cases:**
  - Empty document (zero chars after extraction): `embedding_status = "skipped_extraction_failed"`. No chunks created. No error raised.
  - Very short document (<100 chars total): treated as a single chunk. Embedded as-is.
  - Collection already exists when re-registering after crash: ChromaDB `get_or_create_collection` handles idempotency. Duplicate chunk detection: check by `doc_id + chunk_index` metadata before inserting.
  - Project has many documents and vector index grows large: no size cap in v1. Flag as a future concern if index exceeds 1GB.
  - `n_results` requested is larger than total chunks in collection: return all available chunks. No error.

**Out of scope:** Fine-tuning or custom embedding models. Per-agent embedding collections. Cross-project retrieval. Hybrid BM25 + vector search (v1 vector only).

**Open questions for AK:**
  - Should the embedding step happen synchronously inside `register_document()` (adds latency per upload but keeps things simple) or asynchronously in a background thread (faster UX but adds complexity)? Given Streamlit's threading model, async is non-trivial. BA recommendation: synchronous in v1, with a spinner shown while embedding runs.
  - Should `retrieve_chunks()` be exposed as a tool that agents can call themselves (tool_use loop), or should the orchestrator pre-fetch chunks before invoking each agent? BA recommendation: orchestrator pre-fetches once per finding area and injects as context — cleaner than giving agents a retrieval tool.

---

### BA-WORK-01 — Interim Workpaper Generation
- Status: CONFIRMED — 2026-04-19 (AK answered all 3 questions)
- Scope: NEW DESIGN — mid-engagement workpaper as a named deliverable, available inside the Input Session workspace

**AK decisions (2026-04-19):**
- Trigger: available at ANY point after Junior draft exists — mid-pipeline OR post-pipeline. Maher has full control.
- Structure: Maher-driven at generation time. Generator presents each of the 9 sections as opt-in/opt-out, asks if anything additional is needed. Fixed structure rejected — Maher configures per workpaper.
- Promotion: workpapers CAN be promoted to final reports. Maher reviews, confirms, system applies full report template, writes to `F_Final/` with `PROMOTED_FROM_WORKPAPER` flag in audit_log.

**User outcome:** Partway through an engagement, Maher can generate a professional interim workpaper that documents what has been found so far — structured finding notes, open questions, evidence references, and a status summary. This is NOT a final report. It is an internal document that keeps the engagement organised and can be shared with a supervisor, co-consultant, or used as a progress memo to the client.

**Background (domain context):** In physical forensic engagements, consultants maintain working papers throughout — structured notes on what has been reviewed, what findings are emerging, what questions remain open. These are the audit trail between "raw evidence" and "final report". A sole practitioner like Maher currently has no structured way to capture this mid-engagement state in the tool. Without it, he either keeps informal notes outside the tool (breaking the audit trail) or waits until the full pipeline run to see any structured output.

**Business rules:**

**Trigger:**
  - Available from the Input Session workspace, from the moment at least one document is registered and at least one session note or key fact has been added. Not available on a zero-material project.
  - Triggered manually by Maher: "Generate Interim Workpaper" button in the Streamlit workspace sidebar. Never auto-triggered.
  - Can be generated multiple times. Each generation creates a new versioned file (`D_Working_Papers/interim_workpaper.v1.md`, `v2`, etc.). Previous versions are preserved, not overwritten.
  - Does NOT require the full 3-agent pipeline. It is a single-agent (Sonnet) generation, much faster (~30 seconds target).

**What goes in an interim workpaper:**
  1. **Header**: Project name, client name, engagement type, date generated, "PRELIMINARY — NOT FOR DISTRIBUTION" watermark (in the DOCX header and MD front-matter).
  2. **Materials reviewed to date**: auto-generated from `DocumentIndex` — list of all registered documents with brief summary of each (from `DocumentEntry.summary`).
  3. **Key facts established**: pulled from `D_Working_Papers/key_facts.json` — formatted as a numbered list with source attribution.
  4. **Red flags identified**: pulled from `D_Working_Papers/red_flags.json` — formatted by severity (high → medium → low). Each red flag includes source and action status.
  5. **Emerging findings** (Sonnet-generated): model reviews accumulated materials (via embedding retrieval if available, else full-document) and drafts 3–7 emerging finding narratives. Each finding: title, evidence observed so far, implication (tentative), open questions to confirm or refute. Language standard: ACFE Internal Review regardless of project setting (workpapers are always internal). All findings labelled "PRELIMINARY — subject to further investigation".
  6. **Leads register status**: pulled from `D_Working_Papers/leads_register.json` — open leads listed with current status. Confirmed leads flagged as likely to be in final report.
  7. **Matters pending / open questions**: compiled from `open_questions` in emerging findings + open leads + any unanswered items from `D_Working_Papers/intake_qa.json`.
  8. **Next steps**: Sonnet proposes 3–5 specific next steps based on open questions and red flags. Maher can edit these before saving.
  9. **Audit trail summary**: count of sessions, documents registered, facts recorded — a one-line status.

**Generation pipeline:**
  - Single agent: Sonnet (not the full Junior → PM → Partner chain).
  - Model is explicitly instructed: "This is a preliminary internal workpaper. Do not present findings as conclusions. Use qualified language throughout ('evidence suggests', 'it appears', 'further review required'). Every finding must reference at least one registered document by filename."
  - No PM or Partner review step. Maher reviews the output directly.
  - Language standard injection: ACFE Internal Review, hardcoded for workpapers (not overridable).
  - Output formats: `.md` only (no DOCX for workpapers — internal document, not client-facing). Saved to `D_Working_Papers/interim_workpaper.v{N}.md`.
  - Workpaper generation does NOT transition `CaseState`. It is not a pipeline event. It does NOT write to `E_Drafts/` or `F_Final/`.
  - Audit log entry: `append_audit_event` records a `WORKPAPER_GENERATED` event (new event type) with version number and Sonnet model used.

**Evidence chain enforcement:**
  - Every emerging finding must cite at least one `DocumentEntry` by `doc_id` and `filename`. If no supporting evidence exists in the registered materials, the finding must be labelled "ANALYTICAL INFERENCE — no documentary evidence found yet".
  - Findings labelled ANALYTICAL INFERENCE are highlighted in the output with a warning: "This observation is based on the model's analysis of the client/industry context, not on a registered document. Do not include in final report without documentary support."
  - This is how workpapers differ from the full pipeline: the evidence chain is tracked but the bar is lower — provisional findings with explicit provenance labels are acceptable here, whereas the Partner agent would reject them.

**Edge cases:**
  - No documents registered yet: "Generate Interim Workpaper" is greyed out with tooltip "Upload at least one document to generate a workpaper."
  - Only engagement letter registered (no substantive evidence): workpaper can still be generated. Sections 3–6 will be sparse; model notes this explicitly in the output.
  - Workpaper generated, then more documents uploaded, then workpaper generated again: both versions preserved. Version history shown in sidebar. Maher can compare.
  - Workpaper content conflicts with later final report (common — findings evolve): workpapers are explicitly internal. The DOCX header "PRELIMINARY — NOT FOR DISTRIBUTION" is the control. No reconciliation logic needed between workpaper and final report.
  - Maher wants to share the workpaper with a client: the tool does not prevent it, but the "PRELIMINARY — NOT FOR DISTRIBUTION" header is always present. If Maher wants a client-facing interim memo, he should run the full pipeline (which has the Partner review gate).

**Out of scope:** Workpaper → final report auto-merge (promotion is manual, not automatic). Workpaper review by a separate agent (one-pass Sonnet, reviewed by Maher). Workpapers for Mode B workflows (Proposal, Policy, Training — one-pass, no workpaper needed).

**Open questions for AK:** None — all resolved 2026-04-19.

---

### BA-CONV-01 — Conversational Evidence Mode
- Status: CONFIRMED — 2026-04-19 (AK answered placement and scope questions)
- Scope: NEW DESIGN — exploratory conversation mode over registered case documents; distinct from the pipeline and from general chat

**AK decisions (2026-04-19):**
- Placement: persistent collapsible chat panel available on ALL engagement pages (not standalone page, not tab). Single shared component injected via bootstrap(). Opens against current case_id context. Premium feel — always present, never intrusive.
- Entry point: chat icon / "Ask AI" tab on right edge of every engagement page. Slides open as a panel over content without navigation.

**User outcome:** Maher can open a registered case document and have a back-and-forth conversation with the model about it — asking "What does this email chain say about the approval process?", "Does this transaction pattern suggest structuring?", "Flag anything suspicious in pages 12–18" — without triggering the full pipeline. The conversation is saved as a working paper, so leads and observations from the conversation are not lost.

**Background (domain context):** Evidence review in forensic work is non-linear. A consultant reads a bank statement, notices an anomaly, asks a question, follows a thread, backtracks, re-reads a different document. The current pipeline model forces a linear flow: ingest → pipeline run → review output. That is the right model for final deliverables. But it is the wrong model for discovery. Discovery is conversational. The gap is: Maher currently has no way to have that conversational exploration within the tool, with the output preserved as case evidence.

**Business rules:**

**When it is available:**
  - Conversational Evidence Mode (CEM) is available in the Input Session workspace for any project that has at least one document registered.
  - Entry point: "Explore Documents" or "Evidence Chat" button in the Streamlit workspace sidebar.
  - Available at any time during the project lifecycle — before, during, and after pipeline runs. It is independent of pipeline state.

**How it differs from a pipeline run:**
  - CEM is NOT a pipeline run. It does not create a `CaseState`. It does not trigger Junior, PM, or Partner agents. It does not write to `E_Drafts/` or `F_Final/`.
  - CEM is NOT general chat. The model is strictly scoped to the registered documents of this project. It may not introduce external knowledge as findings — only as context ("this pattern is consistent with a structuring scheme, which is a form of AML…"). External knowledge as explanation is allowed; external knowledge as evidence is not.
  - The model in CEM operates as a "document assistant", not as a drafting agent. It surfaces, quotes, and explains what is in the documents. It does not draft findings or conclusions.

**Conversation mechanics:**
  - Model used: Sonnet (for analytical depth; Haiku is insufficient for multi-document evidence reasoning).
  - System prompt for CEM: "You are reviewing the documents registered for this forensic engagement. You can only present findings and observations that are directly supported by the registered documents. For each observation, state the source document and quote the relevant passage. You may explain forensic concepts, fraud patterns, and regulatory context as background. You must not present inferences as conclusions. All observations are preliminary."
  - Context injection: at conversation start, the model receives:
    1. `DocumentIndex` summary (all registered documents: filename, doc_type, brief summary).
    2. `key_facts.json` and `red_flags.json` (accumulated context from prior sessions).
    3. The first user message.
  - On each user turn: if the query references specific content (e.g. "look at the bank statement"), `EmbeddingEngine.retrieve_chunks()` is called with the user query to fetch relevant chunks. Chunks are injected as context before the model responds. If embedding is unavailable: `DocumentManager.find_relevant_docs()` is used to identify relevant documents, and `read_excerpt()` is used to retrieve content.
  - Document-specific conversations: Maher can say "focus on [filename]" — all subsequent retrieval is filtered to that `doc_id`.
  - Multi-document reasoning: Maher can ask "compare the vendor list in the PO register with the vendor list in the payment run" — model retrieves from both documents and reasons across them.
  - No context window per turn limit is imposed by CEM, but total injected context per turn (chunks + conversation history) is capped at `config.CEM_CONTEXT_CHARS` (default: 16,000 chars). Oldest conversation turns are dropped first when this limit is approached (sliding window on conversation history).

**State saving — what gets preserved:**
  - CEM conversation persistence: the full conversation (user turns + model turns) is saved to `D_Working_Papers/evidence_chat_{YYYYMMDD_HHMMSS}.md` on session close. Append-only. Each new CEM session in the same project creates a new file.
  - Lead capture: during the conversation, Maher can click "Save as Lead" on any model response. This extracts the model's observation and appends it to `D_Working_Papers/leads_register.json` with:
    - `source: "evidence_chat"`, `session_file: "evidence_chat_{timestamp}.md"`, `status: "Open"`, `description`: the model's observation text.
  - Key fact capture: Maher can click "Save as Key Fact" on any model response. Appends to `D_Working_Papers/key_facts.json` with `source_doc_id` and `source_excerpt` from the chunk that generated the observation.
  - Red flag capture: same mechanism — "Save as Red Flag" button on model responses.
  - All saved leads, facts, and red flags from CEM are then available in the Input Session workspace and are passed to the pipeline on the next Final Run.
  - Conversation is NOT automatically converted into a pipeline input. Maher explicitly promotes observations by clicking "Save as Lead/Fact/Red Flag". Unsaved observations are in the chat transcript only.

**Evidence chain integrity:**
  - Every model response in CEM that makes an evidentiary observation must include a source attribution inline: "(Source: {filename}, {section or chunk reference})". Model is instructed to do this in the system prompt.
  - Model may NOT make an evidentiary observation if no registered document supports it. If asked "Do you think there's fraud here?", model responds: "Based on the documents registered so far, I can note the following observations…" and lists only document-supported items.
  - CEM conversations are stored but are NOT part of the formal audit trail (`audit_log.jsonl`). They are working materials. The formal audit trail event is only written when a Lead, Key Fact, or Red Flag is saved from the conversation.

**Session management:**
  - CEM session starts when Maher opens the "Explore Documents" view.
  - CEM session ends when Maher closes the view or explicitly clicks "End Conversation".
  - On session end: conversation saved to `D_Working_Papers/evidence_chat_{timestamp}.md`. Summary of leads/facts/flags saved during the session shown to Maher before close.
  - Conversation history is NOT loaded on next CEM session start (each conversation starts fresh). Prior conversations are accessible as read-only files in the Working Papers view.

**Edge cases:**
  - Maher asks about a document that has not been registered: model responds "I don't have access to that document. Please register it in the Evidence folder first."
  - Maher asks a general knowledge question unrelated to the case: model responds in context ("In the context of this engagement…") and directs back to the registered documents. It does not refuse, but it also does not provide general advice detached from the case.
  - Very long conversation (>50 turns): oldest turns are dropped from context (sliding window). A banner warns Maher when history is being trimmed. Full transcript is still preserved in the saved file.
  - Maher closes the app mid-conversation without ending the session: auto-save to `D_Working_Papers/evidence_chat_{timestamp}_recovered.md`. Any leads/facts/flags already clicked "Save" on are preserved in the JSON files (they are saved on click, not on session close).
  - Model produces a response that Maher believes misquotes the document: Maher can click "Flag Response" — this appends a `FLAGGED` annotation to the conversation transcript. Flagged responses are not saved as leads/facts. No further automated action.
  - Embedding unavailable (fallback mode): CEM still works via keyword search + excerpt. Performance degrades — model receives less targeted context. Banner shown: "Semantic search unavailable — using keyword matching. Results may be less precise."

---

## Session 024 — Report Templates & Config

### BA-TPL-01 — Report Template Management System
- Status: DRAFT
- Scope: Settings → Templates tab; `firm_profile/templates/` directory; `update_report_template` tool; `OutputGenerator.generate_docx()` fallback logic

**User outcome:** Maher can manage branded Word templates per workflow type from the Settings page. Base templates are pre-installed and always present as a fallback. Uploading a custom template overrides the base for that workflow type without deleting it.

**Business rules:**
  - One template slot per workflow type. Supported workflow types: `frm_risk_register`, `investigation_report`, `client_proposal`, `due_diligence`, `sanctions_screening`, `transaction_testing`, `workpaper`.
  - Base templates ship with the product as `firm_profile/templates/{workflow_type}_base.docx`. They are read-only — never deletable and never overwritten by an upload. They serve as permanent fallback.
  - Custom templates are stored as `firm_profile/templates/{workflow_type}_custom.docx`. Uploading a new custom template for a workflow type that already has one triggers versioning before saving: the existing `_custom.docx` is renamed to `{workflow_type}_custom.v{N}.docx` where N is the next available integer. The new file is then saved as `_custom.docx`.
  - The Settings page exposes a **Templates** tab. For each workflow type, the tab shows: (a) whether a custom template exists, (b) the version history (list of `_custom.v{N}.docx` files), and (c) an upload control to replace the current custom template.
  - Upload is handled via the `update_report_template(workflow_type: str, file_bytes: bytes)` AI tool call. The tool: (1) validates the file is a valid .docx (magic bytes check), (2) checks file size ≤ 5 MB, (3) opens the file with `python-docx` and extracts named paragraph styles, (4) verifies that all seven required styles are present: `GW_Title`, `GW_Heading1`, `GW_Heading2`, `GW_Body`, `GW_TableHeader`, `GW_Caption`, `GW_Disclaimer`, (5) if valid, rotates the existing custom template (versioning step above), then saves the new file.
  - `OutputGenerator.generate_docx()` resolves the template path at generation time: checks for `{workflow_type}_custom.docx` first; if absent or if the file is unreadable, falls back to `{workflow_type}_base.docx`. The resolution is logged to audit_log as `{event: "template_resolved", template: "<filename>", fallback: true/false}`.
  - If `_custom.docx` exists but is missing one or more required named styles at generation time, `OutputGenerator` falls back to the base template and logs a warning: `{event: "template_fallback", reason: "missing_required_styles", missing: [...], fallback_to: "{workflow_type}_base.docx"}`.
  - Template versioned history is retained indefinitely (no auto-purge). Maher can download any version from the Templates tab but cannot re-activate a past version directly — they must re-upload it.

**Edge cases:**
  - Upload is not a valid .docx (e.g. a .pdf or a renamed file): tool returns error `"invalid_file_type"`. No file is saved. UI shows: "File must be a valid .docx document."
  - File exceeds 5 MB: tool returns error `"file_too_large"`. No file is saved. UI shows: "Template file must be under 5 MB."
  - File is a valid .docx but is corrupted (python-docx raises on open): tool returns error `"file_corrupted"`. No file is saved. UI shows: "The uploaded file could not be read. Please check the file and try again."
  - One or more required named styles are missing: tool returns error `"missing_required_styles"` with a list of the missing style names. No file is saved. UI shows the list so Maher can correct the template in Word before re-uploading.
  - `firm_profile/templates/` directory does not yet exist at upload time: tool creates it before saving.
  - Base template file is missing from the install (e.g. corrupted install): `OutputGenerator` raises a hard error and surfaces it to Maher in the UI. Generation is blocked until the base template is restored.
  - Maher uploads the same file a second time (identical bytes): tool still proceeds normally — versioning runs, a new `_custom.docx` is saved, and the previous one is versioned. No de-duplication check.

**Out of scope:** PPTX template management (separate feature, not in this sprint). Multi-user template sharing or a cloud template library. In-app template editing or style management (Maher edits templates in Microsoft Word externally). Automated style injection (tool does not add missing styles — it rejects uploads that lack them).

**Open questions for AK:**
  - Should the Templates tab show a preview thumbnail of the first page of each template, or is a filename + upload-date listing sufficient for v1?
  - Do versioned templates (`_custom.v{N}.docx`) need a UI to download them, or is access via the file system acceptable for now?
  - Should `GW_Disclaimer` be mandatory for all workflow types, or only for investigation_report and sanctions_screening? Some workflows (e.g. training_material) may not have a disclaimer section.

---

### BA-TPL-02 — Engagement-Time Template Selection
- Status: DRAFT
- Scope: Intake UI (Zone A, all workflow types); case `state.json`; audit_log; one-time upload flow

**User outcome:** At the start of every engagement, Maher is explicitly asked which report template to use before the pipeline runs. There is no silent default. The choice is recorded in the case state and audit trail.

**Business rules:**
  - The template selector is the last item rendered in Zone A (intake) for every workflow type, immediately before the Run button. It is never hidden or auto-skipped.
  - The selector presents up to three options, depending on what templates exist for the workflow type:
    - **(a) Global saved template** — shown only if `{workflow_type}_custom.docx` exists in `firm_profile/templates/`. Label: "Use saved template: {workflow_type}_custom.docx (uploaded {date})". This option is pre-selected by default when available.
    - **(b) One-time upload for this engagement** — always shown. When selected, a file uploader appears inline in Zone A. The uploaded file is validated (same .docx + size check as BA-TPL-01) but is NOT saved to `firm_profile/templates/`. It is stored temporarily for this pipeline run only (in memory or as a temp file scoped to the session). After the engagement run completes, the file is discarded.
    - **(c) No template — plain Word output** — always shown. OutputGenerator generates a document using python-docx defaults (no named styles applied, no firm branding). This is the correct option for quick internal drafts.
  - If no custom template exists for the workflow type, option (a) is suppressed. Maher sees only (b) and (c). There is no "use base template" option exposed to Maher — the base template is an internal fallback only.
  - Maher's selection is stored in `state.json` under the key `report_template_used`. Value format:
    - Option (a): `{"source": "global", "filename": "frm_risk_register_custom.docx", "resolved_at": "<ISO timestamp>"}`
    - Option (b): `{"source": "one_time", "filename": "<original upload filename>", "resolved_at": "<ISO timestamp>"}`
    - Option (c): `{"source": "none", "filename": null, "resolved_at": "<ISO timestamp>"}`
  - Template selection is recorded in `audit_log.jsonl` at the moment Maher clicks Run (not at the moment of selection). Event format: `{event: "template_selected", workflow: "<workflow_type>", template: "<filename or null>", scope: "global" | "one_time" | "none", case_id: "<id>", timestamp: "<ISO>"}`.
  - If Maher does not interact with the template selector (e.g. scrolls past it and clicks Run without choosing), the system applies the pre-selected default: (a) if a custom template exists, (c) otherwise. The audit event is still written with `scope: "global"` or `scope: "none"` as appropriate.
  - The one-time upload (option b) does NOT trigger the `update_report_template` AI tool. It is a direct file read by `OutputGenerator` with the same validation checks (valid .docx, ≤ 5 MB, required styles present). If validation fails, Run is blocked and the error is shown inline.
  - For one-time uploads, missing required styles cause a warning (not a hard block): "Template is missing styles: [list]. Output will use default formatting for those sections." Maher can proceed or cancel and fix the template.

**Edge cases:**
  - Maher selects option (a) (global template) but the file has been deleted from `firm_profile/templates/` between selection and the time OutputGenerator runs: OutputGenerator falls back to the base template. A warning banner is shown in Zone B: "Saved template not found — using base template instead." The audit event is updated with `fallback: true`.
  - Maher selects option (b) and uploads a file, then changes selection to option (c): the uploaded file is discarded immediately (removed from memory/temp). No file persists.
  - Maher uploads a file for option (b) that fails validation (invalid .docx, too large, or corrupted): the Run button remains disabled. The error is shown inline next to the uploader. Maher must either fix the file or choose a different option before Run is enabled.
  - The workflow type has no base template in `firm_profile/templates/` (broken install): same hard error as BA-TPL-01 — generation is blocked, error surfaced to Maher.
  - Maher resumes an in-progress case (non-terminal state.json): the template selector is not re-shown. The template recorded in `state.json` at first run is used. Maher cannot change the template mid-engagement without starting a new case.

**Out of scope:** Allowing Maher to change the template after a pipeline run has started. Template preview inside the Streamlit UI. Applying different templates to different sections of the same report. PPTX template selection (separate).

**Open questions for AK:**
  - For option (b) one-time uploads: if the upload is missing required styles and Maher proceeds with the warning, should the fallback for those specific sections come from the base template's styles or from python-docx defaults? Base template styles would produce more consistent output but is slightly more complex to implement.
  - Should the template selector state be preserved if Maher refreshes the browser mid-intake (before clicking Run)? Or is losing the selection on refresh acceptable in v1?
  - Is there a case where Maher wants to save a one-time upload as the new global template immediately after using it? If so, a "Save to firm templates" checkbox on option (b) would cover this without a separate Settings round-trip.

**Out of scope:** Real-time collaboration in CEM (multiple users). CEM conversations as discoverable legal documents (they are working papers, explicitly marked as such). Automated Lead extraction without Maher clicking "Save as Lead" (never auto-extract — Maher controls what enters the case record). CEM for Mode B workflows (Proposal, Policy, Training — these do not have evidence documents in the forensic sense).
