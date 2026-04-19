"""Tests for tools/file_tools.py.

Covers: case_dir path traversal (R-019), write_artifact atomic write,
write_state + read_state roundtrip, build_case_index with 0/1/N cases,
append_audit_event append-only semantics.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


# ── case_dir ───────────────────────────────────────────────────────────────────

class TestCaseDir:
    def test_creates_directory(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import case_dir
        d = case_dir(sample_case_id)
        assert d.exists() and d.is_dir()

    def test_returns_path_inside_cases_dir(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import case_dir
        d = case_dir(sample_case_id)
        assert str(d).startswith(str(patched_cases_dir))

    def test_idempotent(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import case_dir
        assert case_dir(sample_case_id) == case_dir(sample_case_id)

    @pytest.mark.parametrize("bad_id", [
        "../etc/passwd",
        "../../evil",
        "foo/../../etc",
    ])
    def test_traversal_attempt_raises(self, patched_cases_dir, bad_id):
        """R-019: case_dir must not create directories outside cases/."""
        from tools.file_tools import case_dir
        try:
            d = case_dir(bad_id)
            # If it did not raise, the returned path must still be inside cases/
            assert str(d.resolve()).startswith(str(patched_cases_dir.resolve())), (
                f"case_dir({bad_id!r}) created a directory outside cases/: {d}"
            )
        except (ValueError, OSError):
            pass  # Expected: traversal blocked


# ── write_artifact ─────────────────────────────────────────────────────────────

class TestWriteArtifact:
    def test_no_tmp_file_remains_after_success(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_artifact, case_dir
        write_artifact(sample_case_id, "junior", "draft", {"test": 1})
        remaining_tmp = list(case_dir(sample_case_id).glob("*.tmp"))
        assert remaining_tmp == []

    def test_first_write_is_v1(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_artifact
        p = write_artifact(sample_case_id, "junior", "draft", {"v": 1})
        assert p.name == "junior_draft.v1.json"

    def test_version_increments_on_second_write(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_artifact
        p1 = write_artifact(sample_case_id, "junior", "draft", {"v": 1})
        p2 = write_artifact(sample_case_id, "junior", "draft", {"v": 2})
        assert "v1" in p1.name
        assert "v2" in p2.name

    def test_content_roundtrip(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_artifact
        data = {"finding": "test_finding", "risk": "high"}
        path = write_artifact(sample_case_id, "partner", "review", data)
        loaded = json.loads(path.read_text())
        assert loaded == data


# ── write_state / read_state ───────────────────────────────────────────────────

class TestStateRoundtrip:
    def test_write_then_read(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_state, read_state
        state = {"case_id": sample_case_id, "status": "intake_created", "workflow": "frm"}
        write_state(sample_case_id, state)
        loaded = read_state(sample_case_id)
        assert loaded["status"] == "intake_created"
        assert loaded["workflow"] == "frm"

    def test_read_missing_returns_none(self, patched_cases_dir):
        from tools.file_tools import read_state
        assert read_state("nonexistent-99999") is None

    def test_write_state_no_tmp_remains(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_state, case_dir
        write_state(sample_case_id, {"case_id": sample_case_id, "status": "test"})
        assert list(case_dir(sample_case_id).glob("*.tmp")) == []

    def test_overwrite_updates_value(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_state, read_state
        write_state(sample_case_id, {"case_id": sample_case_id, "status": "intake_created"})
        write_state(sample_case_id, {"case_id": sample_case_id, "status": "junior_draft_complete"})
        assert read_state(sample_case_id)["status"] == "junior_draft_complete"


# ── build_case_index ───────────────────────────────────────────────────────────

class TestBuildCaseIndex:
    def test_empty_cases_dir_produces_empty_index(self, patched_cases_dir):
        from tools.file_tools import build_case_index
        idx = build_case_index()
        assert idx.exists()
        assert json.loads(idx.read_text()) == []

    def test_single_case_indexed(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_state, build_case_index, _INDEX_PATH
        write_state(sample_case_id, {
            "case_id": sample_case_id, "workflow": "frm",
            "status": "intake_created", "last_updated": "2026-01-01"
        })
        build_case_index()
        entries = json.loads(_INDEX_PATH.read_text())
        assert len(entries) == 1
        assert entries[0]["case_id"] == sample_case_id
        assert entries[0]["workflow"] == "frm"

    def test_multiple_cases_all_indexed(self, patched_cases_dir):
        from tools.file_tools import write_state, build_case_index, _INDEX_PATH
        for i in range(3):
            cid = f"case-{i:03}"
            write_state(cid, {
                "case_id": cid, "workflow": "investigation",
                "status": "intake_created", "last_updated": "2026-01-01"
            })
        build_case_index()
        entries = json.loads(_INDEX_PATH.read_text())
        assert len(entries) == 3

    def test_malformed_state_json_skipped_silently(self, patched_cases_dir):
        from tools.file_tools import build_case_index
        bad_dir = patched_cases_dir / "bad-case"
        bad_dir.mkdir()
        (bad_dir / "state.json").write_text("not valid json {{", encoding="utf-8")
        idx_path = build_case_index()
        entries = json.loads(idx_path.read_text())
        assert all(e.get("case_id") != "bad-case" for e in entries)

    def test_idempotent(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_state, build_case_index, _INDEX_PATH
        write_state(sample_case_id, {
            "case_id": sample_case_id, "workflow": "frm",
            "status": "intake_created", "last_updated": "2026-01-01"
        })
        build_case_index()
        build_case_index()  # second call should produce same result
        entries = json.loads(_INDEX_PATH.read_text())
        assert len(entries) == 1


# ── append_audit_event ─────────────────────────────────────────────────────────

class TestAppendAuditEvent:
    def test_creates_log_file(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import append_audit_event, case_dir
        append_audit_event(sample_case_id, {"event": "test"})
        log = case_dir(sample_case_id) / "audit_log.jsonl"
        assert log.exists()

    def test_file_grows_with_each_append(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import append_audit_event, case_dir
        log = case_dir(sample_case_id) / "audit_log.jsonl"
        append_audit_event(sample_case_id, {"event": "first"})
        size1 = log.stat().st_size
        append_audit_event(sample_case_id, {"event": "second"})
        size2 = log.stat().st_size
        assert size2 > size1, "audit_log.jsonl must only grow (append-only)"

    def test_each_line_is_valid_json_with_timestamp(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import append_audit_event, case_dir
        events = [{"event": f"evt_{i}", "idx": i} for i in range(3)]
        for evt in events:
            append_audit_event(sample_case_id, evt)
        log = case_dir(sample_case_id) / "audit_log.jsonl"
        lines = [ln.strip() for ln in log.read_text().splitlines() if ln.strip()]
        assert len(lines) == 3
        for line in lines:
            parsed = json.loads(line)
            assert "event" in parsed
            assert "timestamp" in parsed  # auto-added by append_audit_event

    def test_previous_content_not_overwritten(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import append_audit_event, case_dir
        append_audit_event(sample_case_id, {"event": "first_event"})
        append_audit_event(sample_case_id, {"event": "second_event"})
        log = case_dir(sample_case_id) / "audit_log.jsonl"
        content = log.read_text()
        assert "first_event" in content
        assert "second_event" in content
