# Sprint-IA-02 Smoke Test Spec

**Sprint:** Sprint-IA-02 — Hybrid Intake
**BA decisions:** BA-IA-04, BA-IA-05, BA-IA-06, BA-IA-07
**Branch:** `feature/sprint-ia-02-hybrid-intake`
**Tester:** QA / Maher
**Run command:** `streamlit run app.py` (from `~/forensic-ai`)

---

## Pre-conditions

- `.env` is present with `ANTHROPIC_API_KEY` and `TAVILY_API_KEY`
- `RESEARCH_MODE=knowledge_only` in `.env` (default) — STEP-F verifies this behaviour
- App starts cleanly at http://localhost:8501
- At least one existing legacy engagement exists OR tests create fresh engagements as described

---

## STEP-A — Multi-workstream engagement → Workspace shows declared sections

**Goal:** BA-IA-04 — creating an engagement with 2 workstreams shows both sections in Workspace before either is run.

**Steps:**
1. Navigate to **Engagements** (sidebar → MAIN → Engagements)
2. Click **＋ New Engagement**
3. Enter engagement name: `Smoke IA02 A`; client name: `Test Corp A`
4. In **Workstreams** multiselect, select: `Investigation Report` and `FRM Risk Register`
5. Leave language standard as default
6. Click **Create Engagement** — confirm success banner

**In Workspace:**
7. From the created engagement detail, click **Open Workspace**
8. In Workspace, locate **Workflow Outputs** expander
9. Expand it

**Pass criteria:**
- [ ] Engagement creation succeeds (no error)
- [ ] Workspace **Workflow Outputs** expander title shows `(0 runs of 2 declared)` or similar indicating 2 declared workstreams
- [ ] Two sections appear: one for **Investigation Report** and one for **FRM Risk Register**
- [ ] Each unrun section shows text "Workstream added — not yet run."
- [ ] Each unrun section has a **Run Now** button
- [ ] Clicking **Run Now** for Investigation Report navigates to the Investigation page (URL contains `02_Investigation`)
- [ ] Clicking **Run Now** for FRM Risk Register navigates to the FRM page (URL contains `06_FRM`)

**Fail criteria:**
- Engagement creation fails
- Workspace shows 0 sections or only 1 section
- "Run Now" button is missing or navigates to wrong page

---

## STEP-B — Standard investigation intake (no Remarks)

**Goal:** HybridIntakeEngine renders structured fields and passes values to pipeline for a standard investigation type.

**Steps:**
1. Navigate to **Investigation Report** (sidebar → WORKFLOWS)
2. Confirm intake stage is shown
3. Ensure no active engagement banner (or client_name auto-fills from banner)
4. If no banner: enter client name `Test Corp B`
5. In **Primary jurisdiction** field, select `UAE`
6. In **Investigation type** field, select `Asset Misappropriation`
7. Leave Remarks expanders empty for all fields
8. In **Regulators implicated** multiselect, select `None`
9. In **Evidence available** multiselect, select `Documents`
10. In **Audience** field, select `Management`
11. Enter **Industry**: `Retail`
12. Enter **Description**: `Suspected asset diversion by warehouse manager over Q1–Q2 2025.`
13. Click **Continue** (end of structured fields step)
14. No Remarks > 10 chars entered → expect to skip directly to **Confirmation** panel
15. Verify confirmation panel shows all values
16. Click **Confirm**
17. (Do not click **Run Investigation** — this test only verifies intake, not the full pipeline)

**Pass criteria:**
- [ ] Structured fields render (jurisdiction, investigation type, regulators, evidence, audience, industry, description as selectbox/multiselect/text/textarea — not a free-text-only form)
- [ ] Remarks expanders are visible on jurisdiction, investigation_type, regulators_implicated, evidence_available fields
- [ ] No Remarks > 10 chars → confirmation panel appears immediately after Continue (no targeted conversation step)
- [ ] Confirmation panel displays: `UAE`, `Asset Misappropriation`, `Management`, `Retail`, and the description text
- [ ] Confirm button is clickable and advances stage to AIC questions (or Run Investigation if AIC is disabled)

**Fail criteria:**
- Old generic intake form renders (single description textarea only)
- Confirmation panel is missing
- Field values not shown in confirmation

---

## STEP-C — AUP investigation intake (3 procedures)

**Goal:** BA-IA-05 — AUP investigation type shows procedures list; description is formatted as AUP SCOPE prefix.

**Steps:**
1. Navigate to **Investigation Report** — click **Start New Case** to reset if needed
2. Enter client name `Test Corp C`
3. In **Investigation type**, select `Agreed-Upon Procedures (AUP)`
4. Notice the AUP info banner: "AUP scope is locked at intake..."
5. In **Number of procedures** input, set to `3`
6. Enter:
   - Procedure 1: `Obtain and inspect all vendor invoices above AED 50,000 for Q1 2025`
   - Procedure 2: `Confirm bank transfer records against vendor payment schedule`
   - Procedure 3: `Reconcile petty cash logs against approved budgets`
7. Complete remaining fields (jurisdiction: UAE, audience: Management, industry: Finance)
8. Click **Continue**, then **Confirm**

