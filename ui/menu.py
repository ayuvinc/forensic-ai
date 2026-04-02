"""Main menu — 10-item Rich terminal menu."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from ui.display import print_header


MENU_ITEMS = [
    # (option, category, label, description)
    ("1",  "INVESTIGATION",  "New Case Intake",               "Create a new case folder and set up structure"),
    ("2",  "INVESTIGATION",  "Investigation Report",          "Full pipeline — Junior > PM > Partner review"),
    ("3",  "INVESTIGATION",  "Persona Review",                "Review deliverable through CFO/Lawyer/Regulator/Adjuster lens"),
    ("4",  "COMPLIANCE",     "Policy / SOP Generator",        "Assisted — draft or gap-analyse policies and SOPs"),
    ("5",  "COMPLIANCE",     "Training Material",             "Assisted — role-specific training content"),
    ("6",  "COMPLIANCE",     "FRM Risk Register",             "Full pipeline — Fraud Risk Management Register"),
    ("7",  "BUSINESS",       "Create Client Proposal",        "Assisted — 7-section forensic engagement proposal"),
    ("8",  "BUSINESS",       "Build Proposal PPT Prompt Pack", "Assisted — slide storyboard + per-slide prompts"),
    ("9",  "BUSINESS",       "Case Tracker",                  "View all cases and resume in-progress work"),
    ("10", "BUSINESS",       "Browse SOPs",                   "Browse saved SOPs and policies"),
]


def render_menu(console: Console, firm_name: str = "GoodWork Forensic Consulting") -> str:
    """Render the main menu and return the selected option."""
    print_header(console, firm_name)
    console.print()

    current_category = None
    for opt, category, label, desc in MENU_ITEMS:
        if category != current_category:
            console.print(f"\n[bold dim][ {category} ][/bold dim]")
            current_category = category
        console.print(f"  [bold cyan]{opt:>2}[/bold cyan]  {label}  [dim]{desc}[/dim]")

    console.print("\n  [bold dim]0[/bold dim]  [dim]Exit[/dim]")
    console.print()

    return Prompt.ask(
        "Select option",
        choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
        default="6",
    )
