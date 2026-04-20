import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from config import CASES_DIR

# Write-through index for Case Tracker — O(1) read instead of O(n) dir scan
_INDEX_PATH = CASES_DIR / "index.json"

# ── A-F folder structure (P9-04a) ────────────────────────────────────────────
# Present in all Phase 9 named projects; absent in legacy UUID cases.
AF_FOLDERS = (
    "A_Engagement_Management",
    "B_Planning",
    "C_Evidence",
    "D_Working_Papers",
    "E_Drafts",
    "F_Final",
)


def case_dir(case_id: str) -> Path:
    """Return (and create) the directory for a given case.

    Raises ValueError if case_id contains path traversal sequences (R-019).
    """
    d = CASES_DIR / case_id
    # Block traversal: resolved path must stay inside CASES_DIR
    try:
        d.resolve().relative_to(CASES_DIR.resolve())
    except ValueError:
        raise ValueError(
            f"Invalid case_id — path traversal attempt blocked: {case_id!r}"
        )
    d.mkdir(parents=True, exist_ok=True)
    return d


def is_af_project(case_id: str) -> bool:
    """Return True if this case uses the A-F folder structure (Phase 9 named project).

    Detection: E_Drafts/ exists inside the case folder.
    Legacy UUID cases (Phase 8 and earlier) never have this folder.
    """
    return (CASES_DIR / case_id / "E_Drafts").exists()


def get_final_report_path(case_id: str, language: str = "en") -> Path:
    """Return the correct path for the final report (.md), accounting for AF vs legacy structure.

    P9-09c: AF projects store reports in F_Final/; legacy projects store in case root.
    Use this instead of case_dir(case_id) / "final_report.en.md" in all done stages.
    """
    if is_af_project(case_id):
        return CASES_DIR / case_id / "F_Final" / f"final_report.{language}.md"
    return CASES_DIR / case_id / f"final_report.{language}.md"


def artifact_path(case_id: str, agent: str, artifact_type: str, version: int) -> Path:
    """Return the canonical path for a versioned artifact.

    AF projects (P9-04c): artifacts land in E_Drafts/ subfolder.
    Legacy projects: artifacts land in case root (unchanged).
    Naming: {agent}_{artifact_type}.v{N}.json
    """
    filename = f"{agent}_{artifact_type}.v{version}.json"
    if is_af_project(case_id):
        drafts_dir = case_dir(case_id) / "E_Drafts"
        drafts_dir.mkdir(exist_ok=True)
        return drafts_dir / filename
    return case_dir(case_id) / filename


def next_version(case_id: str, agent: str, artifact_type: str) -> int:
    """Return the next available version number for an artifact.

    AF projects scan E_Drafts/; legacy projects scan case root.
    """
    # P9-04c: AF projects store artifacts in E_Drafts/
    if is_af_project(case_id):
        d = case_dir(case_id) / "E_Drafts"
        d.mkdir(exist_ok=True)
    else:
        d = case_dir(case_id)
    existing = list(d.glob(f"{agent}_{artifact_type}.v*.json"))
    if not existing:
        return 1
    versions = []
    for p in existing:
        try:
            v = int(p.stem.split(".v")[-1])
            versions.append(v)
        except ValueError:
            pass
    return max(versions) + 1 if versions else 1


def write_artifact(case_id: str, agent: str, artifact_type: str, data: Any, version: int | None = None) -> Path:
    """Atomically write a versioned JSON artifact.

    Writes to a .tmp file first, then os.replace() to prevent partial writes.
    Returns the final path.
    """
    if version is None:
        version = next_version(case_id, agent, artifact_type)

    target = artifact_path(case_id, agent, artifact_type, version)
    tmp    = target.with_suffix(".tmp")

    payload = data if isinstance(data, str) else json.dumps(data, indent=2, default=str)

    tmp.write_text(payload, encoding="utf-8")
    os.replace(tmp, target)

    # ACT-02: log pipeline artifact write as DOCUMENT event
    try:
        from tools.activity_logger import logger as _act_logger
        _act_logger.log(
            category="DOCUMENT",
            action="artifact_written",
            actor=agent,
            case_id=case_id,
            detail={"artifact_type": artifact_type, "version": version},
        )
    except Exception:
        pass

    return target


