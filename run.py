#!/usr/bin/env python3
"""GoodWork Forensic Consulting Framework — main entry point.

Run: python run.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console

console = Console()


def main() -> None:
    # ── First-run check ───────────────────────────────────────────────────────
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        from core.setup_wizard import run_first_time_setup
        run_first_time_setup(console)
        return

    # ── Validate config ───────────────────────────────────────────────────────
    from config import validate_config
    missing = validate_config()
    if missing:
        console.print(f"[red]Configuration errors:[/red] {missing}")
        console.print("Please update your .env file and restart.")
        sys.exit(1)

    # ── Load firm name ────────────────────────────────────────────────────────
    firm_name = _load_firm_name()

    # ── Firm profile setup (Phase 2) ──────────────────────────────────────────
    from core.setup_wizard import is_firm_profile_complete, run_firm_profile_setup
    if not is_firm_profile_complete():
        console.print("[yellow]Firm profile not set up.[/yellow]")
        from rich.prompt import Confirm
        if Confirm.ask("Set up firm profile now?", default=True):
            run_firm_profile_setup(console)
            firm_name = _load_firm_name()

    # ── Bootstrap registry + hooks ────────────────────────────────────────────
    from core.hook_engine import HookEngine
    from core.tool_registry import ToolRegistry
    from hooks.pre_hooks import PRE_HOOKS
    from hooks.post_hooks import POST_HOOKS

    registry    = ToolRegistry()
    hook_engine = HookEngine()

    for name, fn in PRE_HOOKS:
        hook_engine.register_pre(name, fn)
    for name, fn in POST_HOOKS:
        hook_engine.register_post(name, fn)

    # ── Main loop ─────────────────────────────────────────────────────────────
    from ui.menu import render_menu
    from ui.progress import ProgressContext

    progress = ProgressContext(console)

    while True:
        try:
            choice = render_menu(console, firm_name)
        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting...[/yellow]")
            break

        if choice == "q":
            console.print("[dim]Goodbye.[/dim]")
            break

        try:
            _dispatch(choice, registry, hook_engine, console, progress, firm_name)
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Returning to menu...[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")


def _dispatch(
    choice: str,
    registry,
    hook_engine,
    console: Console,
    progress,
    firm_name: str,
) -> None:
    """Dispatch menu choice to appropriate workflow."""

    if choice == "0":
        # Scope New Engagement — problem-first scoping flow
        from ui.guided_intake import run_generic_intake
        from workflows.engagement_scoping import run_engagement_scoping_workflow

        intake = run_generic_intake(console, "engagement_scoping", "Scope New Engagement")
        if intake:
            _persist_intake(intake)
            run_engagement_scoping_workflow(
                intake, console=console,
                on_progress=progress.make_callback(),
            )
            _mark_deliverable_written(intake.case_id, intake.workflow)

    elif choice == "1":
        # New Case Intake
        from workflows.new_case_intake import run_new_case_intake
        run_new_case_intake(console)

    elif choice == "2":
        # Investigation Report
        from ui.guided_intake import run_guided_investigation_intake
        from workflows.investigation_report import run_investigation_workflow

        intake = run_guided_investigation_intake(console)
        if intake:
            _persist_intake(intake)
            document_manager = None
            try:
                from tools.document_manager import DocumentManager
                document_manager = DocumentManager(intake.case_id)
            except Exception:
                pass
            _run_document_ingestion(document_manager, console)
            active_doc_manager = (
                document_manager
                if document_manager and document_manager.has_documents()
                else None
            )
            with progress.stage("Running investigation report pipeline..."):
                result = run_investigation_workflow(
                    intake, registry, hook_engine,
                    document_manager=active_doc_manager,
                    console=console,
                    on_progress=progress.make_callback(),
                )
            from ui.display import render_deliverable_summary
            render_deliverable_summary(console, result)

    elif choice == "3":
        # Persona Review
        from workflows.new_case_intake import run_new_case_intake
        from workflows.persona_review import run_persona_review_workflow

        console.print("\n[bold]Persona Review[/bold]")
        console.print("Select or create a case to review.")
        intake = _select_or_create_intake(console, "persona_review", "Persona Review")
        if intake:
            run_persona_review_workflow(
                intake, registry, hook_engine, console=console,
                on_progress=progress.make_callback(),
            )

    elif choice == "4":
        # Policy / SOP Generator
        from ui.guided_intake import run_generic_intake
        from workflows.policy_sop import run_policy_sop_workflow

        intake = run_generic_intake(console, "policy_sop", "Policy / SOP Generator")
        if intake:
            _persist_intake(intake)
            result = run_policy_sop_workflow(
                intake, registry, hook_engine, console=console,
                on_progress=progress.make_callback(),
            )
            _mark_deliverable_written(intake.case_id, intake.workflow)
            from ui.display import render_deliverable_summary
            render_deliverable_summary(console, result)

    elif choice == "5":
        # Training Material
        from ui.guided_intake import run_generic_intake
        from workflows.training_material import run_training_material_workflow

        intake = run_generic_intake(console, "training_material", "Training Material")
        if intake:
            _persist_intake(intake)
            result = run_training_material_workflow(
                intake, console=console, on_progress=progress.make_callback(),
            )
            _mark_deliverable_written(intake.case_id, intake.workflow)
            from ui.display import render_deliverable_summary
            render_deliverable_summary(console, result)

    elif choice == "6":
        # FRM Risk Register
        from ui.guided_intake import run_guided_frm_intake
        from workflows.frm_risk_register import FRM_MODULES, run_frm_workflow
        from rich.prompt import Prompt

        intake = run_guided_frm_intake(console)
        if not intake:
            return
        _persist_intake(intake)

        # Module selection
        console.print("\n  [bold]Select modules:[/bold]")
        for num, name in FRM_MODULES.items():
            console.print(f"    {num}. {name}")
        modules_raw = Prompt.ask(
            "  Enter module numbers (e.g. 1,2,3 or Enter for all)",
            default="",
        )
        if modules_raw.strip():
            selected_modules = [int(x.strip()) for x in modules_raw.split(",") if x.strip().isdigit()]
        else:
            selected_modules = list(FRM_MODULES.keys())

        # Auto-resolve module dependencies: add any required modules not already selected
        from workflows.frm_risk_register import MODULE_DEPENDENCIES, FRM_MODULES as _FRM_MODULES
        added = []
        changed = True
        while changed:
            changed = False
            for mod in list(selected_modules):
                for dep in MODULE_DEPENDENCIES.get(mod, []):
                    if dep not in selected_modules:
                        selected_modules.insert(0, dep)
                        added.append(dep)
                        changed = True
        if added:
            added_names = ", ".join(f"{d}. {_FRM_MODULES[d]}" for d in sorted(set(added)))
            console.print(f"  [yellow]Auto-added required module(s): {added_names}[/yellow]")
        selected_modules = sorted(set(selected_modules))

        document_manager = None
        try:
            from tools.document_manager import DocumentManager
            document_manager = DocumentManager(intake.case_id)
        except Exception:
            pass
        _run_document_ingestion(document_manager, console)

        # Only pass document_manager to agents if documents are actually registered.
        # An empty DocumentManager causes agents to hallucinate doc_ids.
        active_doc_manager = (
            document_manager
            if document_manager and document_manager.has_documents()
            else None
        )

        with progress.stage(f"Running FRM pipeline for {intake.client_name}..."):
            result = run_frm_workflow(
                intake, selected_modules, registry, hook_engine,
                document_manager=active_doc_manager,
                console=console, on_progress=progress.make_callback(),
            )

        console.print(f"\n[green]FRM Risk Register complete: {len(result.risk_register)} risks identified[/green]")
        console.print(f"Report: cases/{intake.case_id}/final_report.en.md")

    elif choice == "7":
        # Client Proposal
        from ui.guided_intake import run_guided_proposal_intake
        from workflows.client_proposal import run_client_proposal_workflow

        intake = run_guided_proposal_intake(console)
        if intake:
            _persist_intake(intake)
            result = run_client_proposal_workflow(
                intake, registry, hook_engine, console=console,
                on_progress=progress.make_callback(),
            )
            _mark_deliverable_written(intake.case_id, intake.workflow)
            from ui.display import render_deliverable_summary
            render_deliverable_summary(console, result)

    elif choice == "8":
        # Build Proposal PPT Prompt Pack
        from ui.guided_intake import run_generic_intake
        from workflows.proposal_deck import run_proposal_deck_workflow

        intake = run_generic_intake(console, "proposal_deck", "Build Proposal PPT Prompt Pack")
        if intake:
            _persist_intake(intake)
            run_proposal_deck_workflow(
                intake, registry, hook_engine, console=console,
                on_progress=progress.make_callback(),
            )
            _mark_deliverable_written(intake.case_id, intake.workflow)

    elif choice == "9":
        # Case Tracker
        from workflows.case_tracker import run_case_tracker
        run_case_tracker(console)

    elif choice == "10":
        # Browse SOPs
        from workflows.browse_sops import run_browse_sops
        run_browse_sops(console)

    elif choice == "11":
        # Due Diligence
        from ui.guided_intake import run_generic_intake
        from workflows.due_diligence import run_due_diligence_workflow

        intake = run_generic_intake(console, "due_diligence", "Due Diligence")
        if intake:
            _persist_intake(intake)
            result = run_due_diligence_workflow(
                intake, registry, hook_engine, console=console,
                on_progress=progress.make_callback(),
            )
            _mark_deliverable_written(intake.case_id, intake.workflow)
            from ui.display import render_deliverable_summary
            render_deliverable_summary(console, result)

    elif choice == "12":
        # Sanctions Screening
        from ui.guided_intake import run_generic_intake
        from workflows.sanctions_screening import run_sanctions_screening_workflow

        intake = run_generic_intake(console, "sanctions_screening", "Sanctions Screening")
        if intake:
            _persist_intake(intake)
            result = run_sanctions_screening_workflow(
                intake, registry, hook_engine, console=console,
                on_progress=progress.make_callback(),
            )
            _mark_deliverable_written(intake.case_id, intake.workflow)
            from ui.display import render_deliverable_summary
            render_deliverable_summary(console, result)

    elif choice == "13":
        # Transaction Testing
        from ui.guided_intake import run_generic_intake
        from workflows.transaction_testing import run_transaction_testing_workflow

        intake = run_generic_intake(console, "transaction_testing", "Transaction Testing")
        if intake:
            _persist_intake(intake)
            result = run_transaction_testing_workflow(
                intake, registry, hook_engine, console=console,
                on_progress=progress.make_callback(),
            )
            _mark_deliverable_written(intake.case_id, intake.workflow)
            from ui.display import render_deliverable_summary
            render_deliverable_summary(console, result)


def _select_or_create_intake(console: Console, workflow: str, label: str):
    """Let user select existing case or create minimal intake."""
    from config import CASES_DIR
    import json
    from rich.prompt import Confirm

    cases = []
    if CASES_DIR.exists():
        for cdir in sorted(CASES_DIR.iterdir()):
            intake_path = cdir / "intake.json"
            if intake_path.exists():
                try:
                    data = json.loads(intake_path.read_text(encoding="utf-8"))
                    cases.append(data)
                except Exception:
                    pass

    if cases:
        console.print("  Existing cases:")
        for i, c in enumerate(cases[:10], 1):
            console.print(f"    {i}. {c.get('case_id', '?')} — {c.get('client_name', '?')}")
        console.print("    N. New case")
        from rich.prompt import Prompt
        choice = Prompt.ask("  Select", default="1")
        if choice.upper() != "N":
            try:
                data = cases[int(choice) - 1]
                from schemas.case import CaseIntake
                return CaseIntake(**data)
            except (IndexError, ValueError, Exception):
                pass

    from ui.guided_intake import run_generic_intake
    return run_generic_intake(console, workflow, label)


def _persist_intake(intake) -> None:
    """Write intake.json + initial state.json for cases created via guided intake.

    Idempotent — skips state.json if already present (e.g. resumed case).
    Called by _dispatch() for all menu options that build CaseIntake in memory
    without going through the full new_case_intake wizard (options 2–8).
    """
    from core.state_machine import CaseStatus
    from tools.file_tools import append_audit_event, case_dir, write_state

    cdir = case_dir(intake.case_id)

    # Write intake.json atomically
    intake_path = cdir / "intake.json"
    if not intake_path.exists():
        tmp = intake_path.with_suffix(".tmp")
        tmp.write_text(intake.model_dump_json(indent=2), encoding="utf-8")
        os.replace(tmp, intake_path)

        # Write initial state only for fresh cases
        write_state(intake.case_id, {
            "case_id": intake.case_id,
            "workflow": intake.workflow,
            "status": CaseStatus.INTAKE_CREATED.value,
            "revision_rounds": {"junior": 0, "pm": 0},
            "last_updated": datetime.now(timezone.utc).isoformat(),
        })
        append_audit_event(intake.case_id, {
            "event": "case_created",
            "workflow": intake.workflow,
            "client": intake.client_name,
        })


def _mark_deliverable_written(case_id: str, workflow: str) -> None:
    """Transition a Mode B (Assisted) case to DELIVERABLE_WRITTEN terminal status."""
    from core.state_machine import CaseStatus
    from tools.file_tools import append_audit_event, read_state, write_state

    state = read_state(case_id) or {}
    state["status"] = CaseStatus.DELIVERABLE_WRITTEN.value
    state["last_updated"] = datetime.now(timezone.utc).isoformat()
    write_state(case_id, state)
    append_audit_event(case_id, {"event": "deliverable_written", "workflow": workflow})


def _run_document_ingestion(document_manager, console: Console) -> None:
    """Prompt consultant to register case documents before running a workflow.

    Skips silently if document_manager is None (API unavailable).
    Called in choices 2 (investigation) and 6 (FRM) after intake, before pipeline.
    """
    if document_manager is None:
        return

    from rich.prompt import Confirm, Prompt

    if not Confirm.ask("\n  Upload case documents before running?", default=False):
        return

    _DOC_TYPES = {
        "1": ("engagement_letter",    "engagement_docs"),
        "2": ("financial_records",    "evidence/financial_records"),
        "3": ("email",                "evidence/correspondence"),
        "4": ("interview_transcript", "evidence/interview_transcripts"),
        "5": ("contract",             "engagement_docs"),
        "6": ("corporate_document",   "evidence/corporate_documents"),
        "7": ("other",                "working_papers"),
    }

    console.print("  [dim]Type: 1=Engagement letter 2=Financial 3=Email "
                  "4=Transcript 5=Contract 6=Corporate doc 7=Other[/dim]")

    while True:
        filepath = Prompt.ask("  File path (Enter to finish)", default="")
        if not filepath.strip():
            break

        dt_choice = Prompt.ask("  Document type", choices=list(_DOC_TYPES.keys()), default="7")
        doc_type, default_folder = _DOC_TYPES[dt_choice]
        folder = Prompt.ask("  Destination folder", default=default_folder)

        try:
            from schemas.documents import DocumentProvenance
            provenance = DocumentProvenance(
                collection_method="consultant_upload",
                collected_at=datetime.now(timezone.utc),
                collector_role="consultant",
                scope_authorized_by="engagement_letter",
                source_hash="",
            )
            if doc_type == "engagement_letter":
                entry = document_manager.register_engagement_letter(filepath, provenance)
            else:
                entry = document_manager.register_document(filepath, folder, doc_type, provenance)
            console.print(f"  [green]Registered: {entry.filename} (doc_id: {entry.doc_id})[/green]")
        except FileNotFoundError:
            console.print(f"  [red]File not found: {filepath}[/red]")
        except Exception as e:
            console.print(f"  [yellow]Indexing failed ({e})[/yellow]")
            console.print("  [dim]Copy the file to the case folder manually; it can still be referenced in workflows.[/dim]")

        if not Confirm.ask("  Add another document?", default=False):
            break


def _load_firm_name() -> str:
    """Load firm name from firm_profile.json, fallback to default."""
    import json
    path = Path(__file__).parent / "firm_profile" / "firm_profile.json"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data.get("firm_name", "GoodWork Forensic Consulting")
        except Exception:
            pass
    return "GoodWork Forensic Consulting"


if __name__ == "__main__":
    main()
