"""TemplateManager — resolves, validates, and manages per-workflow .docx templates.

All path operations are confined to firm_profile/templates/.
Any path component that escapes this directory raises ValueError (R-019 pattern).
Atomic writes: .tmp → os.replace().
"""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

TEMPLATES_DIR  = Path("firm_profile/templates")
TEMPLATES_JSON = TEMPLATES_DIR / "templates.json"

# All 7 required named styles.  GW_Heading1 and GW_Body are CRITICAL — block on missing.
REQUIRED_STYLES = (
    "GW_Title",
    "GW_Heading1",
    "GW_Heading2",
    "GW_Body",
    "GW_TableHeader",
    "GW_Caption",
    "GW_Disclaimer",
)
CRITICAL_STYLES = {"GW_Heading1", "GW_Body"}

MAX_TEMPLATE_BYTES = 5 * 1024 * 1024  # 5 MB
DOCX_MAGIC = b"PK"                    # ZIP/DOCX magic bytes (Office Open XML)


@dataclass
class ValidationResult:
    valid: bool
    missing_styles: list[str] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def has_critical_missing(self) -> bool:
        """True when any CRITICAL style (GW_Heading1, GW_Body) is absent."""
        return bool(set(self.missing_styles) & CRITICAL_STYLES)


class TemplateManager:
    """Resolves and manages per-workflow report templates.

    Fallback chain for resolve():  custom → base → base_report_base.docx → FileNotFoundError
    All filesystem writes are atomic (.tmp → os.replace()).
    Path traversal is blocked: any resolved path outside TEMPLATES_DIR raises ValueError.
    """

    # ── Path safety ────────────────────────────────────────────────────────────

    def _safe_path(self, *parts: str) -> Path:
        """Resolve a path and assert it stays within TEMPLATES_DIR.

        Raises ValueError on any path that escapes firm_profile/templates/.
        """
        candidate = (TEMPLATES_DIR / Path(*parts)).resolve()
        templates_abs = TEMPLATES_DIR.resolve()
        try:
            candidate.relative_to(templates_abs)
        except ValueError:
            raise ValueError(
                f"Path traversal attempt blocked: '{Path(*parts)}' escapes "
                f"firm_profile/templates/"
            )
        return candidate

    # ── Registry I/O ──────────────────────────────────────────────────────────

    def _load_registry(self) -> dict:
        import json
        if TEMPLATES_JSON.exists():
            try:
                return json.loads(TEMPLATES_JSON.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _save_registry(self, registry: dict) -> None:
        import json
        TEMPLATES_JSON.parent.mkdir(parents=True, exist_ok=True)
        tmp = TEMPLATES_JSON.with_suffix(".tmp")
        tmp.write_text(json.dumps(registry, indent=2), encoding="utf-8")
        os.replace(tmp, TEMPLATES_JSON)

    # ── Public API ─────────────────────────────────────────────────────────────

    def resolve(self, workflow_type: str, custom_path: Optional[str] = None) -> Path:
        """Return the template Path for a workflow type.

        Priority: explicit custom_path → saved custom → base → wildcard fallback.
        Raises ValueError on path traversal.
        Raises FileNotFoundError if no template exists anywhere.
        """
        if custom_path is not None:
            p = self._safe_path(custom_path)
            if not p.exists():
                raise FileNotFoundError(f"Custom template not found: {custom_path}")
            return p

        registry = self._load_registry()
        entry = registry.get(workflow_type, {})

        # Saved custom template
        custom_name = entry.get("custom")
        if custom_name:
            p = self._safe_path(custom_name)
            if p.exists():
                return p

        # Base template registered in templates.json
        base_name = entry.get("base")
        if base_name:
            p = self._safe_path(base_name)
            if p.exists():
                return p

        # Wildcard fallback — generic base report
        fallback = self._safe_path("base_report_base.docx")
        if fallback.exists():
            return fallback

        raise FileNotFoundError(
            f"No template found for workflow '{workflow_type}'. "
            "Add a base template to firm_profile/templates/."
        )

    def validate_docx(self, path: Path) -> ValidationResult:
        """Validate a .docx file: size cap, magic bytes, python-docx open, style check.

        Returns ValidationResult — never raises.
        Callers inspect result.valid and result.has_critical_missing.
        """
        try:
            if path.stat().st_size > MAX_TEMPLATE_BYTES:
                return ValidationResult(valid=False, error="File exceeds 5 MB limit")

            raw = path.read_bytes()
            if not raw.startswith(DOCX_MAGIC):
                return ValidationResult(valid=False, error="Not a valid .docx file (missing PK header)")

            from docx import Document
            doc = Document(str(path))
            existing_styles = {s.name for s in doc.styles}
            missing = [s for s in REQUIRED_STYLES if s not in existing_styles]
            return ValidationResult(valid=True, missing_styles=missing)

        except Exception as exc:
            return ValidationResult(valid=False, error=str(exc))

    def update_custom(self, workflow_type: str, file_bytes: bytes) -> Path:
        """Save a new custom template, rotating the previous one to _custom.v{N}.docx.

        Returns the path of the newly written custom template.
        Atomic write via .tmp → os.replace().
        """
        TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

        custom_name = f"{workflow_type}_custom.docx"
        target = self._safe_path(custom_name)

        # Rotate existing custom template before overwriting
        if target.exists():
            n = 1
            while self._safe_path(f"{workflow_type}_custom.v{n}.docx").exists():
                n += 1
            shutil.copy2(target, self._safe_path(f"{workflow_type}_custom.v{n}.docx"))

        tmp = target.with_suffix(".tmp")
        tmp.write_bytes(file_bytes)
        os.replace(tmp, target)

        # Persist custom path in registry
        registry = self._load_registry()
        if workflow_type not in registry:
            registry[workflow_type] = {}
        registry[workflow_type]["custom"] = custom_name
        self._save_registry(registry)

        return target

    def list_templates(self) -> dict:
        """Return per-workflow template slots from templates.json."""
        return self._load_registry()
