"""Tests for hooks/post_hooks.py (TEST-04).

Covers: validate_schema, persist_artifact, append_audit_event_hook, extract_citations.
All file I/O uses patched_cases_dir — no production data touched.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import BaseModel


# ── helpers ───────────────────────────────────────────────────────────────────

class _SimpleSchema(BaseModel):
    name: str
    value: int


def _ctx(case_id: str, **kwargs) -> dict:
    return {"case_id": case_id, "agent": "test_agent", "artifact_type": "output", **kwargs}


# ── validate_schema ───────────────────────────────────────────────────────────

class TestValidateSchema:
    def test_passes_when_no_schema_cls(self, patched_cases_dir, sample_case_id):
        from hooks.post_hooks import validate_schema
        payload = {"name": "x", "value": 1}
        result = validate_schema(payload, _ctx(sample_case_id))
        assert result == payload

    def test_passes_valid_payload(self, patched_cases_dir, sample_case_id):
        from hooks.post_hooks import validate_schema
        payload = {"output": {"name": "x", "value": 1}}
        ctx = _ctx(sample_case_id, schema_cls=_SimpleSchema)
        result = validate_schema(payload, ctx)
        assert result == payload

    def test_blocks_invalid_payload(self, patched_cases_dir, sample_case_id):
        from hooks.post_hooks import validate_schema
        from core.hook_engine import HookVetoError
        payload = {"output": {"name": "x", "value": "not_an_int"}}
        ctx = _ctx(sample_case_id, schema_cls=_SimpleSchema)
        with pytest.raises(HookVetoError):
            validate_schema(payload, ctx)


# ── persist_artifact ──────────────────────────────────────────────────────────

class TestPersistArtifact:
    def test_writes_file(self, patched_cases_dir, sample_case_id):
        from hooks.post_hooks import persist_artifact
        payload = {"output": {"summary": "test output"}}
        ctx = _ctx(sample_case_id)
        result = persist_artifact(payload, ctx)
        artifact_path = Path(result["_artifact_path"])
        assert artifact_path.exists()
        data = json.loads(artifact_path.read_text())
        assert data["summary"] == "test output"

    def test_no_tmp_file_remains(self, patched_cases_dir, sample_case_id):
        from hooks.post_hooks import persist_artifact
        payload = {"output": {"x": 1}}
        ctx = _ctx(sample_case_id)
        result = persist_artifact(payload, ctx)
        artifact_path = Path(result["_artifact_path"])
        assert not artifact_path.with_suffix(".tmp").exists()

    def test_raises_without_case_id(self):
        from hooks.post_hooks import persist_artifact
        from core.hook_engine import HookVetoError
        with pytest.raises(HookVetoError):
            persist_artifact({"output": {}}, {"agent": "test_agent", "artifact_type": "output"})


# ── append_audit_event_hook ───────────────────────────────────────────────────

class TestAppendAuditEventHook:
    def test_appends_line_to_audit_log(self, patched_cases_dir, sample_case_id):
        from hooks.post_hooks import append_audit_event_hook
        payload = {}
        ctx = _ctx(sample_case_id, event="test_event", workflow="test_wf")
        append_audit_event_hook(payload, ctx)

        from tools.file_tools import case_dir
        log_path = case_dir(sample_case_id) / "audit_log.jsonl"
        assert log_path.exists()
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["event"] == "test_event"

    def test_multiple_appends_grow_log(self, patched_cases_dir, sample_case_id):
        from hooks.post_hooks import append_audit_event_hook
        ctx = _ctx(sample_case_id, event="evt", workflow="wf")
        append_audit_event_hook({}, ctx)
        append_audit_event_hook({}, ctx)

        from tools.file_tools import case_dir
        log_path = case_dir(sample_case_id) / "audit_log.jsonl"
        lines = log_path.read_text().strip().splitlines()
        assert len(lines) == 2

    def test_noop_without_case_id(self):
        from hooks.post_hooks import append_audit_event_hook
        result = append_audit_event_hook({}, {"agent": "a"})
        assert result == {}


# ── extract_citations ─────────────────────────────────────────────────────────

class TestExtractCitations:
    def test_writes_citations_index(self, patched_cases_dir, sample_case_id):
        from hooks.post_hooks import extract_citations
        from tools.file_tools import case_dir
        payload = {
            "output": {
                "citations": [
                    {"source_url": "https://example.com", "source_name": "Example",
                     "source_type": "authoritative", "excerpt": "text",
                     "retrieved_at": "2026-01-01T00:00:00Z", "confidence": "high"},
                ]
            }
        }
        ctx = _ctx(sample_case_id)
        extract_citations(payload, ctx)

        index = json.loads((case_dir(sample_case_id) / "citations_index.json").read_text())
        assert any(c["source_url"] == "https://example.com" for c in index)

    def test_deduplicates_by_source_url(self, patched_cases_dir, sample_case_id):
        from hooks.post_hooks import extract_citations
        from tools.file_tools import case_dir
        citation = {
            "source_url": "https://dedup.com", "source_name": "Dedup",
            "source_type": "general", "excerpt": "x",
            "retrieved_at": "2026-01-01T00:00:00Z", "confidence": "low",
        }
        payload = {"output": {"citations": [citation]}}
        ctx = _ctx(sample_case_id)
        extract_citations(payload, ctx)
        extract_citations(payload, ctx)

        index = json.loads((case_dir(sample_case_id) / "citations_index.json").read_text())
        matches = [c for c in index if c["source_url"] == "https://dedup.com"]
        assert len(matches) == 1

    def test_noop_with_empty_citations(self, patched_cases_dir, sample_case_id):
        from hooks.post_hooks import extract_citations
        result = extract_citations({"output": {}}, _ctx(sample_case_id))
        assert result == {"output": {}}
