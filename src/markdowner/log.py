from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

from rich.console import Console

_console = Console(stderr=True, highlight=False)
_quiet = False


def set_quiet(quiet: bool) -> None:
    global _quiet
    _quiet = quiet


def info(msg: str) -> None:
    if not _quiet:
        _console.print(msg)


@dataclass
class StageCtx:
    detail: str | None = None


@contextmanager
def stage(msg: str) -> Iterator[StageCtx]:
    """Live spinner on stderr; replaced with ✓/✗ line + elapsed + optional detail on exit."""
    ctx = StageCtx()
    if _quiet:
        yield ctx
        return

    t0 = time.monotonic()
    status = _console.status(f"[cyan]{msg}[/cyan]", spinner="dots")
    status.start()
    try:
        yield ctx
    except BaseException:
        status.stop()
        elapsed = time.monotonic() - t0
        _console.print(f"[red]✗[/red] {msg} [dim]({elapsed:.1f}s)[/dim]")
        raise
    else:
        status.stop()
        elapsed = time.monotonic() - t0
        tail = f" — [dim]{ctx.detail}[/dim]" if ctx.detail else ""
        _console.print(f"[green]✓[/green] {msg}{tail} [dim]({elapsed:.1f}s)[/dim]")
