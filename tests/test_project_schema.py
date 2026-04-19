"""tests/test_project_schema.py — P9-01-AC smoke + security tests.

Covers:
  - slug derivation (7-step algorithm)
  - path traversal blocking (R-019)
  - empty slug rejection
  - InputSession lifecycle validation
  - ProjectState field validation
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from schemas.project import ProjectIntake, InputSession, ProjectState, derive_slug
from core.state_machine import CaseStatus


# ── derive_slug unit tests ─────────────────────────────────────────────────────

class TestDeriveSlug:
    def test_spaces_and_slash_stripped(self):
        assert derive_slug("Project Alpha / FRM") == "project-alpha-frm"

    def test_underscores_become_hyphens(self):
        assert derive_slug("__test__") == "test"

    def test_already_valid_slug_unchanged(self):
        assert derive_slug("valid-slug") == "valid-slug"

    def test_mixed_case_lowercased(self):
        assert derive_slug("MyProject") == "myproject"

    def test_consecutive_hyphens_collapsed(self):
        assert derive_slug("a  b") == "a-b"

    def test_path_traversal_dotdot_blocked(self):
        with pytest.raises(ValueError, match="path traversal"):
            derive_slug("../etc/passwd")

    def test_forward_slash_stripped_not_blocked(self):
        # "/" in a natural name like "Project Alpha / FRM" is stripped by step 4
        assert derive_slug("foo/bar") == "foobar"

    def test_backslash_stripped_not_blocked(self):
        # "\" is stripped by step 4 — not a path-traversal trigger on its own
        assert derive_slug("foo\\bar") == "foobar"

    def test_null_byte_blocked(self):
        with pytest.raises(ValueError):
            derive_slug("foo\x00bar")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="empty slug"):
            derive_slug("   ")

    def test_only_special_chars_raises(self):
        with pytest.raises(ValueError, match="empty slug"):
            derive_slug("!!!###")


# ── ProjectIntake tests ────────────────────────────────────────────────────────

class TestProjectIntake:
    def _make(self, **kwargs):
        defaults = dict(
            project_name="Test Project",
            client_name="ACME Corp",
            service_type="due_diligence",
        )
        defaults.update(kwargs)
        return ProjectIntake(**defaults)

    def test_slug_derived_from_name(self):
        intake = self._make(project_name="Project Alpha / FRM")
        assert intake.project_slug == "project-alpha-frm"

    def test_path_traversal_blocked(self):
        with pytest.raises(ValueError):
            self._make(project_name="../etc/passwd")

    def test_empty_name_blocked(self):
        with pytest.raises(ValueError):
            self._make(project_name="   ")

    def test_invalid_language_standard_blocked(self):
        with pytest.raises(ValidationError):
            self._make(language_standard="invalid")

    def test_valid_language_standards(self):
        for std in ("acfe", "expert_witness", "regulatory", "board_pack"):
            intake = self._make(language_standard=std)
            assert intake.language_standard == std

    def test_default_language_standard_is_acfe(self):
        intake = self._make()
        assert intake.language_standard == "acfe"

    def test_created_at_auto_populated(self):
        intake = self._make()
        assert intake.created_at is not None
        assert isinstance(intake.created_at, datetime)


# ── InputSession tests ─────────────────────────────────────────────────────────

class TestInputSession:
    def _make(self, **kwargs):
        defaults = dict(
            session_id="s1",
            project_slug="test-project",
            mode="input",
            status="open",
            started_at=datetime.utcnow(),
            documents_registered=[],
        )
        defaults.update(kwargs)
        return InputSession(**defaults)

    def test_valid_session_creates(self):
        session = self._make()
        assert session.status == "open"

    def test_invalid_status_blocked(self):
        with pytest.raises(ValidationError):
            self._make(status="invalid_status")

    def test_invalid_mode_blocked(self):
        with pytest.raises(ValidationError):
            self._make(mode="unknown")

    def test_session_log_path(self):
        session = self._make(project_slug="my-project")
        assert session.session_log_path == "cases/my-project/D_Working_Papers/session_log.jsonl"

    def test_defaults(self):
        session = self._make()
        assert session.key_facts_count == 0
        assert session.red_flags_count == 0
        assert session.closed_at is None
        assert session.notes_path is None


# ── ProjectState tests ─────────────────────────────────────────────────────────

class TestProjectState:
    def _make(self, **kwargs):
        defaults = dict(
            project_slug="test-project",
            status=CaseStatus.INTAKE_CREATED,
        )
        defaults.update(kwargs)
        return ProjectState(**defaults)

    def test_valid_state_creates(self):
        state = self._make()
        assert state.project_slug == "test-project"

    def test_invalid_health_blocked(self):
        with pytest.raises(ValidationError):
            self._make(project_health="invalid")

    def test_is_legacy_defaults_false(self):
        state = self._make()
        assert state.is_legacy is False

    def test_cases_defaults_empty_dict(self):
        state = self._make()
        assert state.cases == {}
        assert isinstance(state.cases, dict)

    def test_last_updated_auto_set(self):
        state = self._make()
        assert state.last_updated is not None
        assert isinstance(state.last_updated, datetime)

    def test_context_budget_defaults_zero(self):
        state = self._make()
        assert state.context_budget_used_pct == 0.0
