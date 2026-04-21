---
Status: active
Source: user-confirmed
Last confirmed with user: 2026-04-21
Owner: Architect
Open questions: 0
---

# LLD: Product IA Design — Two-Arc Model + Navigation

## Feature Purpose

Defines the two-arc product model (Proposal arc and Engagement arc), Streamlit navigation structure using `st.navigation()`, and the multi-workflow engagement pattern. This LLD is the authority for all Sprint-IA-01 and Sprint-IA-02 build decisions.

---

## Project as the Root Entity

An **Engagement** is called a **Project** in the UI. Every project has:
- `project_name` — human-readable name Maher sets at creation (e.g. "ABC Corp Fraud Investigation Q1 2026")
- `client_name` — who the client is
- `slug` — filesystem identifier (derived from project_name)
- `workstreams` — 1 to N workflow types; minimum 1 required at creation

**Minimum workstream constraint:** A project cannot be created with 0 workstreams. The creation intake requires at least 1 workstream to be selected. Workstreams can be added post-creation (1 → N). The constraint is enforced at creation only.

**Schema addition:** `ProjectState` needs `project_name: str` (additive — backward compatible; defaults to slug if absent in existing state.json files).

---

## Two-Arc Product Model

### Arc 1 — Proposal (pre-engagement)

The Proposal arc exists before any engagement is created. It handles prospect situations where Maher has not yet been formally retained.

```
[Arc 1 — Proposal]
  01b_Scope.py     → Engagement scoping conversation (what services, what scope)
  07_Proposal.py   → Proposal deck generation
  [manual step]    → Client signs engagement letter
  → Triggers Arc 2: Maher creates Engagement from signed letter
```

Arc 1 does NOT create a `ProjectState`. It is a standalone generation step. The output (proposal deck) is a document, not a case artifact.

### Arc 2 — Engagement / Project (root entity)

A Project is the root entity. It maps to one `ProjectState` on disk. A Project contains 1 to N independent workflow runs — Maher assembles the combined deliverable himself.

```
[Arc 2 — Project]
  Create Project → ProjectState created (project_name, slug, client, primary workstream + any additional)
                   minimum 1 workstream required at creation
  Run Workstream N    → cases/{slug}/{workflow_type}/... artifacts
  Run Workstream M    → cases/{slug}/{workflow_type}/... artifacts
  [add more as needed — no upper limit]
  Workspace            → all workstream outputs under the active project
```

**Key constraint:** `service_type` is the primary workstream type (metadata, not a restriction). Maher can run FRM + DD + Investigation on the same project. A project with 0 workstreams cannot be created.

---

## Navigation Model — st.navigation() Design

### Streamlit version: 1.56.0

Uses `st.navigation()` (supported since 1.29.0) with `st.Page(title=...)` for display name control. Pages/ directory convention is replaced — Streamlit no longer auto-registers all files in pages/ as sidebar entries.

### Four-Section Sidebar Layout

| Section | Pages | Display Title |
|---------|-------|---------------|
| `MAIN` | 01_Engagements.py | "Engagements" |
| | 16_Workspace.py | "Workspace" |
| `PROPOSALS` | 01b_Scope.py | "Scope" |
| | 07_Proposal.py | "Proposals" |
| `MONITOR` | 09_Case_Tracker.py | "Case Tracker" |
| | 15_Activity_Log.py | "Activity Log" |
| `SETTINGS` | 12_Team.py | "Team" |
| | 00_Setup.py | — NOT in sidebar (redirect-only) |
| `WORKFLOWS` | 02_Investigation.py | "Investigation Report" |
| | 03_FRM_Risk.py | "FRM Risk Register" |
| | 04_DD.py | "Due Diligence" |
| | 05_Sanctions.py | "Sanctions Screening" |
| | 06_Transaction.py | "Transaction Testing" |
| | 08_Policy_SOP.py | "Policy / SOP" |
| | 10_Training.py | "Training Material" |
| | 11_PPT_Pack.py | "Proposal Deck" |
| | 13_Persona_Review.py | "Persona Review" |
| | 14_Settings.py | "Settings" |

**00_Setup.py:** Not registered in `st.navigation()`. Only reachable via `st.switch_page("pages/00_Setup.py")` from the bootstrap redirect. This prevents it appearing in the sidebar after setup is complete.

### app.py Structure (post-IA-02)

