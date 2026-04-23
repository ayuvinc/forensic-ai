# LLD: Policy/SOP Co-Build (Sprint-IA-04)

**Status:** CURRENT — written post-build, Session 044  
**BA:** BA-IA-09 (tasks/ba-logic.md)  
**HLD reference:** docs/hld.md → Co-Build Workstream section  
**Files:** `schemas/policy_sop_cobuild.py`, `workflows/policy_sop_cobuild.py`, `pages/04_Policy_SOP.py`

---

## Stage Machine

```
intake
  │  HybridIntakeEngine → CaseIntake + params (doc_type, doc_subtype, gap_analysis)
  ▼
ai_questions
  │  render_intake_questions() → aic_context string
  ▼  (if doc_subtype == "custom")
custom_scoping ──► 5 questions, one per rerun → custom_doc_scoping.json
  │  (otherwise skip)
  ▼
structure_proposal
  │  propose_structure() [Sonnet] → section titles list
  │  Maher edits list (reorder / add / remove) → Confirm
  ▼
section_loop                              ◄──┐
  │  draft_section() [Haiku] on first visit    │
  │  Maher: Approve | Edit & Save | Regenerate │
  │  revise_section() [Haiku] on Regenerate    │
  │  append_audit_event() after each action    │
  │  _save_progress() after each action        │
  │  current_idx += 1                          │
  └── if current_idx < total ─────────────────┘
  │  if current_idx >= total
  ▼
done
  │  assemble_and_write() — no model call
  │  write_final_report() → F_Final/final_report.en.md + .en.docx
  ▼
  [download button]
```

**Invalid transitions:** The stage machine only moves forward. Backward navigation is not supported (design decision from BA-IA-09: "A section cannot be skipped"). "Start New Document" resets to intake.

---

## Session State Keys

| Key | Type | Set in | Description |
|-----|------|--------|-------------|
| `ps_stage` | `str` | page init | Current stage name |
| `ps_intake` | `CaseIntake` | intake stage | Pydantic intake object |
| `ps_params` | `dict` | intake stage | `{doc_type, doc_subtype, gap_analysis}` |
| `ps_aic_context` | `str` | ai_questions stage | Joined AIC Q&A pairs |
| `ps_custom_q_idx` | `int` | page init | Which custom scoping question is active |
| `ps_custom_answers` | `dict` | custom_scoping stage | Accumulated answers to 5 scoping questions |
| `ps_proposed_sections` | `list[str]` | structure_proposal stage | Working section titles list |
| `ps_co_build` | `dict` | structure_proposal → confirm | Serialised `CoBuildState` |
| `ps_show_regen` | `bool` | page init | Whether Regenerate instructions panel is visible |
| `ps_assembled` | `bool` | done stage | Guards against double-assembly on rerun |
| `ps_result` | `FinalDeliverable` | done stage | Return value from `assemble_and_write` |

---

## Orchestrator Functions

### `propose_structure(intake, params, aic_context, custom_scope) -> list[str]`

| Item | Value |
|------|-------|
| Model | SONNET |
| Max tokens | 512 |
| Input | CaseIntake fields + doc_type, doc_subtype, gap_analysis, aic_context, custom_scope dict |
| Output | 6–14 section title strings (parsed from numbered list) |
| Fallback | If fewer than 6 titles parsed, pads with `"Section N"` strings |
| Error handling | Exception propagates to page; page shows `st.error()` and `st.stop()` |

**Prompt outline:** System sets consulting/compliance context. User prompt includes DOCUMENT TYPE, CLIENT, JURISDICTION, MODE (new vs gap), DESCRIPTION, CUSTOM SCOPE (if any), AIC CONTEXT (if any). Instructs model to return a numbered list of titles only.

---

### `draft_section(section_title, sections_list, prior_approved_bodies, doc_type, doc_subtype, intake, model=HAIKU) -> str`

| Item | Value |
|------|-------|
| Model | HAIKU (default); can be overridden to SONNET |
| Max tokens | 1024 |
| Input | Section title, full outline, prior approved bodies (truncated to last 1500 chars), doc_type, doc_subtype, client/jurisdiction from intake |
| Output | Section body text (Markdown, 150–400 words) |
| Context truncation | `prior_context[-1500:]` — keeps most recent approved sections, not earliest |

