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
- Case IDs are sequential integers, zero-padded to 4 digits (e.g. `0001`, `0042`)

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
→ Currently stays at INTAKE_CREATED. Options: reuse OWNER_APPROVED or create DELIVERABLE_WRITTEN. Decision pending — see C-02a in tasks/todo.md.
