"""TEST-07b — File artifact assertions for write_final_report and mark_deliverable_written.

Covers the file-system outcomes that test_file_tools.py deferred:
- write_final_report() creates .md file with correct content
- write_final_report() attempts .docx generation (graceful fallback if lib unavailable)
- write_final_report() moves *.v*.json artifacts to interim/
- mark_deliverable_written() sets state to DELIVERABLE_WRITTEN
- mark_deliverable_written() appends audit event with event=deliverable_written
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest


# ── write_final_report ─────────────────────────────────────────────────────────

class TestWriteFinalReport:
    def test_md_file_created_with_correct_content(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_final_report, case_dir
        content = "# Final Report\n\nTest content."
        path = write_final_report(sample_case_id, content)
        assert path.exists()
        assert path.read_text(encoding="utf-8") == content

    def test_md_file_named_correctly(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_final_report
        path = write_final_report(sample_case_id, "content")
        assert path.name == "final_report.en.md"

    def test_language_parameter_respected(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_final_report
        path = write_final_report(sample_case_id, "content", language="ar")
        assert path.name == "final_report.ar.md"

    def test_no_tmp_file_remains(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_final_report, case_dir
        write_final_report(sample_case_id, "content")
        assert list(case_dir(sample_case_id).glob("*.tmp")) == []

    def test_versioned_artifacts_moved_to_interim(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_artifact, write_final_report, case_dir
        # Pre-create some versioned artifacts in case root
        write_artifact(sample_case_id, "junior", "draft", {"x": 1})
        write_artifact(sample_case_id, "pm", "review", {"y": 2})
        cdir = case_dir(sample_case_id)
        assert len(list(cdir.glob("*.v*.json"))) == 2

        write_final_report(sample_case_id, "# Report")
        # Root should have no versioned artifacts remaining
        assert list(cdir.glob("*.v*.json")) == []
        # interim/ should contain them
        interim = cdir / "interim"
        assert interim.exists()
        assert len(list(interim.glob("*.v*.json"))) == 2

    def test_docx_generation_attempted_gracefully(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_final_report
        # OutputGenerator may or may not be available — write_final_report must not raise
        try:
            write_final_report(sample_case_id, "# Report")
        except Exception as exc:
            pytest.fail(f"write_final_report raised unexpectedly: {exc}")

    def test_permanent_files_not_moved_to_interim(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_state, write_final_report, case_dir, append_audit_event
        write_state(sample_case_id, {"case_id": sample_case_id, "status": "partner_review_complete"})
        append_audit_event(sample_case_id, {"event": "test_event"})
        write_final_report(sample_case_id, "# Report")
        cdir = case_dir(sample_case_id)
        # Permanent files must remain at root
        assert (cdir / "state.json").exists()
        assert (cdir / "audit_log.jsonl").exists()


# ── mark_deliverable_written ───────────────────────────────────────────────────

class TestMarkDeliverableWritten:
    def test_state_set_to_deliverable_written(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_state, mark_deliverable_written, read_state
        write_state(sample_case_id, {
            "case_id": sample_case_id,
            "workflow": "frm_risk_register",
            "status": "owner_approved",
        })
        mark_deliverable_written(sample_case_id, "frm_risk_register")
        state = read_state(sample_case_id)
        assert state["status"] == "deliverable_written"

    def test_audit_event_appended(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_state, mark_deliverable_written, case_dir
        write_state(sample_case_id, {
            "case_id": sample_case_id,
            "workflow": "frm_risk_register",
            "status": "owner_approved",
        })
        mark_deliverable_written(sample_case_id, "frm_risk_register")
        log = case_dir(sample_case_id) / "audit_log.jsonl"
        assert log.exists()
        events = [json.loads(line) for line in log.read_text().splitlines() if line.strip()]
        assert any(e.get("event") == "deliverable_written" for e in events)

    def test_workflow_recorded_in_audit_event(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_state, mark_deliverable_written, case_dir
        write_state(sample_case_id, {
            "case_id": sample_case_id,
            "workflow": "investigation_report",
            "status": "owner_approved",
        })
        mark_deliverable_written(sample_case_id, "investigation_report")
        log = case_dir(sample_case_id) / "audit_log.jsonl"
        events = [json.loads(line) for line in log.read_text().splitlines() if line.strip()]
        dw_events = [e for e in events if e.get("event") == "deliverable_written"]
        assert dw_events
        assert dw_events[0].get("workflow") == "investigation_report"

    def test_last_updated_refreshed(self, patched_cases_dir, sample_case_id):
        from tools.file_tools import write_state, mark_deliverable_written, read_state
        write_state(sample_case_id, {
            "case_id": sample_case_id,
            "workflow": "frm_risk_register",
            "status": "owner_approved",
            "last_updated": "2020-01-01T00:00:00Z",
        })
        mark_deliverable_written(sample_case_id, "frm_risk_register")
        state = read_state(sample_case_id)
        assert state["last_updated"] != "2020-01-01T00:00:00Z"
