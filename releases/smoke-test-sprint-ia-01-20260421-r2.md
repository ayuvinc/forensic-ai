# Smoke Test — Sprint-IA-01 — Navigation Restructure + Multi-Workflow Workspace (Re-run 2)
Date: 20260421
Sprint: sprint-ia-01
Branch: feature/sprint-fe-triage
Tester: AK (manual)
Re-run: targeted — STEP-10/13/14/15/16 only (STEP-00..09, 11, 12 confirmed PASS in run 1)
Overall: FAIL

## Summary
| Step | Area | Severity | Result | Notes |
|------|------|----------|--------|-------|
| STEP-00 | Setup | P0 | SKIP/PASS | Confirmed PASS run 1 |
| STEP-01 | Startup | P0 | SKIP/PASS | Confirmed PASS run 1 |
| STEP-02 | Sidebar | P0 | SKIP/PASS | Confirmed PASS run 1 |
| STEP-03 | Sidebar | P0 | SKIP/PASS | Confirmed PASS run 1 |
| STEP-04 | Sidebar | P0 | SKIP/PASS | Confirmed PASS run 1 |
| STEP-05 | Sidebar | P0 | SKIP/PASS | Confirmed PASS run 1 |
| STEP-06 | Sidebar | P0 | SKIP/PASS | Confirmed PASS run 1 |
| STEP-07 | Sidebar | P0 | SKIP/PASS | Confirmed PASS run 1 |
| STEP-08 | Pages | P0 | SKIP/PASS | Confirmed PASS run 1 |
| STEP-09 | Pages | P0 | SKIP/PASS | Confirmed PASS run 1 |
| STEP-10 | Pages | P0 | PASS | Page heading: "Engagement Scoping". URL: localhost:8501/Scope — fix confirmed. Sidebar loading error text noted (transient). |
| STEP-11 | Pages | P1 | SKIP/PASS | Confirmed PASS run 1 |
| STEP-12 | Pages | P1 | SKIP/PASS | Confirmed PASS run 1 |
| STEP-13 | Pages | P0 | PASS | Workspace loaded — engagement picker dropdown visible, no error |
| STEP-14 | Multi-Workflow | P0 | PASS | abc-corp-test-engagement card visible in Active Engagements — opened successfully, Run Workflow selectbox present |
| STEP-15 | Multi-Workflow | P0 | PASS | 9 options in Run Workflow dropdown — Persona Review present as last option |
| STEP-16 | Workspace | P0 | FAIL | AttributeError: 'ProjectState' object has no attribute 'client_name' — 16_Workspace.py:129 |

## P0 Failures (blocks QA_APPROVED)
- **STEP-16**: `AttributeError: 'ProjectState' object has no attribute 'client_name'` — `16_Workspace.py:129`: `st.caption(f"Client: {state.client_name} | Service: {state.service_type} | Last session: {last_session}")`. Fix: replace `state.client_name` with the correct attribute from `ProjectState` schema (likely `state.intake.client_name` or similar).

## P1 Failures (documented, does not block)
- none

## Observations (outside spec)
- STEP-10: Sidebar shows a "loading error" text — details not captured. Likely transient after page rename + Streamlit restart. Monitor on next run.

## Change Requests (outside spec — for junior-dev)
- CR-01: Rename "Persona Review" → "Individual Due Diligence - Background checks" across sidebar label, workflow selectbox, and any internal label references.

## Fixes Confirmed Working (run 2)
- FIX-01: Scope URL slug now `/Scope` (was `/b_Scope`) — PASS
- FIX-02: abc-corp-test-engagement now in Active Engagements (not Legacy) — PASS; Workspace picker shows only A-F engagements — PASS

## QA Signal
**QA_REJECTED**
Reason: STEP-16 P0 failure — `ProjectState.client_name` attribute missing. One-line fix in `16_Workspace.py:129`. Re-run `/smoke-test sprint_id=sprint-ia-01` after fix.
