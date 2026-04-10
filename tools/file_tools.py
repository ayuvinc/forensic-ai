import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from config import CASES_DIR


def case_dir(case_id: str) -> Path:
    """Return (and create) the directory for a given case."""
    d = CASES_DIR / case_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def artifact_path(case_id: str, agent: str, artifact_type: str, version: int) -> Path:
    """Return the canonical path for a versioned artifact.

    Naming: {agent}_{artifact_type}.v{N}.json
    Example: junior_draft.v1.json
    """
    return case_dir(case_id) / f"{agent}_{artifact_type}.v{version}.json"


def next_version(case_id: str, agent: str, artifact_type: str) -> int:
    """Return the next available version number for an artifact."""
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
    return target


def write_state(case_id: str, state: dict) -> Path:
    """Atomically write case state.json."""
    target = case_dir(case_id) / "state.json"
    tmp    = target.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, target)
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

    Returns the payload dict (not the full envelope) for uniform resume semantics.
    Returns None if no artifact found.
    """
    import glob as _glob

    pattern = str(case_dir(case_id) / f"{role}_{artifact_type}.v*.json")
    files = sorted(_glob.glob(pattern))
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


def write_final_report(case_id: str, content: str, language: str = "en") -> Path:
    """Write final_report.{language}.md and final_report.{language}.docx atomically.

    After writing, moves all *.v*.json pipeline artifacts to cases/{id}/interim/
    so the case root contains only the deliverable and permanent files.
    Permanent files kept in root: final_report.*, state.json, audit_log.jsonl,
    citations_index.json, intake.json, document_index.json.
    """
    import shutil

    target = case_dir(case_id) / f"final_report.{language}.md"
    tmp    = target.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, target)

    # Word document — apply firm branding template if available (FE-09)
    try:
        from tools.output_generator import OutputGenerator
        from pathlib import Path as _Path
        docx_path = case_dir(case_id) / f"final_report.{language}.docx"
        template = _Path("firm_profile/template.docx")
        OutputGenerator().generate_docx(
            content,
            docx_path,
            template_path=template if template.exists() else None,
        )
    except Exception:
        pass

    # FE-08: move pipeline artifacts to interim/ subfolder (best-effort, non-atomic)
    # Keeps case root clean — only deliverables and permanent files remain at root level
    _KEEP_IN_ROOT = {
        "state.json", "audit_log.jsonl", "citations_index.json",
        "intake.json", "document_index.json",
    }
    cdir = case_dir(case_id)
    interim = cdir / "interim"

    versioned = [
        p for p in cdir.glob("*.v*.json")
        if p.name not in _KEEP_IN_ROOT
    ]
    if versioned:
        interim.mkdir(exist_ok=True)
        for artifact in versioned:
            try:
                shutil.move(str(artifact), str(interim / artifact.name))
            except Exception:
                pass  # best-effort — artifact remains in root, no data loss

    return target
