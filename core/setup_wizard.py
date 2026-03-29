"""Setup wizard — first-time environment configuration.

Phase 1 scope: .env creation, dependency verification, API key validation.
Phase 2 extension: firm profile setup (firm name, team, pricing, T&C).
"""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

BASE_DIR = Path(__file__).parent.parent


def run_first_time_setup(console: Console) -> None:
    """Guide the user through first-time setup (env + deps)."""
    console.print(Panel(
        "[bold cyan]Welcome to the Forensic Consulting Framework[/bold cyan]\n\n"
        "It looks like this is your first time here — let me get you set up.\n"
        "This takes about 5 minutes.",
        border_style="cyan",
    ))

    # Step 1 — Python version
    console.print("\n[bold]Step 1 — Checking Python version...[/bold]")
    _check_python(console)

    # Step 2 — Virtual environment
    console.print("\n[bold]Step 2 — Virtual environment[/bold]")
    _guide_venv(console)

    # Step 3 — Dependencies
    console.print("\n[bold]Step 3 — Install dependencies[/bold]")
    _guide_deps(console)

    # Step 4 — API keys
    console.print("\n[bold]Step 4 — API keys[/bold]")
    _guide_api_keys(console)

    # Step 5 — Create .env
    console.print("\n[bold]Step 5 — Create .env file[/bold]")
    _create_env(console)

    # Step 6 — Verify
    console.print("\n[bold]Step 6 — Verifying installation...[/bold]")
    _verify_deps(console)

    console.print(Panel(
        "[bold green]Setup complete![/bold green]\n\n"
        "Run [cyan]python run.py[/cyan] to launch the framework.",
        border_style="green",
    ))


def _check_python(console: Console) -> None:
    major, minor = sys.version_info[:2]
    if (major, minor) >= (3, 11):
        console.print(f"  [green]Python {major}.{minor} — OK[/green]")
    else:
        console.print(f"  [red]Python {major}.{minor} detected — Python 3.11+ required.[/red]")
        console.print("  Please install from [link]https://python.org[/link] and restart.")
        Prompt.ask("  Press Enter once you have Python 3.11+ installed")


def _guide_venv(console: Console) -> None:
    is_windows = platform.system() == "Windows"
    activate = r"venv\Scripts\activate" if is_windows else "source venv/bin/activate"

    console.print("  Create and activate a virtual environment by running:")
    console.print(f"  [cyan]python3 -m venv venv[/cyan]")
    console.print(f"  [cyan]{activate}[/cyan]")
    console.print("  You will see [cyan](venv)[/cyan] in your prompt when active.")
    Confirm.ask("  Virtual environment activated?", default=True)


def _guide_deps(console: Console) -> None:
    console.print("  Run: [cyan]pip install -r requirements.txt[/cyan]")
    Confirm.ask("  Dependencies installed without errors?", default=True)


def _guide_api_keys(console: Console) -> None:
    console.print(
        "  You need two API keys:\n"
        "  1. [bold]ANTHROPIC_API_KEY[/bold] — "
        "https://console.anthropic.com → API Keys → Create Key\n"
        "  2. [bold]TAVILY_API_KEY[/bold] — "
        "https://app.tavily.com → free account → dashboard"
    )
    Confirm.ask("  Do you have both keys ready?", default=True)


def _create_env(console: Console) -> None:
    env_example = BASE_DIR / ".env.example"
    env_file = BASE_DIR / ".env"

    if env_file.exists():
        console.print("  [green].env already exists — skipping.[/green]")
        return

    if env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        console.print("  [green]Copied .env.example to .env[/green]")
    else:
        env_file.write_text(
            "ANTHROPIC_API_KEY=sk-ant-\nTAVILY_API_KEY=tvly-\nBUDGET_MODE=balanced\n",
            encoding="utf-8",
        )
        console.print("  [green]Created .env[/green]")

    console.print("  Open [cyan].env[/cyan] in any text editor and paste your API keys.")
    console.print("  Format:")
    console.print("    [cyan]ANTHROPIC_API_KEY=sk-ant-...[/cyan]")
    console.print("    [cyan]TAVILY_API_KEY=tvly-...[/cyan]")
    Confirm.ask("  .env file saved with your keys?", default=True)