def _update_case_index(
    case_id: str,
    workflow: str,
    status: str,
    last_updated: str,
    client_name: str = "",
    engagement_id: str = "",
) -> None:
    """Upsert one entry in cases/index.json by case_id.

    Index exists so Case Tracker reads O(1) from a single file rather than
    scanning O(n) case directories. Written atomically via .tmp → os.replace().
    Contains no PHI — only case_id, workflow, status, last_updated, client_name, engagement_id.

    Raises ValueError if index.json exists but is corrupt JSON.
    """
    if _INDEX_PATH.exists():
        try:
            entries: list[dict] = json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"cases/index.json is corrupt — fix or delete it: {exc}") from exc
    else:
        entries = []

    entry = {
        "case_id":       case_id,
        "workflow":      workflow,
        "status":        status,
        "last_updated":  last_updated,
        "client_name":   client_name,
        "engagement_id": engagement_id,
    }

    # Upsert: replace in-place to preserve ordering of existing entries
    updated = False
    for i, e in enumerate(entries):
        if e.get("case_id") == case_id:
            entries[i] = entry
            updated = True
            break
    if not updated:
        entries.append(entry)

    tmp = _INDEX_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    os.replace(tmp, _INDEX_PATH)


def build_case_index() -> Path:
    """Backfill cases/index.json by scanning all cases/*/state.json files.

    Called when index.json is missing. Idempotent — safe to call multiple times.
    Skips case dirs where state.json is absent or malformed (does not crash).
    Returns the path to cases/index.json.
    """
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    entries: list[dict] = []

    for state_path in sorted(CASES_DIR.glob("*/state.json")):
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue  # skip corrupt or unreadable state files

        case_id = state.get("case_id") or state_path.parent.name
        if not case_id:
            continue

        entries.append({
            "case_id":       case_id,
            "workflow":      state.get("workflow", ""),
            "status":        state.get("status", ""),
            "last_updated":  state.get("last_updated", ""),
            "client_name":   state.get("client_name", ""),
            "engagement_id": state.get("engagement_id", ""),
        })

    tmp = _INDEX_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    os.replace(tmp, _INDEX_PATH)
    return _INDEX_PATH


def write_state(case_id: str, state: dict) -> Path:
    """Atomically write case state.json, then update cases/index.json."""
    target = case_dir(case_id) / "state.json"
    tmp    = target.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, target)

    # Update write-through index after state.json is safely persisted.
    # Index failure is non-fatal (Case Tracker can backfill) — log and continue.
    try:
        _update_case_index(
            case_id=case_id,
            workflow=state.get("workflow", ""),
            status=state.get("status", ""),
            last_updated=state.get("last_updated", datetime.now(timezone.utc).isoformat()),
            client_name=state.get("client_name", ""),
            engagement_id=state.get("engagement_id", ""),
        )
    except Exception as exc:
        print(f"[WARN] case index update failed for {case_id}: {exc}", file=sys.stderr)

    return target


def read_state(case_id: str) -> dict | None:
    """Read case state.json. Returns None if not found."""
    path = case_dir(case_id) / "state.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def append_audit_event(case_id: str, event: dict) -> None:
    """Append one JSON line to audit_log.jsonl (append-only, never mutate)."""
    log_path = case_dir(case_id) / "audit_log.jsonl"
    event.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, default=str) + "\n")


def write_envelope(
    case_id: str,
    role: str,
    artifact_type: str,
    payload: dict,
    workflow: str,
    status: str,
    tool_calls_made: Optional[list[str]] = None,
    revision_round: int = 0,
    version: Optional[int] = None,
) -> Path:
    """Wrap payload in ArtifactEnvelope and write atomically.

    This is the canonical persistence path for agent outputs.
    post_hooks.persist_artifact calls this instead of write_artifact directly.
    """
    from schemas.plugins import ArtifactEnvelope

    v = version or next_version(case_id, role, artifact_type)
    envelope = ArtifactEnvelope(
        case_id=case_id,
        agent=role,
        role=role,
        artifact_type=artifact_type,
        version=v,
        workflow=workflow,
        status=status,
        payload=payload,
        created_at=datetime.now(timezone.utc),
        tool_calls_made=tool_calls_made or [],
        revision_round=revision_round,
    )
    return write_artifact(case_id, role, artifact_type, envelope.model_dump(), v)


