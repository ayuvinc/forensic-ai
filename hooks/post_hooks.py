"""Post-hooks — run in order after each agent produces output.

Each hook: (payload: dict, context: dict) -> dict
Raise HookVetoError to block persistence.

Order:
  1. validate_schema     — blocking: output must match expected Pydantic model
  2. persist_artifact    — atomic write to cases/{id}/{agent}.v{N}.json
  3. append_audit_event  — append one line to audit_log.jsonl
  4. extract_citations   — merge new citations into citations_index.json
  5. render_markdown     — write human-readable .md alongside the JSON artifact
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

from core.hook_engine import HookVetoError
from tools.file_tools import (
    append_audit_event,
    case_dir,
    write_artifact,
)


# ── 1. validate_schema ────────────────────────────────────────────────────────

def validate_schema(payload: dict, context: dict) -> dict:
    """Block if context supplies a schema class and payload fails validation."""
    schema_cls = context.get("schema_cls")
    if schema_cls is None:
        return payload
    try:
        schema_cls(**payload.get("output", payload))
    except ValidationError as e:
        raise HookVetoError("validate_schema", str(e))
    return payload


# ── 2. persist_artifact ───────────────────────────────────────────────────────

def persist_artifact(payload: dict, context: dict) -> dict:
    """Atomically write agent output to cases/{case_id}/{agent}_{type}.v{N}.json."""
    case_id       = context.get("case_id") or payload.get("case_id")
    agent         = context.get("agent", "unknown")
    artifact_type = context.get("artifact_type", "output")
    version       = context.get("version")

    if not case_id:
        raise HookVetoError("persist_artifact", "case_id missing from context and payload")

    data = payload.get("output", payload)
    path = write_artifact(case_id, agent, artifact_type, data, version)
    payload["_artifact_path"] = str(path)
    return payload


# ── 3. append_audit_event ─────────────────────────────────────────────────────

def append_audit_event_hook(payload: dict, context: dict) -> dict:
    """Append one audit event to audit_log.jsonl."""
    case_id = context.get("case_id") or payload.get("case_id")
    if not case_id:
        return payload

    event = {
        "event":    context.get("event", "agent_output"),
        "agent":    context.get("agent", "unknown"),
        "workflow": context.get("workflow") or payload.get("workflow"),
        "artifact": payload.get("_artifact_path"),
        "status":   context.get("status", "ok"),
    }
    append_audit_event(case_id, event)
    return payload


# ── 4. extract_citations ──────────────────────────────────────────────────────

def extract_citations(payload: dict, context: dict) -> dict:
    """Merge new citations from payload into citations_index.json."""
    case_id = context.get("case_id") or payload.get("case_id")
    if not case_id:
        return payload

    output = payload.get("output", payload)
    new_citations: list[dict] = []

    # support both top-level 'citations' and nested inside 'output'
    for src in (output, payload):
        if isinstance(src, dict):
            new_citations.extend(src.get("citations", []))
        elif isinstance(src, list):
            new_citations.extend(src)

    if not new_citations:
        return payload

    index_path = case_dir(case_id) / "citations_index.json"
    existing: list[dict] = []
    if index_path.exists():
        existing = json.loads(index_path.read_text(encoding="utf-8"))

    # deduplicate by source_url
    seen = {c["source_url"] for c in existing if "source_url" in c}
    for c in new_citations:
        c_dict = c if isinstance(c, dict) else c.model_dump() if hasattr(c, "model_dump") else {}
        if c_dict.get("source_url") and c_dict["source_url"] not in seen:
            existing.append(c_dict)
            seen.add(c_dict["source_url"])

    tmp = index_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(existing, indent=2, default=str), encoding="utf-8")
    import os; os.replace(tmp, index_path)
    return payload


# ── 5. render_markdown ────────────────────────────────────────────────────────

def render_markdown(payload: dict, context: dict) -> dict:
    """Write a human-readable .md file alongside the JSON artifact."""
    artifact_path = payload.get("_artifact_path")
    if not artifact_path:
        return payload

    p = Path(artifact_path)
    md_path = p.with_suffix(".md")
    output = payload.get("output", payload)

    lines = [f"# Artifact: {p.stem}", ""]
    if isinstance(output, dict):
        for key, value in output.items():
            if key.startswith("_"):
                continue
            lines.append(f"## {key.replace('_', ' ').title()}")
            if isinstance(value, list):
                for item in value:
                    lines.append(f"- {item}")
            else:
                lines.append(str(value))
            lines.append("")
    else:
        lines.append(str(output))

    import os
    tmp = md_path.with_suffix(".tmp")
    tmp.write_text("\n".join(lines), encoding="utf-8")
    os.replace(tmp, md_path)
    payload["_markdown_path"] = str(md_path)
    return payload


# ── 6. generate_arabic_version ───────────────────────────────────────────────
# Off by default — enabled when context["generate_arabic"] = True

def generate_arabic_version(payload: dict, context: dict) -> dict:
    """Generate Arabic translation of final deliverable. Off by default."""
    if not context.get("generate_arabic"):
        return payload

    output = payload.get("output", payload)
    content_en = output.get("content_en") or output.get("text", "")
    if not content_en:
        return payload

    case_id = context.get("case_id") or payload.get("case_id")
    if not case_id:
        return payload

    try:
        from tools.formatting import translate_to_arabic
        from tools.file_tools import write_final_report
        content_ar = translate_to_arabic(
            content_en,
            document_type=context.get("workflow", "report"),
            client_name=context.get("client_name", ""),
        )
        write_final_report(case_id, content_ar, "ar")
        if isinstance(output, dict):
            output["content_ar"] = content_ar
        payload["_arabic_generated"] = True
    except Exception as e:
        payload["_arabic_error"] = str(e)

    return payload


# ── Ordered list for HookEngine registration ─────────────────────────────────
POST_HOOKS = [
    ("validate_schema",        validate_schema),
    ("persist_artifact",       persist_artifact),
    ("append_audit_event",     append_audit_event_hook),
    ("extract_citations",      extract_citations),
    ("render_markdown",        render_markdown),
    ("generate_arabic_version", generate_arabic_version),
]