def _verify_deps(console: Console) -> None:
    check = (
        "import anthropic, rich, pydantic, openpyxl, pandas, pdfplumber; "
        "print('Dependencies OK')"
    )
    result = subprocess.run(
        [sys.executable, "-c", check],
        capture_output=True, text=True,
    )
    if "Dependencies OK" in result.stdout:
        console.print("  [green]All dependencies verified — OK[/green]")
    else:
        console.print(f"  [yellow]Warning: {result.stderr.strip() or 'Some packages may be missing'}[/yellow]")
        console.print("  Run [cyan]pip install -r requirements.txt[/cyan] to resolve.")


# ── Phase 2: Firm profile setup ───────────────────────────────────────────────

def run_firm_profile_setup(console: Console) -> None:
    """Collect firm name, logo, team bios, T&C, pricing model.
    Called after Phase 1 QA gate passes.
    Writes firm_profile/ folder with JSON config files.
    """
    import json

    firm_dir = BASE_DIR / "firm_profile"
    firm_dir.mkdir(exist_ok=True)

    console.print(Panel(
        "[bold cyan]Firm Profile Setup[/bold cyan]\n\n"
        "Let me collect some information about your firm.\n"
        "Your firm name will appear on all reports, proposals, and deliverables.\n"
        "This is saved locally and used in every document.",
        border_style="cyan",
    ))

    # Firm basics
    firm_name = Prompt.ask("  Your firm name", default="GoodWork LLC")
    logo_path = Prompt.ask("  Logo file path (leave blank to skip)", default="")
    website   = Prompt.ask("  Website (optional)", default="")

    firm_profile = {
        "firm_name": firm_name,
        "logo_path": logo_path or None,
        "website": website or None,
    }

    _atomic_write(firm_dir / "firm_profile.json", json.dumps(firm_profile, indent=2))
    console.print("  [green]Firm profile saved.[/green]")

    # Team members
    console.print("\n  [bold]Team members[/bold] (press Enter with blank name to finish)")
    team = []
    while True:
        name = Prompt.ask("    Member name (or Enter to finish)", default="")
        if not name:
            break
        role = Prompt.ask("    Role / title")
        bio  = Prompt.ask("    Short bio (1-2 sentences)")
        team.append({"name": name, "role": role, "bio": bio})

    _atomic_write(firm_dir / "team.json", json.dumps(team, indent=2))
    console.print(f"  [green]{len(team)} team member(s) saved.[/green]")

    # Pricing model
    console.print("\n  [bold]Pricing model[/bold]")
    console.print("  Options: hourly / daily / lump_sum / retainer / mixed")
    pricing_type = Prompt.ask("  Default pricing model", default="daily")
    currency     = Prompt.ask("  Currency", default="AED")
    partner_rate = Prompt.ask("  Partner rate", default="")
    pm_rate      = Prompt.ask("  Senior/PM rate", default="")
    junior_rate  = Prompt.ask("  Junior analyst rate", default="")

    pricing = {
        "model": pricing_type,
        "currency": currency,
        "rates": {
            "partner": partner_rate,
            "pm": pm_rate,
            "junior": junior_rate,
        },
    }
    _atomic_write(firm_dir / "pricing_model.json", json.dumps(pricing, indent=2))
    console.print("  [green]Pricing model saved.[/green]")

    # T&C
    console.print("\n  [bold]Terms & Conditions[/bold]")
    tc_path = Prompt.ask(
        "  Path to T&C file (Word/PDF), or leave blank to enter text directly", default=""
    )
    if tc_path:
        tc_data = {"tc_file_path": tc_path, "tc_text": None}
    else:
        console.print("  Paste your standard T&C text (Enter a blank line twice to finish):")
        lines = []
        blank_count = 0
        while blank_count < 2:
            line = Prompt.ask("  ", default="")
            if not line:
                blank_count += 1
            else:
                blank_count = 0
            lines.append(line)
        tc_data = {"tc_file_path": None, "tc_text": "\n".join(lines).strip()}

    _atomic_write(firm_dir / "terms_conditions.json", json.dumps(tc_data, indent=2))
    console.print("  [green]Terms & Conditions saved.[/green]")

    console.print(Panel(
        "[bold green]Firm profile complete![/bold green]\n\n"
        f"Files saved to [cyan]{firm_dir}[/cyan]",
        border_style="green",
    ))


def _atomic_write(path: Path, content: str) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(content, encoding="utf-8")
    import os
    os.replace(tmp, path)


def is_firm_profile_complete() -> bool:
    """Return True if firm profile has been set up."""
    firm_dir = BASE_DIR / "firm_profile"
    return (firm_dir / "firm_profile.json").exists()
