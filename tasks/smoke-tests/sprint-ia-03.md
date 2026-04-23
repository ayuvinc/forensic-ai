# Smoke Test Spec — Sprint-IA-03
# HybridIntakeEngine wiring: FRM, DD, Sanctions, TT, Policy/SOP, Training

Status: PENDING MAHER LIVE RUN
Generated: 2026-04-23
Tester: Maher (live Streamlit app)

---

## Pre-conditions
- `streamlit run app.py` running
- ANTHROPIC_API_KEY set in .env
- Active project / engagement optionally set in sidebar

---

## STEP-A — 06_FRM.py

**A-1 Load:** Navigate to FRM Risk Register. Verify page loads without crash.
**A-2 Engine renders:** Jurisdiction selectbox, Industry text input, Company size selectbox, and 8 Module radio fields (Yes/No) all visible.
**A-3 Module dependency:** Select Module 3 (Yes) or Module 7 (Yes) without selecting Module 2. Click Confirm. Verify warning "Module(s) {2} added automatically" fires and Module 2 is added to selected_modules.
**A-4 Remarks trigger:** On Jurisdiction field, select a jurisdiction and add Remarks. Verify engine advances to conversation step.
**A-5 Confirm:** Complete engine fields and click Confirm. Verify transition to `frm_stage = confirm` (doc upload screen).
**A-6 Reset:** From a non-intake stage, click "Start New FRM Case" in sidebar. Verify engine state clears and blank intake re-renders.

---

## STEP-B — 09_Due_Diligence.py

**B-1 Load:** Navigate to Due Diligence. Verify page loads without crash.
**B-2 Engine renders:** Jurisdiction, DD depth, Subject type, Subject jurisdictions (multiselect), Industry, Description all visible.
**B-3 Post-engine fields:** After engine Confirm step, verify Subject name (text_input), DD purpose, Subject count (number_input), Relationship (radio), and doc upload all appear BELOW the engine confirmation.
**B-4 Screening level map:** Select "Enhanced Phase 2" in engine. Click Run Due Diligence. Verify `dd_params["screening_level"] == "enhanced_phase2"`.
**B-5 Report format:** Subject count=1, Relationship=Unrelated → `report_format = "per_subject"`. Subject count=2 → `report_format = "consolidated"`.
**B-6 Reset:** Click "Start New Case" → engine clears, blank intake.

---

## STEP-C — 10_Sanctions.py

**C-1 Load:** Navigate to Sanctions Screening. Verify knowledge_only error banner renders (if RESEARCH_MODE != live).
**C-2 Gate blocks engine:** Before ticking the acknowledgement checkbox, verify engine fields do NOT render (info message visible only).
**C-3 Gate passes:** Tick acknowledgement checkbox. Verify engine fields now render.
**C-4 Subject name in engine:** "Name of individual or entity to screen" is first field in engine (not a separate text_input).
**C-5 Purpose mapping:** Select "Periodic Review" in engine. On transition, verify `san_params["purpose"] == "periodic_review"`.
**C-6 Nationalities/aliases split:** Enter "UAE, UK" in nationalities field. Verify `san_params["nationalities"] == ["UAE", "UK"]`.
**C-7 Reset:** "Start New Case" clears engine AND `sanctions_acknowledged` state.

---

## STEP-D — 11_Transaction_Testing.py

**D-1 Load:** Navigate to Transaction Testing. Verify page loads without crash.
**D-2 Engine renders:** Jurisdiction, Engagement context, Fraud typology, Transaction types, Date range, Data inventory, Evidence standard, Description all visible.
**D-3 Context key map:** Select "Audit / Controls Compliance". On transition, verify `tt_params["engagement_context"] == "audit_compliance"`.
**D-4 Fraud typology None:** Select engagement context "Audit / Controls Compliance" and fraud typology "Not applicable". Verify `tt_params["fraud_typology"] is None`.
**D-5 Doc upload outside engine:** After engine Confirm, doc upload widget appears before Run Transaction Testing button.
**D-6 Date range required:** Date range is a required field in engine — engine blocks Confirm if left blank.
**D-7 Reset:** "Start New Case" clears engine + doc upload state.

---

## STEP-E — 04_Policy_SOP.py

**E-1 Load:** Navigate to Policy / SOP Generator. Verify page loads without crash.
**E-2 Combined selectbox:** Single "Document type" selectbox shows all 11 options (6 policies + 5 SOPs). No separate "Policy" / "SOP" radio.
**E-3 Doc type inference — policy:** Select "AML / CFT Policy". On transition, verify `ps_params["doc_type"] == "policy"` and `ps_params["doc_subtype"] == "aml_cft_policy"`.
**E-4 Doc type inference — sop:** Select "Fraud Investigation SOP". On transition, verify `ps_params["doc_type"] == "sop"` and `ps_params["doc_subtype"] == "fraud_investigation_sop"`.
**E-5 Gap analysis map:** Select "New document" → `ps_params["gap_analysis"] == "new"`. Select "Gap analysis of existing" → `"gap"`.
**E-6 Reset:** "Start New Case" clears engine state.

---

## STEP-F — 05_Training.py

**F-1 Load:** Navigate to Training Material. Verify page loads without crash.
**F-2 Engine renders:** Jurisdiction, Training topic (selectbox), Target audience (selectbox), Duration (selectbox with presets), Include quiz (radio Yes/No), Include case study (radio Yes/No), Industry, Description all visible.
**F-3 Duration conversion:** Select "90 min" → `tr_params["duration"] == 90`. Select "Custom" → `tr_params["duration"] == 60` (safe default).
**F-4 Bool conversion:** include_quiz = "Yes" → `tr_params["include_quiz"] is True`. "No" → `False`.
**F-5 Topic key map:** Select "Fraud Awareness" → `tr_params["topic"] == "fraud_awareness"`. "Board / Directors" audience → `tr_params["target_audience"] == "board_directors"`.
**F-6 Reset:** "Start New Case" clears engine state.

---

## STEP-G — Cross-page regression

**G-1 Investigation page unaffected:** Navigate to 02_Investigation.py. Verify it still loads and renders HybridIntakeEngine (no regression from IA-03 changes).
**G-2 Session isolation:** Navigate between FRM and DD pages. Verify engine session_state from one page does not contaminate the other (`hybrid_intake_frm_*` vs `hybrid_intake_due_diligence_*` namespacing).
**G-3 Test suite:** `python3 -m pytest tests/ -x` → 131 passed, 0 failed.
