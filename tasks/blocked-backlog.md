# Blocked Backlog
Tasks here are BLOCKED on BA sign-off or architectural decision. They cannot enter the build queue
until a /ba session produces the required entry in tasks/ba-logic.md.
Re-activate: open a BA session, write the required ba-logic.md entry, then move task to todo.md.

---

## FE-10 — FRM Risk Register: Excel Output (.xlsx)
**BLOCKED: MISSING_BA_SIGNOFF**
No BA entry exists for Excel as a required output format for FRM Risk Register.
Required: /ba session producing BA-FE-10 entry covering: when Excel is required vs optional,
schema for Excel tabs, whether it replaces or supplements DOCX, file naming convention.

- [ ] FE-10 / P8-12-EXCEL — `tools/frm_excel_builder.py` + pages/06_FRM.py Done stage second download button.
  Do not build until /ba session produces entry in tasks/ba-logic.md.

---

## FE-11 — FRM Risk Register: Two-Tier Risk Structure
**BLOCKED: MISSING_BA_SIGNOFF**
No BA entry for tier taxonomy (Design-Level vs Operational-Level) or schema change to RiskItem.
Required: /ba session producing BA-FE-11 entry covering: tier definitions, whether both tiers
appear in same register or separate sections, impact on current RiskItem schema.

- [ ] FE-11 / P8-13-TIER — Two-tier risk structure (Design-Level vs Operational-Level).
  Do not build until /ba session produces entry in tasks/ba-logic.md.

---

## Sprint-10L Phase B — Behavioral Matrix
**BLOCKED: MISSING_BA_SIGNOFF**
REVIEW_MODE enum, verdict spectrum, DocLevel axis, Phase axis, Authority Level have no BA entry.
Required: /ba session with AK input producing SRL-B-BA entry.

**Files touched when unblocked:** config.py, schemas/artifacts.py, core/orchestrator.py,
agents/project_manager/prompts.py + agent.py, agents/partner/prompts.py + agent.py,
workflows/sanctions_screening.py, due_diligence.py, transaction_testing.py, investigation_report.py

- [ ] SRL-B-BA Write BA entries for behavioral matrix to ba-logic.md (AK input required)
- [ ] SRL-B-01 config.py — REVIEW_MODE flag with validation (DEMO/DEV/CLIENT_DRAFT/CLIENT_FINAL)
- [ ] SRL-B-02 schemas/artifacts.py — ReviewVerdict enum; update ApprovalDecision + RevisionRequest
- [ ] SRL-B-03 core/orchestrator.py — behavioral_matrix(), universal_blocker_checks(), D0/D1 equivalence enforcement
- [ ] SRL-B-04 agents/project_manager/prompts.py — rewrite to consume full matrix context
- [ ] SRL-B-05 agents/partner/prompts.py — same
- [ ] SRL-B-06 agents/project_manager/agent.py + agents/partner/agent.py — pass matrix context
- [ ] SRL-B-07 workflows/sanctions_screening.py, due_diligence.py — BLOCK not loop for G-A
- [ ] SRL-B-08 workflows/transaction_testing.py, investigation_report.py — intake completeness gates

---

## Sprint-FE — BA Gate (FE-GATE-BA)
**BLOCKED: BA-FE-01 MISSING**
No BA entry covers: AI questions stage placement, template selector placement, per-hit review
screen, DD intake extensions, P9-05 workspace UX.
Required: /ba or /ux session producing BA-FE-01.

Sprint-FE tasks FE-01..FE-07 are written in todo.md but gated on BA-FE-01. Once BA-FE-01
exists in ba-logic.md, the gate opens and tasks can enter the build queue.
