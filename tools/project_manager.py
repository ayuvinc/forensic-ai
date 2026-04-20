"""ProjectManager — named engagement lifecycle management.

Creates and manages A-F folder structure per Phase 9 design.
All filesystem writes are atomic (.tmp → os.replace()).
Path operations are confined to cases/{slug}/ — no traversal.

BA: BA-P9-01, BA-P9-02, BA-P9-03, BA-P9-04
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from config import CASES_DIR
from core.state_machine import CaseStatus
from schemas.project import InputSession, ProjectIntake, ProjectState

# The 6 standard A-F subfolders (also exported for file_tools.py P9-04a)
AF_FOLDERS = (
    "A_Engagement_Management",
    "B_Planning",
    "C_Evidence",
    "D_Working_Papers",
    "E_Drafts",
    "F_Final",
)

_INDEX_PATH = CASES_DIR / "index.json"


class ProjectManager:
    """Creates, lists, and manages named Phase 9 engagements.

    All slugs have already been validated by ProjectIntake before reaching here.
    Security: case_dir() is the only path-construction method — no raw slug
    concatenation outside of it.
    """

    # ── Path helpers ──────────────────────────────────────────────────────────

    def _case_dir(self, slug: str) -> Path:
        return CASES_DIR / slug

    # ── Project creation ──────────────────────────────────────────────────────

    def create_project(self, intake: ProjectIntake) -> Path:
        """Create case folder with A-F structure and write initial state.json.

        Returns the path to the created project folder.
        Raises ValueError if slug collides with an existing folder.
        """
        if self.detect_slug_collision(intake.project_slug):
            raise ValueError(f"Project slug already exists: {intake.project_slug}")

        project_dir = self._case_dir(intake.project_slug)
        created_dirs: list[Path] = []

        try:
            project_dir.mkdir(parents=True, exist_ok=False)
            created_dirs.append(project_dir)
            for folder in AF_FOLDERS:
                d = project_dir / folder
                d.mkdir()
                created_dirs.append(d)
        except Exception as exc:
            # All-or-nothing: roll back any dirs created so far
            for d in reversed(created_dirs):
                try:
                    d.rmdir()
                except Exception:
                    pass
            raise exc

        # Initial state
        state = ProjectState(
            project_slug=intake.project_slug,
            status=CaseStatus.INTAKE_CREATED,
            language_standard=intake.language_standard,
        )
        self._write_state(intake.project_slug, state)

        # Register in index
        self._register_in_index(intake, state)

        # Audit event
        self._append_audit(
            intake.project_slug,
            {"event": "PROJECT_CREATED", "service_type": intake.service_type},
        )

        return project_dir

    def create_af_structure(self, slug: str) -> None:
        """Create the 6 A-F subfolders inside an existing project dir."""
        base = self._case_dir(slug)
        for folder in AF_FOLDERS:
            (base / folder).mkdir(parents=True, exist_ok=True)

    # ── Project listing ───────────────────────────────────────────────────────

    def list_projects(self) -> list[dict]:
        """Read cases/index.json. Returns all entries; legacy ones have legacy=True."""
        if not _INDEX_PATH.exists():
            return []
        try:
            entries = json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        return entries if isinstance(entries, list) else []

    # ── Project retrieval ─────────────────────────────────────────────────────

    def get_project(self, slug: str) -> Optional[ProjectState]:
        """Load ProjectState from cases/{slug}/state.json. Returns None if missing."""
        state_path = self._case_dir(slug) / "state.json"
        if not state_path.exists():
            return None
        try:
            return ProjectState(**json.loads(state_path.read_text(encoding="utf-8")))
        except Exception:
            return None

    def get_context_summary(self, slug: str) -> dict:
        """Return document count, token usage %, and interim_context_written flag."""
        state = self.get_project(slug)
        doc_count = self._count_documents(slug)
        return {
            "document_count":         doc_count,
            "context_budget_used_pct": state.context_budget_used_pct if state else 0.0,
            "interim_context_written": state.interim_context_written if state else False,
        }

    # ── Session management ────────────────────────────────────────────────────

    def start_input_session(self, slug: str) -> InputSession:
        """Create a new input session and register it in state.json."""
        session = InputSession(
            session_id=uuid.uuid4().hex[:12],
            project_slug=slug,
            mode="input",
            status="open",
            started_at=datetime.now(timezone.utc),
        )
        state = self.get_project(slug)
        if state:
            state.sessions.append(session)
            self._write_state(slug, state)
        self._append_session_log(slug, {
            "event": "SESSION_STARTED",
            "session_id": session.session_id,
        })
        return session

    def add_session_note(self, slug: str, note: str) -> None:
        """Append note to D_Working_Papers/session_notes_{YYYYMMDD}.md (never overwrites)."""
        notes_dir = self._case_dir(slug) / "D_Working_Papers"
        notes_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        notes_file = notes_dir / f"session_notes_{date_str}.md"
        entry = f"\n---\n**{datetime.now(timezone.utc).isoformat()}**\n\n{note}\n"
        with open(notes_file, "a", encoding="utf-8") as fh:
            fh.write(entry)

    def add_key_fact(self, slug: str, fact: dict) -> None:
        """Append a key fact to D_Working_Papers/key_facts.json."""
        kf_path = self._case_dir(slug) / "D_Working_Papers" / "key_facts.json"
        facts = self._load_json_list(kf_path)
        fact.setdefault("added_at", datetime.now(timezone.utc).isoformat())
        facts.append(fact)
        self._write_json_atomic(kf_path, facts)

    def add_red_flag(self, slug: str, flag: dict) -> None:
        """Append a red flag to D_Working_Papers/red_flags.json."""
        rf_path = self._case_dir(slug) / "D_Working_Papers" / "red_flags.json"
        flags = self._load_json_list(rf_path)
        flag.setdefault("added_at", datetime.now(timezone.utc).isoformat())
        flags.append(flag)
        self._write_json_atomic(rf_path, flags)

    # ── Context accumulation ──────────────────────────────────────────────────

    def write_interim_context(self, slug: str, content: str) -> None:
        """Atomic write of interim_context.md to D_Working_Papers/."""
        wp_dir = self._case_dir(slug) / "D_Working_Papers"
        wp_dir.mkdir(parents=True, exist_ok=True)
        ctx_path = wp_dir / "interim_context.md"
        tmp = ctx_path.with_suffix(".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, ctx_path)

        state = self.get_project(slug)
        if state:
            state.interim_context_written = True
            self._write_state(slug, state)

    # ── AIC context injection (AIC-03) ───────────────────────────────────────

    def get_intake_qa_context(self, slug: str) -> str:
        """Return intake Q&A as a formatted string for agent context injection.

        Returns empty string if intake_qa.json does not exist.
        """
        import json as _json
        qa_path = self._case_dir(slug) / "D_Working_Papers" / "intake_qa.json"
        if not qa_path.exists():
            return ""
        try:
            data = _json.loads(qa_path.read_text(encoding="utf-8"))
            qa_pairs = data.get("qa", [])
            if not qa_pairs:
                return ""
            lines = ["## Intake Follow-Up Q&A"]
            for item in qa_pairs:
                q = item.get("question", "")
                a = item.get("answer", "").strip()
                if q:
                    lines.append(f"Q: {q}")
                    lines.append(f"A: {a if a else '(not answered)'}")
            return "\n".join(lines)
        except Exception:
            return ""

    def get_prefinalrun_context(self, slug: str) -> str:
        """Return pre-final-run review results as a formatted string for agent context.

        Returns empty string if prefinalrun_review.json does not exist.
        """
        import json as _json
        review_path = self._case_dir(slug) / "D_Working_Papers" / "prefinalrun_review.json"
        if not review_path.exists():
            return ""
        try:
            data = _json.loads(review_path.read_text(encoding="utf-8"))
            cards = data.get("cards", [])
            if not cards:
                return ""
            lines = ["## Pre-Run Review Concerns"]
            for card in cards:
                ack = card.get("acknowledgement", "unacknowledged")
                sev = card.get("severity", "medium").upper()
                lines.append(
                    f"[{sev}] {card.get('title','')}: {card.get('detail','')} "
                    f"(Acknowledgement: {ack})"
                )
            return "\n".join(lines)
        except Exception:
            return ""

    # ── Exhibit and Lead register (WF-01a) ───────────────────────────────────

    def add_exhibit(self, slug: str, exhibit: dict) -> None:
        """Append an exhibit entry to D_Working_Papers/exhibits.json.

        exhibit should contain at minimum: exhibit_id (str), description (str).
        added_at is injected automatically.
        """
        path = self._case_dir(slug) / "D_Working_Papers" / "exhibits.json"
        exhibits = self._load_json_list(path)
        exhibit.setdefault("added_at", datetime.now(timezone.utc).isoformat())
        exhibits.append(exhibit)
        self._write_json_atomic(path, exhibits)

    def add_lead(self, slug: str, lead: dict) -> None:
        """Append a lead entry to D_Working_Papers/leads_register.json.

        lead should contain: lead_id (str), description (str).
        status defaults to "open". added_at injected automatically.
        """
        path = self._case_dir(slug) / "D_Working_Papers" / "leads_register.json"
        leads = self._load_json_list(path)
        lead.setdefault("status", "open")
        lead.setdefault("added_at", datetime.now(timezone.utc).isoformat())
        leads.append(lead)
        self._write_json_atomic(path, leads)

    def update_lead(self, slug: str, lead_id: str, updates: dict) -> None:
        """Update an existing lead by lead_id.

        Raises KeyError if lead_id is not found — callers must handle this
        to avoid silent no-ops when an ID is mistyped.
        """
        path = self._case_dir(slug) / "D_Working_Papers" / "leads_register.json"
        leads = self._load_json_list(path)
        for lead in leads:
            if lead.get("lead_id") == lead_id:
                lead.update(updates)
                lead["updated_at"] = datetime.now(timezone.utc).isoformat()
                self._write_json_atomic(path, leads)
                return
        raise KeyError(f"Lead not found: {lead_id}")

    def get_open_leads(self, slug: str) -> list[dict]:
        """Return all leads where status != 'confirmed'."""
        path = self._case_dir(slug) / "D_Working_Papers" / "leads_register.json"
        return [l for l in self._load_json_list(path) if l.get("status") != "confirmed"]

    def get_confirmed_leads(self, slug: str) -> list[dict]:
        """Return all leads where status == 'confirmed'."""
        path = self._case_dir(slug) / "D_Working_Papers" / "leads_register.json"
        return [l for l in self._load_json_list(path) if l.get("status") == "confirmed"]

    # ── Stakeholder context (FR-02) ───────────────────────────────────────────

    def get_stakeholder_context(self, slug: str) -> str:
        """Return stakeholder inputs as a formatted string for agent injection.

        Returns empty string if stakeholder_inputs.json does not exist — no crash.
        """
        path = self._case_dir(slug) / "D_Working_Papers" / "stakeholder_inputs.json"
        if not path.exists():
            return ""
        try:
            entries = json.loads(path.read_text(encoding="utf-8"))
            if not entries:
                return ""
            lines = ["## Stakeholder Inputs"]
            for e in entries:
                name = e.get("name", "Unknown")
                role = e.get("role", "")
                concern = e.get("key_concern", "")
                risk_view = e.get("risk_view", "")
                lines.append(f"**{name}** ({role}): Concern — {concern}. Risk view — {risk_view}.")
            return "\n".join(lines)
        except Exception:
            return ""

    # ── Collision detection ───────────────────────────────────────────────────

    def detect_slug_collision(self, slug: str) -> bool:
        return self._case_dir(slug).exists()

    # ── Private helpers ───────────────────────────────────────────────────────

    def _write_state(self, slug: str, state: ProjectState) -> None:
        state_path = self._case_dir(slug) / "state.json"
        tmp = state_path.with_suffix(".tmp")
        tmp.write_text(state.model_dump_json(indent=2), encoding="utf-8")
        os.replace(tmp, state_path)

    def _register_in_index(self, intake: ProjectIntake, state: ProjectState) -> None:
        """Upsert an entry into cases/index.json."""
        entries = self.list_projects()
        entry = {
            "case_id":       intake.project_slug,
            "engagement_id": intake.project_slug,
            "client_name":   intake.client_name,
            "workflow":      intake.service_type,
            "status":        state.status.value,
            "last_updated":  state.last_updated.isoformat() if state.last_updated else "",
            "project_name":  intake.project_name,
            "service_type":  intake.service_type,
            "language_standard": intake.language_standard,
            "is_af_project": True,
            "legacy":        False,
        }
        entries = [e for e in entries if e.get("case_id") != intake.project_slug]
        entries.append(entry)
        self._write_json_atomic(_INDEX_PATH, entries)

    def _append_audit(self, slug: str, event: dict) -> None:
        audit_path = self._case_dir(slug) / "audit_log.jsonl"
        event.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        with open(audit_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(event) + "\n")

    def _append_session_log(self, slug: str, event: dict) -> None:
        log_path = self._case_dir(slug) / "D_Working_Papers" / "session_log.jsonl"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        event.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(event) + "\n")

    def _count_documents(self, slug: str) -> int:
        idx_path = self._case_dir(slug) / "document_index.json"
        if not idx_path.exists():
            return 0
        try:
            data = json.loads(idx_path.read_text(encoding="utf-8"))
            return len(data.get("documents", []))
        except Exception:
            return 0

    def _load_json_list(self, path: Path) -> list:
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return []

    def _write_json_atomic(self, path: Path, data: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        os.replace(tmp, path)
