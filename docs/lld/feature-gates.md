# Feature Gates — Pre-Build Design Requirements

Design constraints that must be resolved before implementation begins.
Each gate below is a build blocker for the named feature.

**Source:** Sprint-REM-04, derived from Phase 3 future-direction simulation (FUT-22, FUT-25, FUT-27, FUT-29).

---

## Gate 1 — Custom Investigation Templates (FUT-22)

**Blocks:** Custom Investigation (Type 9), AUP Investigation (Type 8) where user supplies own template.

### Constraint

`python-docx` raises `KeyError` at artifact generation time if a named paragraph style referenced in
the rendering code does not exist in the template file. A user-supplied .docx without the firm's
standard styles will crash the pipeline with no user-facing explanation.

### Required before build

1. **Reference template** — `templates/investigation_reference.docx` must exist and contain these
   named paragraph styles:
   - `Heading 1`, `Heading 2`, `Heading 3`
   - `Body Text`
   - `Table Header`, `Table Body`
   - `Caption`

2. **Pre-pipeline validation** — before the orchestrator starts, validate the template file:
   ```python
   def validate_template(template_path: Path) -> list[str]:
       """Return list of missing required style names. Empty list = valid."""
       from docx import Document
       REQUIRED_STYLES = {"Heading 1", "Heading 2", "Body Text", "Table Header"}
       doc = Document(template_path)
       present = {s.name for s in doc.styles}
       return sorted(REQUIRED_STYLES - present)
   ```
   Surface as a pre-hook veto with a friendly message:
   `"Template missing required styles: {missing}. Use the GoodWork reference template or add the styles manually."`

3. **Fallback** — if no template is provided, use `templates/investigation_reference.docx`.
   Never allow a missing-template condition to reach artifact generation silently.

### Acceptance criteria

- `validate_template()` called before `Orchestrator.run()` for Type 8/9 workflows.
- Missing styles surface as a pre-pipeline error with the exact style names listed.
- `templates/investigation_reference.docx` ships with the repo (committed, not gitignored).

---

## Gate 2 — Evidence Chat Session (CEM) Context Cap (FUT-25)

**Blocks:** Evidence Chat Session / CEM feature build.

### Constraint

`CEM_CONTEXT_CHARS = 16,000` is the confirmed context budget per session. At 50 turns of typical
adversarial interview exchange, the context window is exhausted. The simulation showed a 14%
failure rate from context exhaustion alone — the second highest failure mode for this workflow.

Without an explicit cap and user warning, the consultant loses the session silently (API truncation
or error) with no prompt to save work.

### Required before build

1. **Turn counter** — `evidence_chat_session` must track `turn_count` in session state.

2. **Warning at turn 45** — surface a persistent banner:
   `"5 turns remaining in this session (context limit). Consider promoting key findings to a workpaper now."`

3. **Hard stop at turn 50** — block new user input. Show:
   `"Session limit reached. Promote your findings to a workpaper to preserve them, then start a new session if needed."`
   Expose a "Promote to Workpaper" button that triggers the workpaper promotion flow inline.

4. **Context budget tracking** — the `CEM_CONTEXT_CHARS` constant must be defined in `config.py`
   (not hardcoded in the page) so it can be adjusted per model tier without touching the UI.

5. **Session resumability** — promoted workpapers must carry a `source_session_id` field so the
   consultant can trace which chat session produced which workpaper.

### Acceptance criteria

- Warning banner appears at turn 45, not after.
- New input is blocked at turn 50 with inline "Promote to Workpaper" button visible.
- `CEM_CONTEXT_CHARS` in `config.py`.
- `source_session_id` on promoted workpaper artifact.

---

## Gate 3 — Knowledge Harvester PII Filter (FUT-27)

**Blocks:** Knowledge harvester feature build (any code that writes patterns to the shared knowledge library).

### Constraint

The knowledge harvester extracts patterns from completed case artifacts to build the firm's
knowledge library. The simulation confirmed a 13% PII-leak rate from unfiltered harvest —
the highest failure mode for this workflow. If client names, case IDs, entity names, or
financial figures are not stripped, they leak from one engagement into another engagement's
AI output.

