"""`learn shortcut`: a Desktop icon that opens a terminal in the course folder with `learn` ready.

Windows: a .lnk made by scripts/make_desktop_shortcut.ps1 (PowerShell, `learn` defined for that window).
Linux:   a .desktop launcher that starts a terminal emulator.
macOS:   a .command file, which Terminal opens when double-clicked.
The Linux and macOS starters read a small bash file that changes into the folder and defines `learn`.
"""

from __future__ import annotations

import os
import shlex
import shutil
import stat
import subprocess
import sys
from pathlib import Path

from learn import paths

NAME = "Python Learning"
ASSETS = "scripts/assets"


def _asset(name: str) -> Path:
    return paths.root() / ASSETS / name


def starter_text(root: Path) -> str:
    """The bash file the Linux and macOS starters run: opens in the course folder, defines `learn`."""
    folder = shlex.quote(str(root))
    launcher = shlex.quote(str(root / "learn"))
    return (
        "# Written by `learn shortcut`. Opens the course folder with `learn` ready.\n"
        '[ -f "$HOME/.bashrc" ] && . "$HOME/.bashrc"\n'
        f"cd {folder} || exit 1\n"
        f'learn() {{ {launcher} "$@"; }}\n'
        'echo "Starting Python Learning. Later, type: learn today   (the shell stays open after you quit)"\n'
        "learn\n"
    )


def starter_path() -> Path:
    base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / "python-learning" / "shortcut-bashrc.sh"


def _desktop_quote(text: str) -> str:
    """Quote one argument for a .desktop Exec= line (double quotes, with \\ " $ ` escaped)."""
    escaped = "".join("\\" + ch if ch in '\\"$`' else ch for ch in text)
    return f'"{escaped}"'


def terminal_command(starter: Path) -> list[str] | None:
    """The first terminal emulator that is installed, with the arguments that run the starter in it."""
    bash = ["bash", "--rcfile", str(starter), "-i"]
    options = [
        ("x-terminal-emulator", ["-e"]),
        ("gnome-terminal", ["--"]),
        ("konsole", ["-e"]),
        ("xfce4-terminal", ["-e"]),
        ("xterm", ["-e"]),
    ]
    for name, flag in options:
        if shutil.which(name):
            return [name, *flag, *bash]
    return None


def desktop_entry(root: Path, starter: Path, command: list[str], icon: Path) -> str:
    exec_line = " ".join(_desktop_quote(part) for part in command)
    return (
        "[Desktop Entry]\n"
        "Type=Application\n"
        f"Name={NAME}\n"
        "Comment=Open the Python course in a terminal\n"
        f"Exec={exec_line}\n"
        f"Path={root}\n"
        "Terminal=false\n"
        f"Icon={icon}\n"
        "Categories=Education;Development;\n"
    )


def command_file(starter: Path) -> str:
    """The macOS .command file: Terminal runs it when you double-click it."""
    return f"#!/bin/bash\nexec bash --rcfile {shlex.quote(str(starter))} -i\n"


def desktop_dir() -> Path:
    """The Desktop folder, including the one a redirected or localised Desktop uses on Linux."""
    try:
        out = subprocess.run(["xdg-user-dir", "DESKTOP"], capture_output=True, text=True, timeout=5).stdout.strip()
        if out:
            return Path(out)
    except (OSError, subprocess.SubprocessError):
        pass
    return Path.home() / "Desktop"


def _write(path: Path, text: str, executable: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    if executable:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def create(root: Path | None = None) -> str:
    """Make the icons for this platform: one on the Desktop, one in the course folder. Returns the text to show.

    Raises RuntimeError with a fix message when a step is impossible here.
    """
    root = (root or paths.root()).resolve()
    if sys.platform == "win32":
        return _create_windows(root)
    starter = starter_path()
    _write(starter, starter_text(root), executable=False)
    if sys.platform == "darwin":
        files = [desktop_dir() / f"{NAME}.command", root / f"{NAME}.command"]
        for target in files:
            _write(target, command_file(starter), executable=True)
        tip = "Double-click either one. Terminal opens in the course folder with `learn` ready."
    else:
        command = terminal_command(starter)
        if command is None:
            raise RuntimeError("No terminal program found (tried x-terminal-emulator, gnome-terminal, konsole, xfce4-terminal, xterm). "
                               "Open a terminal yourself and run: cd " + shlex.quote(str(root)) + " && ./learn")
        icon = _asset("learn.png")
        files = [desktop_dir() / f"{NAME}.desktop", root / f"{NAME}.desktop"]
        for target in files:
            _write(target, desktop_entry(root, starter, command, icon), executable=True)
            # GNOME (Ubuntu, Fedora) refuses to start a launcher until it is marked trusted. Best effort.
            if shutil.which("gio"):
                subprocess.run(["gio", "set", str(target), "metadata::trusted", "true"], capture_output=True)
        tip = 'Double-click either one. If GNOME asks, choose "Allow Launching".'
    return "\n".join(f"Created: {f}" for f in files) + "\n" + tip


def _create_windows(root: Path) -> str:
    script = root / "scripts" / "make_desktop_shortcut.ps1"
    if not script.exists():
        raise RuntimeError(f"{script} is missing. Copy the course folder again.")
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError("Could not create the icons:\n" + (result.stdout + result.stderr).strip())
    return result.stdout.strip() + "\nDouble-click either one. PowerShell opens in the course folder with `learn` ready."
