# Channel

## Last QA Run
Agent: qa-run
Sprint: Sprint-IA-03
Timestamp: 2026-04-23T06:10:00Z
Status: PASS

## Criterion Results

### IA-03-C1 (field configs)
- [PASS] All 6 configs importable
- [PASS] All field_types valid (selectbox/multiselect/radio/text/textarea)
- [PASS] required=True fields defined; has_remarks fields correct
- [PASS] 131 tests pass

### IA-03-W1 (06_FRM.py)
- [PASS] HybridIntakeEngine wired; frm_intake_form import removed (comments only, no import statement)
- [PASS] Module dependency enforcement (missing_deps auto-add + st.warning)
- [PASS] primary_jurisdiction from engine; workflow=frm_risk_register
- [PASS] frm_stage=confirm on engine_result
- [PASS] 131 tests pass

### IA-03-W2 (09_Due_Diligence.py)
- [PASS] HybridIntakeEngine wired; dd_intake_form import removed
- [PASS] subject_count and relationship outside engine (post-engine)
- [PASS] report_format logic (per_subject/consolidated)
- [PASS] dd_params["screening_level"] mapped from _DD_DEPTH_MAP
- [PASS] 131 tests pass

### IA-03-W3 (10_Sanctions.py)
- [PASS] knowledge_only gate position: byte offset 88 < engine offset 2159
- [PASS] subject_name from engine values (not separate text_input)
- [PASS] nationalities + aliases split on comma
- [PASS] _SAN_PURPOSE_KEYS + _SAN_OUTPUT_KEYS present
- [PASS] _san_engine.reset() + sanctions_acknowledged pop in reset button
- [PASS] 131 tests pass

### IA-03-W4 (11_Transaction_Testing.py)
- [PASS] HybridIntakeEngine wired; generic_intake_form removed
- [PASS] "Not applicable" → None in _TT_TYPOLOGY_KEYS (line 26)
- [PASS] doc upload outside engine (after engine_result is not None)
- [PASS] "Run Transaction Testing" button present
- [PASS] sampling="full_population" preserved
- [PASS] 131 tests pass

### IA-03-W5 (04_Policy_SOP.py)
- [PASS] POLICY_SUBTYPE_LABELS imported; doc_type inferred from membership
- [PASS] gap_analysis "New document"→"new" / "Gap analysis of existing"→"gap"
- [PASS] _POLICY_SUBTYPE_KEYS maps all 11 labels → pipeline keys
- [PASS] no separate doc_type selectbox widget
- [PASS] 131 tests pass

### IA-03-W6 (05_Training.py)
- [PASS] Duration "Custom" → 60; strip " min" → int conversion
- [PASS] include_quiz/include_case_study "Yes"/"No" → bool
- [PASS] _TR_TOPIC_KEYS + _TR_AUDIENCE_KEYS present
- [PASS] TRAINING_TOPICS/TARGET_AUDIENCES inverted dicts for running-stage display
- [PASS] 131 tests pass

### IA-03-QA (smoke test)
- [PASS] Smoke test spec written: tasks/smoke-tests/sprint-ia-03.md (7 steps, 6 pages + regression)
- [PASS] 131 tests pass (regression gate)
- [MANUAL] Steps A-G pending Maher live run in Streamlit

## Mobile Issues
None — Streamlit app; no custom CSS layout in wired pages.

## Warnings
- frm_intake_form appears in 2 comment lines in 06_FRM.py (docstring + code comment). Not an import. AC satisfied.
- date_range validation in TT now enforced at engine confirmation step (required field), not at Run click. Behaviour preserved, stage shifted earlier. Acceptable.
- Training TRAINING_TOPICS/TARGET_AUDIENCES dicts reconstructed as inverted maps (key→label) for running-stage expander display.
