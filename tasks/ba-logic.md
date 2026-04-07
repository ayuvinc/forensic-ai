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