def load_envelope(case_id: str, role: str, artifact_type: str) -> Optional[dict]:
    """Load the latest ArtifactEnvelope for a given role+artifact_type.

    AF projects (P9-04c): searches E_Drafts/ first, then case root as fallback.
    Returns the payload dict (not the full envelope) for uniform resume semantics.
    Returns None if no artifact found.
    """
    import glob as _glob

    cdir = case_dir(case_id)
    glob_name = f"{role}_{artifact_type}.v*.json"

    if is_af_project(case_id):
        # Primary location for AF projects
        files = sorted(_glob.glob(str(cdir / "E_Drafts" / glob_name)))
        if not files:
            # Fallback: root (pre-migration artifacts)
            files = sorted(_glob.glob(str(cdir / glob_name)))
    else:
        files = sorted(_glob.glob(str(cdir / glob_name)))

    if not files:
        return None
    data = json.loads(open(files[-1], encoding="utf-8").read())
    # Support both envelope format and bare payload
    if "payload" in data:
        return data["payload"]
    return data


def mark_deliverable_written(case_id: str, workflow: str) -> None:
    """Advance case state to DELIVERABLE_WRITTEN (terminal).

    Called by both run.py (CLI) and Streamlit pages after a workflow completes.
    Extracted from run.py so Streamlit pages can import it without importing the
    CLI entry point.
    """
    from core.state_machine import CaseStatus
    from datetime import datetime, timezone

    state = read_state(case_id) or {}
    state["status"] = CaseStatus.DELIVERABLE_WRITTEN.value
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    write_state(case_id, state)
    append_audit_event(case_id, {"event": "deliverable_written", "workflow": workflow})

    # ACT-02: log final deliverable write
    try:
        from tools.activity_logger import logger as _act_logger
        _act_logger.log(
            category="DELIVERABLE",
            action="deliverable_written",
            actor="system",
            case_id=case_id,
            detail={"workflow": workflow},
        )
    except Exception:
        pass


def _version_existing_report(case_id: str) -> int:
    """Move existing final_report.* files to Previous_Versions/final_report.v{N}.* (RD-04).

    Called by write_final_report() before each write to preserve prior outputs.
    Creates Previous_Versions/ if missing.
    Returns the highest version number used (0 if nothing was moved).
    """
    import shutil as _shutil

    if is_af_project(case_id):
        search_dir = case_dir(case_id) / "F_Final"
    else:
        search_dir = case_dir(case_id)

    if not search_dir.exists():
        return 0

    existing = list(search_dir.glob("final_report.*"))
    if not existing:
        return 0

    # Find the highest existing version in Previous_Versions/ to set next N
    prev_dir = search_dir / "Previous_Versions"
    prev_dir.mkdir(exist_ok=True)

    existing_versions = []
    for p in prev_dir.glob("final_report.v*.*"):
        # Pattern: final_report.v{N}.{ext} or final_report.v{N}.{lang}.{ext}
        parts = p.name.split(".")
        for part in parts:
            if part.startswith("v") and part[1:].isdigit():
                existing_versions.append(int(part[1:]))
                break

    next_v = max(existing_versions, default=0) + 1

    for f in existing:
        # Build versioned name: insert v{N} before extension(s)
        # e.g. final_report.en.md → final_report.v1.en.md
        stem = f.name  # e.g. "final_report.en.md" or "final_report.en.docx"
        versioned_name = stem.replace("final_report.", f"final_report.v{next_v}.", 1)
        try:
            _shutil.move(str(f), str(prev_dir / versioned_name))
        except Exception:
            pass  # best-effort — leave in place, no data loss

    return next_v