**Prompt outline:** User prompt includes FULL DOCUMENT OUTLINE, SECTIONS ALREADY DRAFTED, and the specific section to draft. Instructs model to write body only (no heading) in Markdown.

---

### `revise_section(section_title, current_body, instructions, doc_type, doc_subtype, intake, model=HAIKU) -> str`

| Item | Value |
|------|-------|
| Model | HAIKU (default) |
| Max tokens | 1024 |
| Security | `instructions` is HTML-stripped (`re.sub(r"<[^>]+>", "", text)`) and capped at 500 chars before injection |
| Output | Revised section body (Markdown) |

---

### `assemble_and_write(co_build_state, intake, registry=None, hook_engine=None) -> FinalDeliverable`

No model API call. Pure assembly:
1. Joins all section bodies in order with `## N. Title` headings.
2. Prepends a cover header (client, jurisdiction, date).
3. Calls `write_final_report(case_id, content, "en", workflow="policy_sop")`.
4. Calls `append_audit_event` with `event="cobuild_complete"`, section count, action breakdown.
5. Calls `write_artifact` to persist a deliverable metadata record.
6. Returns `FinalDeliverable(approved_by="consultant", ...)`.

**Note:** `registry` and `hook_engine` parameters are accepted but not used (signature matches other workflow functions for interface consistency).

---

### `identify_gaps(intake, params, uploaded_doc_text, standard_sections) -> dict[str, str | None]`

| Item | Value |
|------|-------|
| Model | SONNET |
| Max tokens | 4096 |
| Input | Existing document text (truncated to 6000 chars), proposed section titles |
| Output | `{section_title: existing_text_or_None}` |
| Fallback | On JSON parse failure or any exception: returns `{title: None}` for all sections (safe fallback — blank drafts) |

Used in gap analysis mode (`gap_analysis == "gap"`) when documents are registered via DocumentManager.

---

## Audit Events

All events written to `cases/{case_id}/audit_log.jsonl` via `append_audit_event`.

### Per-section events (one per section, written at action time)

```json
{
  "event": "section_approved" | "section_edited" | "section_regenerated",
  "section_title": "Roles and Responsibilities",
  "action": "approved" | "edited" | "regenerated",
  "agent": "consultant"
}
```

### Assembly event (one per completed document)

```json
{
  "event": "cobuild_complete",
  "agent": "policy_sop_cobuild",
  "workflow": "policy_sop",
  "doc_subtype": "whistleblower_policy",
  "section_count": 9,
  "actions": {
    "approved": 6,
    "edited": 2,
    "regenerated": 1
  },
  "status": "ok"
}
```

---

## cobuild_progress.json Schema

Written atomically to `cases/{id}/E_Drafts/cobuild_progress.json` (AF projects) or `cases/{id}/cobuild_progress.json` (legacy) after each section approval.

```json
{
  "sections": [
    {
      "section_title": "Purpose and Scope",
      "body": "...",
      "status": "approved",
      "action_note": ""
    }
  ],
  "current_idx": 3,
  "doc_type": "policy",
  "doc_subtype": "whistleblower_policy",
  "gap_analysis": "new",
  "custom_scope": null,
  "structure_confirmed": true,
  "aic_context": "Q: ...\nA: ...",
  "intake_snapshot": {
    "case_id": "...",
    "client_name": "...",
    "industry": "...",
    "primary_jurisdiction": "UAE",
    "description": "...",
    "workflow": "policy_sop",
    "language": "en",
    "created_at": "..."
  }
}
```

**Resume behaviour:** On page load, if `active_project` is set in session state and `cobuild_progress.json` exists with `structure_confirmed=true` and a non-empty `intake_snapshot`, the page offers "Resume co-build" or "Start new document". Resuming restores `ps_co_build`, `ps_intake`, `ps_params`, and advances `ps_stage` to `"section_loop"`.

---

## Security Notes

- `doc_subtype` comes from a controlled selectbox — no injection risk.
- `regen_instructions` is user free text — HTML-stripped and capped at 500 chars before model injection (`_strip_html` in orchestrator, `max_chars=500` in `st.text_area`).
- `cobuild_progress.json` is local-only and contains no PII beyond what is already in `cases/{id}/`.
- `sanitize_pii` pre-hook applies to all downstream model calls via the standard hook chain.
