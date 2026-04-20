"""KnowledgeHarvester — KL-02: engagement knowledge promotion pipeline.

After a case reaches OWNER_APPROVED, harvest_case() extracts approved
engagement patterns and promotes them to the firm-level cross-case knowledge
layer (firm_profile/knowledge/engagement/index.jsonl).

Security:
  - Content fields strip client identifiers before writing.
  - No raw evidence text is exported — only structural patterns and
    anonymised observations.
  - File writes are atomic (.tmp → os.replace()).

BA: BA-KL-01
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from config import CASES_DIR
from tools.file_tools import append_audit_event, case_dir


# ── Paths ─────────────────────────────────────────────────────────────────────

_ENGAGEMENT_INDEX = (
    Path(__file__).parent.parent
    / "firm_profile"
    / "knowledge"
    / "engagement"
    / "index.jsonl"
)

# Simple regex patterns for PII stripping
_PII_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b[A-Z]{1,3}-\d{6,}\b"),           # company reg numbers
    re.compile(r"\bTRN\d{15}\b", re.IGNORECASE),     # UAE tax reg numbers
    re.compile(r"\b\d{9,12}\b"),                     # long numeric IDs
    re.compile(r"\b[A-Z][0-9]{8}\b"),                # passport-style IDs
]

# Field names that may contain client identifiers — never exported
_BLOCKED_FIELDS = frozenset({
    "client_name", "case_id", "company_name", "entity_name",
    "subject_name", "contact_name", "email", "phone",
    "passport_number", "visa_number", "company_registration",
})


def harvest_case(case_id: str) -> Optional[Path]:
    """Extract approved patterns from a completed case and promote to firm knowledge.

    Reads junior_output and partner_approval artifacts from the case folder.
    Strips client identifiers. Writes approved_patterns.json to
    cases/{case_id}/knowledge_export/ and appends a summary entry to
    firm_profile/knowledge/engagement/index.jsonl.

    Returns path to approved_patterns.json, or None if no artifacts found.
    """
    cdir = case_dir(case_id)

    # ── Load source artifacts ──────────────────────────────────────────────────
    artifacts = _load_case_artifacts(cdir)
    if not artifacts:
        append_audit_event(case_id, {
            "event":   "KNOWLEDGE_HARVEST_SKIPPED",
            "reason":  "no_artifacts_found",
            "case_id": case_id,
        })
        return None

    # ── Extract patterns ───────────────────────────────────────────────────────
    patterns = _extract_patterns(artifacts)
    if not patterns:
        append_audit_event(case_id, {
            "event":   "KNOWLEDGE_HARVEST_SKIPPED",
            "reason":  "no_patterns_extracted",
            "case_id": case_id,
        })
        return None

    # ── Strip client identifiers ───────────────────────────────────────────────
    sanitised = _sanitise_patterns(patterns)

    # ── Write to knowledge_export/ ─────────────────────────────────────────────
    export_dir = cdir / "knowledge_export"
    export_dir.mkdir(parents=True, exist_ok=True)
    export_path = export_dir / "approved_patterns.json"

    payload = {
        "harvested_at": datetime.now(timezone.utc).isoformat(),
        "workflow": artifacts.get("workflow", "unknown"),
        "pattern_count": len(sanitised),
        "patterns": sanitised,
    }
    _atomic_write_json(export_path, payload)

    # ── Promote to firm-level engagement layer ─────────────────────────────────
    _promote_to_firm_index(case_id, payload)

    # ── Audit event ───────────────────────────────────────────────────────────
    append_audit_event(case_id, {
        "event":         "KNOWLEDGE_HARVEST_COMPLETE",
        "patterns_count": len(sanitised),
        "export_path":   str(export_path.relative_to(cdir)),
    })

    return export_path


# ── Internal helpers ──────────────────────────────────────────────────────────

def _load_case_artifacts(cdir: Path) -> dict:
    """Load the most recent junior_output and partner_approval from the case folder.

    Checks both E_Drafts/ (AF projects) and root (legacy projects).
    """
    artifacts: dict[str, Any] = {}

    # Read state.json for workflow and metadata
    state_path = cdir / "state.json"
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            artifacts["workflow"] = state.get("workflow", "unknown")
        except (json.JSONDecodeError, OSError):
            pass

    # Search in E_Drafts/ first (AF projects), then root (legacy)
    search_dirs = [cdir / "E_Drafts", cdir]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for pattern, key in [
            ("junior_output.v*.json", "junior_output"),
            ("partner_approval.v*.json", "partner_approval"),
        ]:
            files = sorted(search_dir.glob(pattern))
            if files:
                try:
                    artifacts[key] = json.loads(files[-1].read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    pass
        if "junior_output" in artifacts or "partner_approval" in artifacts:
            break  # found artifacts — stop searching

    return artifacts


def _extract_patterns(artifacts: dict) -> list[dict]:
    """Extract structural patterns from case artifacts.

    Pulls approved findings, risk items, and recommendations — not raw evidence.
    """
    patterns: list[dict] = []
    workflow = artifacts.get("workflow", "unknown")

    # Partner approval contains the final approved output
    partner = artifacts.get("partner_approval", {})
    junior = artifacts.get("junior_output", {})

    # FRM risk register patterns
    if "risk_items" in partner:
        for item in partner.get("risk_items", []):
            patterns.append({
                "type": "risk_item",
                "workflow": workflow,
                "category": item.get("category", ""),
                "risk_level": item.get("risk_rating", 0),
                "pattern": item.get("description", "")[:500],
                "recommendations": item.get("recommendations", [])[:3],
            })

    # Investigation findings
    for source in [partner, junior]:
        for finding in source.get("findings", []):
            patterns.append({
                "type": "finding",
                "workflow": workflow,
                "category": finding.get("category", finding.get("type", "")),
                "pattern": finding.get("description", finding.get("summary", ""))[:500],
                "severity": finding.get("severity", ""),
            })

    # Recommendations from any source
    for source in [partner, junior]:
        for rec in source.get("recommendations", []):
            if isinstance(rec, str):
                patterns.append({
                    "type": "recommendation",
                    "workflow": workflow,
                    "pattern": rec[:300],
                })

    return patterns


def _sanitise_patterns(patterns: list[dict]) -> list[dict]:
    """Strip client identifiers from pattern content fields.

    Removes values for blocked field names and applies PII regex
    scrubbing on text content.
    """
    sanitised = []
    for pattern in patterns:
        clean = {}
        for key, val in pattern.items():
            # Drop blocked identifier fields
            if key.lower() in _BLOCKED_FIELDS:
                continue
            # Scrub PII from text fields
            if isinstance(val, str):
                val = _scrub_text(val)
            elif isinstance(val, list):
                val = [_scrub_text(v) if isinstance(v, str) else v for v in val]
            clean[key] = val
        sanitised.append(clean)
    return sanitised


def _scrub_text(text: str) -> str:
    """Apply PII regex patterns to text content."""
    for pattern in _PII_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


def _promote_to_firm_index(case_id: str, payload: dict) -> None:
    """Append a summary entry to firm_profile/knowledge/engagement/index.jsonl."""
    _ENGAGEMENT_INDEX.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "case_id_hash": _hash_case_id(case_id),  # hashed — no raw case ID
        "harvested_at": payload["harvested_at"],
        "workflow": payload.get("workflow", "unknown"),
        "pattern_count": payload.get("pattern_count", 0),
    }
    with open(_ENGAGEMENT_INDEX, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def _hash_case_id(case_id: str) -> str:
    """Return a short hash of the case_id — preserves uniqueness without exposing ID."""
    import hashlib
    return hashlib.sha256(case_id.encode()).hexdigest()[:16]


def _atomic_write_json(path: Path, data: dict) -> None:
    """Write JSON atomically via .tmp → os.replace()."""
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, path)