def write_final_report(
    case_id: str,
    content: str,
    language: str = "en",
    workflow: str = "",
    section_overrides: Optional[dict] = None,
) -> Path:
    """Write final_report.{language}.md and final_report.{language}.docx atomically.

    RD-03: Uses BaseReportBuilder for .docx; loads template from firm.json if set.
    RD-04: Calls _version_existing_report() before writing to preserve prior outputs.
    P9-04c: AF projects write to F_Final/; legacy projects write to case root.
    P9-04d: migration — AF projects move root *.v*.json → E_Drafts/;
            legacy projects move *.v*.json → interim/ (unchanged).
    Permanent files never migrated: state.json, audit_log.jsonl,
    citations_index.json, intake.json, document_index.json.

    Args:
        section_overrides: Optional dict with keys "cover" and "sections" to drive
            structured .docx output via BaseReportBuilder.
            "cover": {title, subtitle, metadata}
            "sections": [{heading, content, level (1|2)}]
    """
    import shutil

    cdir = case_dir(case_id)

    # P9-04c: AF projects write to F_Final/, legacy to case root
    if is_af_project(case_id):
        final_dir = cdir / "F_Final"
        final_dir.mkdir(exist_ok=True)
    else:
        final_dir = cdir

    # RD-04: version any existing final reports before overwriting
    _version_existing_report(case_id)

    # Write Markdown (unchanged from pre-RD-03)
    target = final_dir / f"final_report.{language}.md"
    tmp    = target.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, target)

    # RD-03: produce .docx via BaseReportBuilder (replaces OutputGenerator)
    try:
        from tools.report_builder import BaseReportBuilder

        # Load template from firm.json["templates"][workflow] if available
        template_path = _resolve_template(workflow)

        builder = BaseReportBuilder(template_path=template_path)
        docx_path = final_dir / f"final_report.{language}.docx"

        if section_overrides:
            # Structured build: cover page + sections list
            cover = section_overrides.get("cover", {})
            if cover:
                builder.add_cover_page(
                    title=cover.get("title", "Report"),
                    subtitle=cover.get("subtitle", ""),
                    metadata=cover.get("metadata"),
                )
                builder.add_toc()
            for sec in section_overrides.get("sections", []):
                if sec.get("level", 1) == 2:
                    builder.add_subsection(sec.get("heading", ""), sec.get("content", ""))
                else:
                    builder.add_section(sec.get("heading", ""), sec.get("content", ""))
        else:
            # Fallback: write raw markdown content as body text
            builder.add_section("Report", content)

        builder.save(docx_path)
    except Exception:
        pass

    # P9-04d: migrate root-level pipeline artifacts to their archive folder
    # AF projects → E_Drafts/; legacy projects → interim/ (FE-08 behaviour)
    _KEEP_IN_ROOT = {
        "state.json", "audit_log.jsonl", "citations_index.json",
        "intake.json", "document_index.json",
    }
    versioned = [p for p in cdir.glob("*.v*.json") if p.name not in _KEEP_IN_ROOT]
    if versioned:
        if is_af_project(case_id):
            archive_dir = cdir / "E_Drafts"  # AF projects archive to E_Drafts
        else:
            archive_dir = cdir / "interim"   # legacy projects archive to interim
        archive_dir.mkdir(exist_ok=True)
        for artifact in versioned:
            try:
                shutil.move(str(artifact), str(archive_dir / artifact.name))
            except Exception:
                pass  # best-effort — artifact remains in root, no data loss

    return target


def _resolve_template(workflow: str) -> Optional[Path]:
    """Return template path from firm.json["templates"][workflow], or None."""
    try:
        import json as _json
        from config import FIRM_PROFILE_DIR
        firm_json = FIRM_PROFILE_DIR / "firm.json"
        if not firm_json.exists():
            return None
        data = _json.loads(firm_json.read_text(encoding="utf-8"))
        tpl_name = data.get("templates", {}).get(workflow)
        if not tpl_name:
            return None
        from config import BASE_DIR
        tpl_path = BASE_DIR / "templates" / tpl_name
        return tpl_path if tpl_path.exists() else None
    except Exception:
        return None
