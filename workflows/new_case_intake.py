"""New case intake workflow.

Creates case folder, checks engagement letter gate, sets up document structure.
Exempt from engagement letter pre-hook (this IS the intake).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from config import CASES_DIR
from schemas.case import CaseIntake, CaseState
from core.state_machine import CaseStatus
from tools.file_tools import write_state, append_audit_event, case_dir


SUPPORTED_WORKFLOWS = {
    "1": "investigation_report",
    "2": "frm_risk_register",
    "3": "client_proposal",
    "4": "proposal_deck",
    "5": "policy_sop",
    "6": "training_material",
}


def run_new_case_intake(console: Console) -> Optional[CaseIntake]:
    """Conversational intake — one question at a time. Returns CaseIntake or None if cancelled."""
    console.print(Panel(
        "[bold cyan]New Case Intake[/bold cyan]\n"
        "I'll ask you a few questions to set up the case folder.",
        border_style="cyan",
    ))

    # Client details
    client_name = Prompt.ask("\n  Client name")
    if not client_name.strip():
        console.print("  [yellow]Cancelled.[/yellow]")
        return None

    industry = Prompt.ask("  Industry / sector")
    company_size = Prompt.ask("  Approximate company size (employees)", default="")

    # Jurisdiction
    primary_j = Prompt.ask("  Primary jurisdiction", default="UAE")
    ops_j_raw = Prompt.ask(
        "  Operating jurisdictions (comma-separated, or Enter for same as primary)",
        default="",
    )
    operating_j = [j.strip() for j in ops_j_raw.split(",") if j.strip()] or [primary_j]

    # Workflow selection
    console.print("\n  Workflow type:")
    for k, v in SUPPORTED_WORKFLOWS.items():
        console.print(f"    {k}. {v.replace('_', ' ').title()}")
    workflow_choice = Prompt.ask("  Select workflow", choices=list(SUPPORTED_WORKFLOWS.keys()), default="1")
    workflow = SUPPORTED_WORKFLOWS[workflow_choice]

    # Description
    description = Prompt.ask("\n  Brief description of the engagement")
    language = Prompt.ask("  Primary language (en/ar)", choices=["en", "ar"], default="en")

    # Generate case ID
    case_id = f"{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
    console.print(f"\n  [green]Case ID: {case_id}[/green]")

    intake = CaseIntake(
        case_id=case_id,
        client_name=client_name,
        industry=industry,
        company_size=company_size or None,
        primary_jurisdiction=primary_j,
        operating_jurisdictions=operating_j,
        workflow=workflow,
        description=description,
        language=language,
        created_at=datetime.now(timezone.utc),
    )

    # Create case folder
    case_folder = case_dir(case_id)
    console.print(f"  Case folder: {case_folder}")

    # Propose and confirm folder structure
    console.print("\n  [bold]Document folder structure[/bold]")
    folders = _default_folders(workflow)
    console.print("  Proposed folders:")
    for f in folders:
        console.print(f"    - {f}")

    if Confirm.ask("  Use this structure?", default=True):
        for folder in folders:
            (case_folder / folder).mkdir(parents=True, exist_ok=True)
        console.print("  [green]Folders created.[/green]")

    # Engagement letter
    console.print(
        "\n  [bold]Engagement letter[/bold]\n"
        "  For best results, please copy your signed engagement letter/contract to:\n"
        f"  [cyan]{case_folder / 'engagement_docs'}[/cyan]\n"
        "  This defines scope, limitations, and authorizations for the entire case."
    )
    eng_letter_path = Prompt.ask(
        "  Path to engagement letter (or Enter to add later)", default=""
    )
    if eng_letter_path.strip():
        intake = intake.model_copy(update={"engagement_letter_path": eng_letter_path.strip()})

    # Write initial state
    state = {
        "case_id": case_id,
        "workflow": workflow,
        "status": CaseStatus.INTAKE_CREATED.value,
        "revision_rounds": {"junior": 0, "pm": 0},
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
    write_state(case_id, state)
    append_audit_event(case_id, {
        "event": "case_created",
        "workflow": workflow,
        "client": client_name,
    })

    # Save intake
    import json, os
    intake_path = case_folder / "intake.json"
    tmp = intake_path.with_suffix(".tmp")
    tmp.write_text(intake.model_dump_json(indent=2), encoding="utf-8")
    os.replace(tmp, intake_path)

    console.print(Panel(
        f"[bold green]Case {case_id} created[/bold green]\n\n"
        f"Client: {client_name}\n"
        f"Workflow: {workflow.replace('_', ' ').title()}\n"
        f"Folder: {case_folder}",
        border_style="green",
    ))

    # C-04b: Offer document ingestion inline after case creation
    if Confirm.ask("\n  Upload documents to this case now?", default=False):
        _offer_document_ingestion(console, case_id, case_folder)

    return intake


def _offer_document_ingestion(console: Console, case_id: str, case_folder: Path) -> None:
    """Register documents into the case folder at intake time."""
    try:
        from tools.document_manager import DocumentManager
        dm = DocumentManager(case_id)
    except Exception as e:
        console.print(f"  [yellow]Document manager unavailable: {e}[/yellow]")
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

    console.print("  [dim]1=Engagement letter 2=Financial 3=Email "
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
                entry = dm.register_engagement_letter(filepath, provenance)
            else:
                entry = dm.register_document(filepath, folder, doc_type, provenance)
            console.print(f"  [green]Registered: {entry.filename} (doc_id: {entry.doc_id})[/green]")
        except FileNotFoundError:
            console.print(f"  [red]File not found: {filepath}[/red]")
        except Exception as e:
            console.print(f"  [yellow]Indexing failed ({e})[/yellow]")
            console.print(
                f"  [dim]Copy the file to {case_folder / folder} manually; "
                "it can be referenced in workflows.[/dim]"
            )

        if not Confirm.ask("  Add another?", default=False):
            break


def _default_folders(workflow: str) -> list[str]:
    base = ["engagement_docs", "reports", "working_papers"]
    extras = {
        "investigation_report": [
            "evidence/financial_records",
            "evidence/correspondence",
            "evidence/interview_transcripts",
            "evidence/corporate_documents",
        ],
        "frm_risk_register": [
            "client_documents",
            "policies_procedures",
            "org_structure",
        ],
        "client_proposal": [
            "client_background",
            "reference_materials",
        ],
        "proposal_deck": [
            "deck_assets",
        ],
        "policy_sop": [
            "existing_policies",
            "regulatory_references",
        ],
        "training_material": [
            "source_material",
            "case_studies",
        ],
    }
    return base + extras.get(workflow, [])
