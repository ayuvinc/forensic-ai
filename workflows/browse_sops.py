"""Browse SOPs — list and display SOP documents from sops/ folder."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from config import SOPS_DIR


def run_browse_sops(console: Console) -> None:
    """Browse and display SOP documents."""
    if not SOPS_DIR.exists() or not any(SOPS_DIR.iterdir()):
        console.print("[yellow]No SOPs found in sops/ folder.[/yellow]")
        console.print("SOPs generated via Policy / SOP Generator (Option 4) are saved here.")
        return

    sops = sorted(SOPS_DIR.glob("**/*.md")) + sorted(SOPS_DIR.glob("**/*.txt"))

    if not sops:
        console.print("[yellow]No SOP files found.[/yellow]")
        return

    console.print(f"\n[bold]Available SOPs ({len(sops)})[/bold]")
    for i, sop in enumerate(sops, 1):
        size_kb = sop.stat().st_size / 1024
        console.print(f"  {i:2d}. {sop.name} ({size_kb:.1f} KB)")

    choice = Prompt.ask("\nSelect SOP to view (number, or Enter to cancel)", default="")
    if not choice.strip():
        return

    try:
        selected = sops[int(choice) - 1]
        content = selected.read_text(encoding="utf-8")
        # Display first 3000 chars
        preview = content[:3000]
        if len(content) > 3000:
            preview += "\n\n[... truncated — open file for full content ...]"

        console.print(Panel(
            preview,
            title=selected.name,
            border_style="cyan",
        ))
        console.print(f"\nFull path: [cyan]{selected}[/cyan]")
    except (IndexError, ValueError):
        console.print("[red]Invalid selection.[/red]")