```python
# app.py
import streamlit as st
from streamlit_app.shared.session import bootstrap

try:
    session = bootstrap(st, caller_file=__file__)
except Exception as _bootstrap_err:
    st.error(f"App failed to load: {_bootstrap_err}")
    st.stop()

pg = st.navigation({
    "MAIN": [
        st.Page("pages/01_Engagements.py", title="Engagements"),
        st.Page("pages/16_Workspace.py", title="Workspace"),
    ],
    "PROPOSALS": [
        st.Page("pages/01b_Scope.py", title="Scope"),
        st.Page("pages/07_Proposal.py", title="Proposals"),
    ],
    "MONITOR": [
        st.Page("pages/09_Case_Tracker.py", title="Case Tracker"),
        st.Page("pages/15_Activity_Log.py", title="Activity Log"),
    ],
    "SETTINGS": [
        st.Page("pages/12_Team.py", title="Team"),
        st.Page("pages/14_Settings.py", title="Settings"),
    ],
    "WORKFLOWS": [
        st.Page("pages/02_Investigation.py", title="Investigation Report"),
        st.Page("pages/03_FRM_Risk.py", title="FRM Risk Register"),
        st.Page("pages/04_DD.py", title="Due Diligence"),
        st.Page("pages/05_Sanctions.py", title="Sanctions Screening"),
        st.Page("pages/06_Transaction.py", title="Transaction Testing"),
        st.Page("pages/08_Policy_SOP.py", title="Policy / SOP"),
        st.Page("pages/10_Training.py", title="Training Material"),
        st.Page("pages/11_PPT_Pack.py", title="Proposal Deck"),
        st.Page("pages/13_Persona_Review.py", title="Persona Review"),
    ],
})
pg.run()
```

**Note:** `st.switch_page()` calls in individual pages still work with `st.navigation()`. They must reference the file path string, not the page title.

---

## Multi-Workflow Engagement

### Data model (no schema change required)

`ProjectState.cases` already holds the multi-workflow mapping:

```python
class ProjectState(BaseModel):
    cases: dict[str, str] = {}  # workflow_type → case_id
```

For example, an engagement with three workflow runs:
```json
{
  "cases": {
    "investigation_report": "case_abc123",
    "frm_risk_register": "case_def456",
    "due_diligence": "case_ghi789"
  }
}
```

### Engagements page (IA-03 constraint)

The "Run Workflow" selectbox in `01_Engagements.py` must enumerate ALL workflow types, not filter by `engagement.service_type`. The `service_type` field on `ProjectState` records what Maher was retained for — it does not constrain future runs.

Existing workflows in `ProjectState.cases` should be shown in the engagement detail panel with a link to their latest output.

### Workspace page (IA-04 design)

`16_Workspace.py` iterates `ProjectState.cases` and renders one section per workflow run:

```
[Project: ABC Corp Fraud Investigation Q1 2026]
  ├── Investigation Report (case_abc123)
  │     Draft: E_Drafts/junior_output.v3.json  [Download]
  │     Final: F_Final/final_report.en.docx    [Download]
  ├── FRM Risk Register (case_def456)
  │     Final: F_Final/final_report.en.docx    [Download]
  └── Due Diligence (case_ghi789)
        Workstream added — not yet run. [Run Now]
```

**Note:** A project always has at least 1 workstream section (minimum enforced at creation). "Not yet run" is valid at the workstream level; an empty project-level view never occurs.

---

## State Flow

### Arc 1 — Proposal (stateless)
```
[Scope page] → conversational input → [no state written]
[Proposal page] → generate deck → [.pptx saved to firm_profile/proposals/]
```
No `ProjectState` is created. No case_id is allocated. Proposal outputs are firm-level, not case-level.

### Arc 2 — Engagement
```
Create Engagement
  → ProjectState(status=INTAKE_CREATED, cases={}) written to projects/{slug}/state.json
  → Audit event: engagement_created

Run Workflow (type T)
  → case_id allocated → projects/{slug}/state.json: cases[T] = case_id
  → Standard pipeline proceeds (Junior → PM → Partner or Mode B)
  → Audit events: per existing hook chain

Workspace
  → reads projects/{slug}/state.json.cases → renders per-workflow sections
```

---

## Rules and Validations

| Rule | Enforcement | Consequence |
|------|-------------|-------------|
| Project name required at creation | `01_Engagements.py` — `project_name` field cannot be empty | Form does not submit |
| Minimum 1 workstream at creation | `01_Engagements.py` — workstream selector validation | Form does not submit; error shown |
| Project required before any workflow run | `01_Engagements.py` — check `active_project` in session state | Redirect to Engagements page |
| `service_type` does not restrict workflow selection | `01_Engagements.py` — workflow selectbox shows all types | No restriction enforced |
| Workspace never shows empty project | `16_Workspace.py` — guaranteed by creation constraint | Not applicable — cannot occur |
| Proposal output is firm-level, not case-level | `07_Proposal.py` — no `ProjectState` write | Proposal deck saved to `firm_profile/proposals/` |
| `00_Setup` not in sidebar | `app.py st.navigation()` — page not registered | Page only reachable via redirect |
| `st.switch_page()` uses file path, not title | All pages — existing calls unchanged | No change needed — file paths still valid |

---

## Failure Handling

| Failure | Response | Recovery |
|---------|----------|----------|
| Bootstrap error in app.py | `st.error()` + `st.stop()` | User sees error panel, not blank crash |
| `ProjectState` missing for active engagement | `01_Engagements.py` — catch FileNotFoundError | Show "Engagement not found" + prompt to reselect |
| Workflow page opened without active engagement | Check `session_state.active_project` at page top | `st.switch_page("pages/01_Engagements.py")` |
| `st.navigation()` page path not found | Streamlit raises on startup | Fix: verify all file paths in navigation dict exist |

---

## Open Questions

None. All decisions confirmed by AK 2026-04-21.
