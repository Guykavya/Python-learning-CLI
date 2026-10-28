"""Small terminal output helpers. No third-party dependencies."""

from __future__ import annotations

import os
import re
import shutil
import sys

_USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ

_CODES = {
    "bold": "1",
    "dim": "2",
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "magenta": "35",
    "cyan": "36",
}


_ANSI = re.compile(r"\033\[[0-9;]*m")


def color_enabled() -> bool:
    return _USE_COLOR


def vis_len(s: str) -> int:
    """Length as seen on screen, ignoring colour codes."""
    return len(_ANSI.sub("", s))


def style(text: str, *names: str) -> str:
    if not _USE_COLOR or not names:
        return text
    codes = ";".join(_CODES[n] for n in names)
    return f"\033[{codes}m{text}\033[0m"


def bold(t: str) -> str:
    return style(t, "bold")


def dim(t: str) -> str:
    return style(t, "dim")


def ok(t: str) -> str:
    return style(t, "green")


def warn(t: str) -> str:
    return style(t, "yellow")


def err(t: str) -> str:
    return style(t, "red")


def accent(t: str) -> str:
    return style(t, "cyan")


def bar(fraction: float, width: int = 10) -> str:
    fraction = max(0.0, min(1.0, fraction))
    filled = round(fraction * width)
    return "█" * filled + "░" * (width - filled)


def progress_bar(fraction: float, width: int = 10) -> str:
    """A coloured bar with a percentage: green when done, yellow in progress, dim when empty."""
    fraction = max(0.0, min(1.0, fraction))
    colour = "green" if fraction >= 1 else "yellow" if fraction > 0 else "dim"
    return style(bar(fraction, width), colour) + dim(f" {round(fraction * 100):>3}%")


BANNER = r"""
 ____  __   __ _____  _   _   ___   _   _
|  _ \ \ \ / /|_   _|| | | | / _ \ | \ | |
| |_) | \ V /   | |  | |_| || | | ||  \| |
|  __/   | |    | |  |  _  || |_| || |\  |
|_|      |_|    |_|  |_| |_| \___/ |_| \_|
"""[1:].splitlines()


def banner() -> None:
    """The fixed welcome art: top half blue, bottom half yellow, like the Python logo."""
    for i, line in enumerate(BANNER):
        print(style(line, "bold", "blue" if i < 3 else "yellow"))
    print(dim("  one problem at a time  ·  learn today  ·  learn next"))
    print()


def heading(text: str) -> None:
    print()
    print(bold(text))
    print(dim("─" * min(len(text) + 4, terminal_width())))


def terminal_width() -> int:
    return shutil.get_terminal_size((88, 24)).columns


def table(rows: list[list[str]], header: list[str] | None = None, indent: int = 2) -> None:
    """Print a simple aligned table. Cells may contain colour codes."""
    all_rows = ([header] if header else []) + rows
    if not all_rows:
        return
    ncols = max(len(r) for r in all_rows)
    widths = [0] * ncols
    for r in all_rows:
        for i, c in enumerate(r):
            widths[i] = max(widths[i], vis_len(c))
    pad = " " * indent
    for idx, r in enumerate(all_rows):
        cells = []
        for i, c in enumerate(r):
            cells.append(c + " " * (widths[i] - vis_len(c)))
        line = pad + "  ".join(cells).rstrip()
        print(bold(line) if header and idx == 0 else line)


def box(title: str, lines: list[str], color: str = "green", indent: int = 0) -> None:
    """Print lines inside a rounded frame with the title in the top edge."""
    pad = " " * indent
    inner = max([vis_len(title) + 4] + [vis_len(line) + 2 for line in lines])
    print(pad + style("╭─ ", color) + title + " " + style("─" * (inner - vis_len(title) - 3) + "╮", color))
    for line in lines:
        print(pad + style("│", color) + " " + line + " " * (inner - 1 - vis_len(line)) + style("│", color))
    print(pad + style("╰" + "─" * inner + "╯", color))


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        value = input(f"{prompt}{suffix}: ").strip()
    except EOFError:
        value = ""
    return value or default
