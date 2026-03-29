"""Pre-hooks — run in order before any agent call.

Each hook: (payload: dict, context: dict) -> dict
Raise HookVetoError to block the pipeline.

Order:
  1. validate_input       — blocking: required fields must be present
  2. normalize_language   — ensure language is a supported code
  3. sanitize_pii         — strip raw account/passport numbers from free-text fields
  4. attach_case_metadata — stamp case_id, workflow, timestamp onto payload
"""

import re
from datetime import datetime, timezone

from core.hook_engine import HookVetoError

# ── Patterns stripped by sanitize_pii ────────────────────────────────────────
_PII_PATTERNS = [
    (re.compile(r'\b[A-Z]{1,2}\d{6,9}\b'), '[PASSPORT_REDACTED]'),          # passport numbers
    (re.compile(r'\b\d{10,20}\b'), '[ACCOUNT_REDACTED]'),                    # bank account numbers
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), '[SSN_REDACTED]'),               # SSN-style
    (re.compile(r'\b(?:\d[ -]?){13,16}\b'), '[CARD_REDACTED]'),             # card numbers
]

_SUPPORTED_LANGUAGES = {"en", "ar"}
_REQUIRED_FIELDS = {"case_id", "workflow"}
_FREE_TEXT_FIELDS = {"description", "summary", "notes", "context"}


def validate_input(payload: dict, context: dict) -> dict:
    """Block if required fields are missing."""
    missing = [f for f in _REQUIRED_FIELDS if not payload.get(f)]
    if missing:
        raise HookVetoError("validate_input", f"Missing required fields: {missing}")
    return payload


def normalize_language(payload: dict, context: dict) -> dict:
    """Normalise language code; default to 'en' if unsupported."""
    lang = str(payload.get("language", "en")).lower().strip()
    if lang not in _SUPPORTED_LANGUAGES:
        lang = "en"
    payload["language"] = lang
    return payload


def sanitize_pii(payload: dict, context: dict) -> dict:
    """Strip raw account/passport numbers from free-text fields."""
    for field in _FREE_TEXT_FIELDS:
        value = payload.get(field)
        if not isinstance(value, str):
            continue
        for pattern, replacement in _PII_PATTERNS:
            value = pattern.sub(replacement, value)
        payload[field] = value
    return payload


def attach_case_metadata(payload: dict, context: dict) -> dict:
    """Stamp case_id, workflow, and processing timestamp onto payload."""
    payload.setdefault("_meta", {})
    payload["_meta"]["case_id"]    = payload.get("case_id")
    payload["_meta"]["workflow"]   = payload.get("workflow")
    payload["_meta"]["processed_at"] = datetime.now(timezone.utc).isoformat()
    return payload


# ── Ordered list for HookEngine registration ─────────────────────────────────
PRE_HOOKS = [
    ("validate_input",       validate_input),
    ("normalize_language",   normalize_language),
    ("sanitize_pii",         sanitize_pii),
    ("attach_case_metadata", attach_case_metadata),
]
