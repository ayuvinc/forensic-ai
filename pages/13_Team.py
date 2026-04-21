"""Team — Streamlit page (UX-D-04).

Reads and writes firm_profile/team.json.
Each member is a flat dict: name, title, credentials, bio.
"""

from __future__ import annotations

import json
import os
import time

import streamlit as st

from config import FIRM_PROFILE_DIR
from streamlit_app.shared.session import bootstrap

try:
    session = bootstrap(st, caller_file=__file__)
except Exception as _bootstrap_err:
    st.error(f"Page failed to load: {_bootstrap_err}")
    st.stop()

_TEAM_JSON = FIRM_PROFILE_DIR / "team.json"


def _load_team() -> tuple[list[dict], bool]:
    """Read firm_profile/team.json.

    Returns (members, corrupt).
    - members=[]   when absent (normal first-run) or corrupt.
    - corrupt=True only when file exists but cannot be parsed as a JSON array.
    """
    if not _TEAM_JSON.exists():
        return [], False
    try:
        data = json.loads(_TEAM_JSON.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return [], True
        return data, False
    except json.JSONDecodeError:
        return [], True


def _save_team(members: list[dict]) -> str | None:
    """Atomically write firm_profile/team.json.

    Uses .tmp → os.replace() so a process kill mid-write leaves a .tmp file,
    never a corrupt team.json.
    Returns None on success, error string on failure.
    """
    try:
        FIRM_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        tmp = _TEAM_JSON.with_suffix(".tmp")
        tmp.write_text(json.dumps(members, indent=2), encoding="utf-8")
        os.replace(tmp, _TEAM_JSON)
        return None
    except Exception as exc:
        return str(exc)


# ── Session state ──────────────────────────────────────────────────────────────
# team_members: list of dicts, each with a stable _id used as widget key suffix.
# _next_id: monotonic counter — never reused, so Remove + Add never collides keys.
# Loading happens once per browser session (or after a save-triggered reload).
if "team_members" not in st.session_state:
    with st.spinner("Loading team..."):
        raw, corrupt = _load_team()
    st.session_state.team_corrupt = corrupt
    st.session_state.team_members = [{"_id": i, **m} for i, m in enumerate(raw)]
    st.session_state._next_id = len(raw)

if "team_error" not in st.session_state:
    st.session_state.team_error = None
if "team_saved" not in st.session_state:
    st.session_state.team_saved = False

# ── Page header ────────────────────────────────────────────────────────────────
st.title("Team")
st.caption("Team bios — used in proposals and deliverables.")

# File-state banner — shown before content so user knows what to expect
if st.session_state.get("team_corrupt"):
    st.warning(
        "Team file could not be loaded. Adding members below will overwrite the existing file."
    )

# ── Success banner ─────────────────────────────────────────────────────────────
# Rendered before the member list; auto-clears after 3 s (consistent with Settings page).
if st.session_state.team_saved:
    placeholder = st.empty()
    placeholder.success("Team saved.")
    time.sleep(3)
    placeholder.empty()
    st.session_state.team_saved = False

# ── Member count / empty state ─────────────────────────────────────────────────
members = st.session_state.team_members
count = len(members)

if count > 0:
    st.caption(f"{count} team member{'s' if count != 1 else ''}")
else:
    st.info("No team members yet. Click 'Add Member' below to get started.")

# ── Member expanders ───────────────────────────────────────────────────────────
# Each member gets a stable _id so widget keys survive Add/Remove reruns.
for member in members:
    mid = member["_id"]
    # Use live widget value for label when available so edits reflect immediately on rerun
    current_name = st.session_state.get(f"team_name_{mid}", member.get("name", "")).strip()
    label = current_name if current_name else "New Member"

    # _new flag: newly added members open expanded; existing members start collapsed
    with st.expander(label, expanded=member.get("_new", False)):
        st.text_input("Name *", key=f"team_name_{mid}", value=member.get("name", ""))
        st.text_input("Title", key=f"team_title_{mid}", value=member.get("title", ""))
        st.text_input(
            "Credentials",
            key=f"team_credentials_{mid}",
            value=member.get("credentials", ""),
            help="e.g. CFE, CPA, CAMS",
        )
        st.text_area(
            "Bio",
            key=f"team_bio_{mid}",
            value=member.get("bio", ""),
            height=120,
        )

        if st.button("Remove", key=f"team_remove_{mid}"):
            # Remove from session state — does NOT write to disk until Save is clicked (RM-2)
            st.session_state.team_members = [
                m for m in st.session_state.team_members if m["_id"] != mid
            ]
            st.rerun()

st.divider()

# ── Add Member ─────────────────────────────────────────────────────────────────
if st.button("Add Member", key="team_add"):
    new_id = st.session_state._next_id
    st.session_state._next_id += 1
    st.session_state.team_members.append(
        {"_id": new_id, "name": "", "title": "", "credentials": "", "bio": "", "_new": True}
    )
    st.rerun()

# ── Save ───────────────────────────────────────────────────────────────────────
# Save is always enabled — saving zero members is valid (clears the team list).
if st.button("Save", type="primary", key="team_save"):
    members_to_save = []
    blank_count = 0

    for m in st.session_state.team_members:
        mid = m["_id"]
        name        = st.session_state.get(f"team_name_{mid}",        "").strip()
        title       = st.session_state.get(f"team_title_{mid}",       "").strip()
        credentials = st.session_state.get(f"team_credentials_{mid}", "").strip()
        bio         = st.session_state.get(f"team_bio_{mid}",         "").strip()

        if name:
            members_to_save.append(
                {"name": name, "title": title, "credentials": credentials, "bio": bio}
            )
        else:
            blank_count += 1

    # SV-2: warn about blank-name entries that will be skipped
    if blank_count > 0:
        st.warning(
            f"{blank_count} member{'s' if blank_count > 1 else ''} with no name "
            "will not be saved — add a name or use Remove first."
        )

    err = _save_team(members_to_save)

    if err:
        st.session_state.team_error = err
    else:
        st.session_state.team_error = None
        st.session_state.team_saved = True
        # Clear team session state so next render re-reads the saved file
        for key in ["team_members", "_next_id", "team_corrupt"]:
            st.session_state.pop(key, None)
        st.rerun()

# ── Error banner ───────────────────────────────────────────────────────────────
if st.session_state.team_error:
    st.error(f"Save failed: {st.session_state.team_error}")
    if st.button("Try Again", key="team_retry"):
        # Clear error; widget values preserved in session_state — no data loss
        st.session_state.team_error = None
