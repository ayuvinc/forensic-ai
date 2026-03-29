"""Progress display — Rich spinner/progress for pipeline stages."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn


class ProgressContext:
    """Context manager for displaying progress during pipeline runs."""

    def __init__(self, console: Console):
        self.console = console
        self._progress: Progress | None = None
        self._task_id = None

    @contextmanager
    def stage(self, description: str) -> Generator[None, None, None]:
        """Show a spinner for a named stage."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        ) as progress:
            task = progress.add_task(description, total=None)
            try:
                yield
            finally:
                progress.remove_task(task)

    def log(self, message: str, style: str = "cyan") -> None:
        """Print a progress message."""
        self.console.print(f"  [{style}]{message}[/{style}]")

    def success(self, message: str) -> None:
        self.log(message, style="green")

    def warn(self, message: str) -> None:
        self.log(message, style="yellow")

    def error(self, message: str) -> None:
        self.log(message, style="red")

    def make_callback(self) -> callable:
        """Return a simple on_progress callback."""
        def callback(msg: str) -> None:
            self.log(msg)
        return callback
