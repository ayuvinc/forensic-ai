"""Readiness check for the GoodWork app.

check_readiness() is called by bootstrap() on every page load.  It derives
setup state from the presence and content of actual artifacts — never from
setup.json alone.  setup.json is a cache/convenience marker only; a missing
or corrupt setup.json on a working install is silently rebuilt.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

_BASE = Path(__file__).parent.parent.parent  # repo root


@dataclass
class ReadinessResult:
    ready: bool
    missing: list[str] = field(default_factory=list)
    setup_json_rebuilt: bool = False


def check_readiness() -> ReadinessResult:
    """Check whether the app is fully configured for use.

    Five required conditions (all must pass):
      1. .env exists and ANTHROPIC_API_KEY is non-empty
      2. firm_profile/firm.json exists and contains a non-empty firm_name
      3. firm_profile/team.json exists and contains at least one member
      4. firm_profile/pricing_model.json exists
      5. assets/templates/base_report_base.docx exists

    Returns a ReadinessResult.  If all pass, also ensures setup.json is
    present (rebuilds silently if missing/corrupt — never blocks on it).
    """
    missing: list[str] = []

    # 1 — API key
    _load_env()
    if not os.getenv("ANTHROPIC_API_KEY", "").strip():
        missing.append("ANTHROPIC_API_KEY")

    # 2 — firm.json with firm_name
    firm_json = _BASE / "firm_profile" / "firm.json"
    if not firm_json.exists():
        missing.append("firm_profile/firm.json")
    else:
        try:
            data = json.loads(firm_json.read_text(encoding="utf-8"))
            if not data.get("firm_name", "").strip():
                missing.append("firm_name (firm_profile/firm.json is missing firm_name)")
        except (json.JSONDecodeError, OSError):
            missing.append("firm_profile/firm.json (unreadable)")

    # 3 — team.json with at least one member
    team_json = _BASE / "firm_profile" / "team.json"
    if not team_json.exists():
        missing.append("firm_profile/team.json")
    else:
        try:
            team = json.loads(team_json.read_text(encoding="utf-8"))
            if not isinstance(team, list) or len(team) == 0:
                missing.append("firm_profile/team.json (no team members defined)")
        except (json.JSONDecodeError, OSError):
            missing.append("firm_profile/team.json (unreadable)")

    # 4 — pricing_model.json
    pricing_json = _BASE / "firm_profile" / "pricing_model.json"
    if not pricing_json.exists():
        missing.append("firm_profile/pricing_model.json")

    # 5 — base Word template
    base_template = _BASE / "assets" / "templates" / "base_report_base.docx"
    if not base_template.exists():
        missing.append("assets/templates/base_report_base.docx")

    ready = len(missing) == 0
    rebuilt = False

    if ready:
        rebuilt = _ensure_setup_json()

    return ReadinessResult(ready=ready, missing=missing, setup_json_rebuilt=rebuilt)


# ── helpers ───────────────────────────────────────────────────────────────────

def _load_env() -> None:
    """Load .env into the environment (override=True so hot-reloads work)."""
    try:
        from dotenv import load_dotenv
        load_dotenv(_BASE / ".env", override=True)
    except ImportError:
        pass


def _ensure_setup_json() -> bool:
    """Write setup.json if it is missing or corrupt.  Returns True if rebuilt."""
    setup_path = _BASE / "firm_profile" / "setup.json"
    try:
        data = json.loads(setup_path.read_text(encoding="utf-8"))
        if data.get("setup_complete") is True:
            return False
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass

    # Rebuild
    import datetime
    payload = {
        "setup_complete": True,
        "setup_version": 1,
        "completed_at": datetime.datetime.utcnow().isoformat() + "Z",
        "note": "rebuilt by readiness check — all artifacts present",
    }
    try:
        _atomic_write(setup_path, json.dumps(payload, indent=2))
    except OSError:
        pass  # Non-fatal — readiness is artifact-based, not setup.json-based
    return True


def _atomic_write(path: Path, content: str) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)