This is not an optional sanitisation step — it is a mandatory pre-write gate.

### Required before build

1. **PII filter function** — must be applied to every string extracted before it enters the library:
   ```python
   def sanitize_harvest(text: str, case_manifest: dict) -> str:
       """Strip client-identifiable information from harvested pattern text."""
       # 1. Replace entity names from case manifest
       for entity in case_manifest.get("entities", []):
           text = text.replace(entity, "[ENTITY]")
       # 2. Replace case_id prefix patterns
       import re
       text = re.sub(r'\b[A-Z]{2,6}-\d{4,}\b', '[CASE_ID]', text)
       # 3. Replace financial figures above AED 10,000
       text = re.sub(r'\bAED\s?[\d,]+\b', '[AMOUNT]', text)
       text = re.sub(r'\bUSD\s?[\d,]+\b', '[AMOUNT]', text)
       # 4. Re-run sanitize_pii from pre_hooks (covers passport/IBAN/account)
       from hooks.pre_hooks import sanitize_pii
       return sanitize_pii({"description": text}, {})["description"]
   ```

2. **Human review gate** — no pattern enters the shared library without an explicit consultant
   approval step. The harvest pipeline must:
   - Extract candidate patterns
   - Show them to the consultant in a review UI (inline diff: original → sanitised)
   - Only write approved patterns after the consultant clicks "Approve for Library"
   - Log each approval to `audit_log.jsonl` with the consultant's session ID

3. **Library namespace** — harvested patterns must be stored under a firm-level namespace, not
   per-case. Path: `knowledge/library/{category}/{pattern_id}.json`. No case_id in the path.

4. **Embedding isolation** — if sentence-transformers is not installed, the harvester must
   surface a visible warning and refuse to run (not silently degrade to zero-vector embeddings).
   Error: `"Knowledge harvester requires sentence-transformers. Install with: pip install sentence-transformers"`

### Acceptance criteria

- `sanitize_harvest()` called on every extracted string before review.
- Human approval gate shown before any write to `knowledge/library/`.
- Each library write logged to `audit_log.jsonl`.
- Missing sentence-transformers raises a visible error, not a silent fallback.

---

## Gate 4 — Multi-Workstream Artifact Slug Prefix (FUT-29)

**Blocks:** AUP Investigation (Type 8) multi-workstream build, Sprint-IA-03.

### Constraint

Current artifact naming: `{agent}_{artifact_type}.v{N}.json` (e.g. `junior_output.v1.json`).
When two different workflows run under the same `case_id` (AUP Type 8 can host multiple
workstreams), workflow A's `junior_output.v1.json` silently overwrites workflow B's.

No collision today — each case has exactly one workflow. Becomes a data-loss bug the moment
Sprint-IA-03 ships multi-workstream support.

### Required before Sprint-IA-03 ships

1. **Rename artifact path function** — update `artifact_path()` in `tools/file_tools.py`
   to include workflow slug:
   ```python
   filename = f"{workflow_slug}_{agent}_{artifact_type}.v{version}.json"
   # e.g. aup_investigation_junior_output.v1.json
   ```

2. **Update `next_version()` glob** — change glob pattern to include workflow slug:
   `f"{workflow_slug}_{agent}_{artifact_type}.v*.json"`

3. **Inject workflow into persist_artifact context** — `core/orchestrator.py` must ensure
   `context["workflow"]` is set before calling `run_post()`.

4. **Migration note** — existing cases in `cases/` use the old naming. Add a migration
   utility `scripts/migrate_artifact_names.py` that renames existing artifacts when
   the case has exactly one workflow (safe to rename) and leaves multi-workflow cases
   for manual review.

5. **Update all test fixtures** — `simulation/empirical_fixtures.py` and
   `tests/test_workflow_smoke.py` artifact path assertions must use the new pattern.

### Acceptance criteria

- Two workflows under one case_id produce non-colliding artifact files.
- `next_version()` correctly counts versions per workflow, not globally.
- Migration script exists before the naming change lands.

---

*Gates written: 2026-04-21 — Sprint-REM-04*
*Review before: Sprint-IA-02 (Gates 1–3) and Sprint-IA-03 (Gate 4)*
