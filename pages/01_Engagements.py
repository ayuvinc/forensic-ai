"""Engagements — two-panel named engagement home (P9-UI-01, UX-012).

Left panel  (1/3): engagement card list + "New Engagement" button.
Right panel (2/3): selected engagement detail — cases, "Run New Workflow" button.

New Engagement wizard: multi-field form, slug preview, collision detection.
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from config import CASES_DIR
from schemas.project import ProjectIntake, derive_slug
from streamlit_app.shared.session import bootstrap
from tools.project_manager import AF_FOLDERS, ProjectManager

session = bootstrap(st)
pm = ProjectManager()

# ── Constants ─────────────────────────────────────────────────────────────────
_LANG_LABELS = {
    "acfe":           "ACFE Internal Review",
    "expert_witness": "Expert Witness",
    "regulatory":     "Regulatory Submission",
    "board_pack":     "Board Pack",
}

_SERVICE_TYPES = [
    "Investigation Report",
    "FRM Risk Register",
    "Due Diligence",
    "Sanctions Screening",
    "Transaction Testing",
    "Policy / SOP",
    "Training Material",
    "Client Proposal",
]

_HEALTH_DOT = {"green": "🟢", "amber": "🟡", "red": "🔴"}

_WORKFLOW_PAGE = {
    "Investigation Report": "pages/02_Investigation.py",
    "FRM Risk Register":    "pages/06_FRM.py",
    "Due Diligence":        "pages/09_Due_Diligence.py",
    "Sanctions Screening":  "pages/10_Sanctions.py",
    "Transaction Testing":  "pages/11_Transaction_Testing.py",
    "Policy / SOP":         "pages/04_Policy_SOP.py",
    "Training Material":    "pages/05_Training.py",
    "Client Proposal":      "pages/07_Proposal.py",
}


# ── Helper: New Engagement wizard ─────────────────────────────────────────────

def _render_wizard() -> None:
    st.subheader("New Engagement")

    project_name = st.text_input(
        "Engagement name *",
        placeholder="e.g. Alpha Corp FRM 2026",
        key="new_eng_name",
    )

    preview_slug: str | None = None
    collision = False
    if project_name.strip():
        try:
            preview_slug = derive_slug(project_name)
            collision = pm.detect_slug_collision(preview_slug)
            st.caption(
                f"Folder: `cases/{preview_slug}/`  "
                + ("⚠️ name already exists" if collision else "✓ available")
            )
        except ValueError as exc:
            st.caption(f"⚠️ {exc}")

    client_name = st.text_input("Client name *", key="new_eng_client")

    service_type = st.selectbox("Service type *", _SERVICE_TYPES, key="new_eng_svc")

    lang_std = st.selectbox(
        "Language standard *",
        options=list(_LANG_LABELS.keys()),
        format_func=lambda k: _LANG_LABELS[k],
        key="new_eng_lang",
    )

    st.text_input(
        "Naming convention",
        placeholder=f"{(client_name or 'Client').split()[0]}_{service_type.replace(' ', '')}",
        key="new_eng_naming",
    )

    st.divider()

    if collision and preview_slug:
        st.warning(f"An engagement named '{project_name}' already exists.")
        if st.button("Open existing engagement", key="open_existing"):
            st.session_state.eng_selected = preview_slug
            st.session_state.eng_wizard   = False
            st.rerun()
        return

    can_create = bool(project_name.strip() and client_name.strip() and preview_slug)

    if st.button("Create Engagement", type="primary", disabled=not can_create, key="create_btn"):
        try:
            intake = ProjectIntake(
                project_name=project_name.strip(),
                client_name=client_name.strip(),
                service_type=service_type,
                language_standard=lang_std,
                naming_convention=st.session_state.get("new_eng_naming", "").strip() or "acfe",
            )
            pm.create_project(intake)
            st.success(f"Engagement created: `cases/{intake.project_slug}/`")
            st.markdown("**Folders created:**")
            for folder in AF_FOLDERS:
                st.markdown(f"  - `{folder}/`")
            st.session_state.eng_selected = intake.project_slug
            st.session_state.eng_wizard   = False
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Failed to create engagement: {exc}")

    if st.button("Cancel", key="cancel_wizard"):
        st.session_state.eng_wizard = False
        st.rerun()


# ── Helper: engagement detail ─────────────────────────────────────────────────

def _render_detail(slug: str, named_entries: list) -> None:
    entry = next((e for e in named_entries if e.get("case_id") == slug), None)
    if not entry:
        st.warning(f"Engagement `{slug}` not found in index.")
        return

    name   = entry.get("project_name") or slug
    client = entry.get("client_name", "")
    stype  = entry.get("service_type") or entry.get("workflow", "")
    lang   = entry.get("language_standard", "acfe")
    health = entry.get("project_health", "green")

    st.subheader(f"{_HEALTH_DOT.get(health, '')} {name}")
    st.caption(
        f"Client: **{client}** · Service: {stype} · "
        f"Language: {_LANG_LABELS.get(lang, lang)}"
    )

    # A-F folder tree
    cdir = CASES_DIR / slug
    if cdir.exists():
        with st.expander("Project folder structure", expanded=False):
            for folder in AF_FOLDERS:
                fpath = cdir / folder
                if fpath.exists():
                    files = list(fpath.iterdir())
                    st.markdown(
                        f"`{folder}/`  ({len(files)} item{'s' if len(files) != 1 else ''})"
                    )
                    for f in sorted(files)[:5]:
                        size = (
                            f"{f.stat().st_size / 1024:.1f} KB" if f.is_file() else "dir"
                        )
                        st.markdown(f"&nbsp;&nbsp;&nbsp;`{f.name}` — {size}")
                    if len(files) > 5:
                        st.caption(f"  ... and {len(files) - 5} more")

    # Registered workflow cases
    state = pm.get_project(slug)
    cases_dict = state.cases if state else {}
    st.subheader("Workflows")
    if cases_dict:
        for wf_type, case_id in cases_dict.items():
            st.markdown(f"- **{wf_type}** → case `{case_id}`")
    else:
        st.caption("No workflows run yet for this engagement.")

    # Open Workspace (P9-05)
    if st.button("Open Workspace", key=f"open_ws_{slug}"):
        st.session_state["active_project"] = slug
        try:
            st.switch_page("pages/16_Workspace.py")
        except Exception:
            st.info("Navigate to **Workspace** in the sidebar (engagement is now active).")

    # Run New Workflow
    st.divider()
    st.markdown("**Run a workflow for this engagement:**")
    wf_choice = st.selectbox("Select workflow", _SERVICE_TYPES, key=f"wf_sel_{slug}")
    if st.button("Run Workflow", type="primary", key=f"run_wf_{slug}"):
        st.session_state["active_project"] = slug
        page = _WORKFLOW_PAGE.get(wf_choice)
        if page and Path(page).exists():
            try:
                st.switch_page(page)
            except Exception:
                st.info(f"Navigate to **{wf_choice}** in the sidebar (engagement `{slug}` is now active).")
        else:
            st.info(f"Navigate to **{wf_choice}** in the sidebar (engagement `{slug}` is now active).")

    # Context summary footer
    ctx = pm.get_context_summary(slug)
    st.divider()
    st.caption(
        f"Documents: {ctx['document_count']}  |  "
        f"Context used: {ctx['context_budget_used_pct']:.0f}%  |  "
        f"Interim context: {'written' if ctx['interim_context_written'] else 'not yet written'}"
    )


# ── Page ──────────────────────────────────────────────────────────────────────

if "eng_selected" not in st.session_state:
    st.session_state.eng_selected = None
if "eng_wizard" not in st.session_state:
    st.session_state.eng_wizard = False

st.title("Engagements")
st.caption("Manage all active and completed forensic engagements.")

entries    = pm.list_projects()
named      = [e for e in entries if e.get("is_af_project")]
legacy     = [e for e in entries if not e.get("is_af_project")]

left, right = st.columns([1, 2])

# ── Left panel ────────────────────────────────────────────────────────────────
with left:
    st.subheader("Active Engagements")

    if st.button("＋ New Engagement", type="primary", use_container_width=True, key="new_btn"):
        st.session_state.eng_wizard   = True
        st.session_state.eng_selected = None

    if not named and not st.session_state.eng_wizard:
        st.info("No engagements yet. Start your first engagement.")

    for e in sorted(named, key=lambda x: x.get("last_updated", ""), reverse=True):
        slug    = e.get("case_id", "")
        name    = e.get("project_name") or slug
        client  = e.get("client_name", "")
        stype   = e.get("service_type") or e.get("workflow", "")
        health  = e.get("project_health", "green")
        updated = (e.get("last_updated") or "")[:10]

        label = (
            f"{_HEALTH_DOT.get(health, '⚪')} **{name}**  \n"
            f"{client} · {stype}  \n*{updated}*"
        )
        if st.button(label, key=f"card_{slug}", use_container_width=True):
            st.session_state.eng_selected = slug
            st.session_state.eng_wizard   = False

    if legacy:
        with st.expander(f"Legacy Cases ({len(legacy)})", expanded=False):
            for e in legacy:
                cid  = e.get("case_id", "")
                wf   = e.get("workflow", "")
                stat = e.get("status", "")
                st.caption(f"`{cid[:20]}` — {wf} — {stat}")

# ── Right panel ───────────────────────────────────────────────────────────────
with right:
    if st.session_state.eng_wizard:
        _render_wizard()
    elif st.session_state.eng_selected:
        _render_detail(st.session_state.eng_selected, named)
    else:
        st.markdown("### Select an engagement or create a new one.")
        st.info("Click an engagement card on the left, or press **＋ New Engagement**.")