**Pass criteria:**
- [ ] Selecting AUP shows the numbered procedures UI (not generic description textarea)
- [ ] AUP info banner is visible above procedures
- [ ] Procedures input accepts 3 procedures
- [ ] Confirmation panel shows the 3 procedures (not a generic description)
- [ ] After Confirm + Run Investigation: `CaseIntake.description` starts with `AUP SCOPE — Procedures agreed with client:` (verifiable by checking cases/{case_id}/state.json after run, or by inspecting session state before run)
- [ ] At least 1 non-empty procedure is required before Run Investigation is enabled (try with all empty — button must be disabled)

**Fail criteria:**
- AUP type shows generic description textarea instead of procedures UI
- Description does not have AUP SCOPE prefix
- Run Investigation enabled with zero procedures entered

---

## STEP-D — Custom investigation intake

**Goal:** BA-IA-06 — Other/Custom investigation type shows extended description + custom notice; description is prefixed.

**Steps:**
1. Navigate to **Investigation Report** — Start New Case
2. Enter client name `Test Corp D`
3. In **Investigation type**, select `Other / Custom`
4. Notice the info banner: "Custom type: the model will propose a report structure..."
5. Enter description: `Multi-party joint venture dispute involving undisclosed side agreements and alleged breach of fiduciary duties by the managing partner.`
6. Complete remaining fields (jurisdiction: UAE, audience: Legal Proceedings, industry: Real Estate)
7. Click **Continue**, then **Confirm**

**Pass criteria:**
- [ ] Selecting Other/Custom shows the info notice (not just a blank form)
- [ ] Description textarea is visible and accepts free text
- [ ] Confirmation panel shows the description
- [ ] After Confirm: description visible in confirmation starts with `CUSTOM INVESTIGATION — Structure to be proposed before drafting:` (verifiable via session state inspection or state.json)

**Fail criteria:**
- Other/Custom shows no info notice
- Description prefix is missing

---

## STEP-E — Remarks conversation fires for jurisdiction > 10 chars

**Goal:** BA-IA-07 — Remarks field with > 10 characters triggers a targeted conversation step before confirmation.

**Steps:**
1. Navigate to **Investigation Report** — Start New Case
2. Enter client name `Test Corp E`
3. In **Primary jurisdiction** selectbox, select `UAE`
4. Click to expand the **Remarks** expander next to jurisdiction
5. Enter remark: `UAE primary but also involves an offshore holding in BVI`  (> 10 chars)
6. Complete remaining fields with any valid values
7. Click **Continue**

**Pass criteria:**
- [ ] Remarks expander is present next to the jurisdiction field
- [ ] After clicking Continue with a remark > 10 chars: a **targeted conversation step** appears (not confirmation)
- [ ] The targeted conversation step shows the remark text and an AI-generated question about it
- [ ] Max 2 user reply rounds are enforced (after 2 replies, conversation closes and proceeds to confirmation)
- [ ] Confirmation panel shows the refined value or the original value + remarks note

**Fail criteria:**
- Remarks expander is missing
- Remark > 10 chars skips directly to confirmation with no conversation
- More than 2 reply rounds are permitted

---

## STEP-F — knowledge_only mode: Remarks skips API call

**Goal:** BA-IA-07 — In `knowledge_only` mode (default), Remarks conversation skips Claude API call and appends remarks note inline.

**Pre-condition:** `RESEARCH_MODE=knowledge_only` in `.env` (this is the default — do not change for this step)

**Steps:**
1. Navigate to **Investigation Report** — Start New Case
2. Enter client name `Test Corp F`
3. In jurisdiction, select `UAE`; in Remarks, enter: `UAE primary but offshore BVI structure is also relevant`
4. Complete remaining fields; click **Continue**

**Pass criteria:**
- [ ] No API call is made (no spinner or "AI is thinking" indicator appears for the remarks step)
- [ ] Intake proceeds to confirmation without a conversation step
- [ ] Confirmation panel shows the jurisdiction value with the remarks noted inline (e.g. `UAE [remarks noted: UAE primary but offshore BVI structure is also relevant]`)
- [ ] No error or crash occurs

**Fail criteria:**
- App crashes or shows an API error in knowledge_only mode
- Remarks are silently dropped with no trace in the confirmation panel

---

## STEP-G — Automated test suite passes

**Goal:** No regressions in existing 131 tests after all Sprint-IA-02 changes.

**Steps:**
1. From terminal in `~/forensic-ai`, run:
   ```
   python3 -m pytest tests/ -q
   ```

**Pass criteria:**
- [ ] Output: `131 passed` (no failures, no errors)
- [ ] Deprecation warnings acceptable — they are pre-existing

**Fail criteria:**
- Any test failure or import error

---

## Sign-off

| Step | Result | Notes |
|------|--------|-------|
| STEP-A | PASS / FAIL | |
| STEP-B | PASS / FAIL | |
| STEP-C | PASS / FAIL | |
| STEP-D | PASS / FAIL | |
| STEP-E | PASS / FAIL | |
| STEP-F | PASS / FAIL | |
| STEP-G | PASS / FAIL | |

QA sign-off: ___________________________  Date: ___________
