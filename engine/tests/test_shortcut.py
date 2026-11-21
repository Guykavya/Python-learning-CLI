"""`learn shortcut`: the generated starter, launcher and terminal choice (pure logic, no Desktop is touched)."""

from pathlib import Path

from learn import shortcut

ROOT = Path("/home/someone/My Courses/learning module")  # a folder with a space, like most real ones


def test_starter_opens_the_folder_and_defines_learn():
    text = shortcut.starter_text(ROOT)
    assert f"cd '{ROOT}' || exit 1" in text, "the starter must change into the course folder, quoted, so spaces work"
    assert f"learn() {{ '{ROOT / 'learn'}' \"$@\"; }}" in text, "`learn` must run the course launcher with all arguments"


def test_starter_quotes_an_apostrophe_in_the_path():
    text = shortcut.starter_text(Path("/home/anne/Anne's course"))
    assert "'/home/anne/Anne'\"'\"'s course'" in text, "an apostrophe in the folder name would break the starter script"


def test_desktop_exec_line_quotes_every_argument(tmp_path):
    starter = tmp_path / "start with space.sh"
    entry = shortcut.desktop_entry(ROOT, starter, ["x-terminal-emulator", "-e", "bash", "--rcfile", str(starter), "-i"], Path("/i.png"))
    exec_line = next(line for line in entry.splitlines() if line.startswith("Exec="))
    assert f'"{starter}"' in exec_line, "a path with a space must be one quoted argument in the Exec= line"
    assert f"Path={ROOT}" in entry, "the desktop entry must start in the course folder"
    assert "Terminal=false" in entry, "the terminal is started by Exec itself, so Terminal must be false"


def test_macos_command_file_runs_the_starter():
    text = shortcut.command_file(Path("/Users/me/start.sh"))
    assert text.startswith("#!/bin/bash\n"), "Terminal runs a .command file only if it starts with a shell line"
    assert "--rcfile /Users/me/start.sh" in text, "the .command file must start bash with our starter"


def test_terminal_is_the_first_one_installed(monkeypatch):
    installed = {"gnome-terminal", "xterm"}
    monkeypatch.setattr(shortcut.shutil, "which", lambda name: f"/usr/bin/{name}" if name in installed else None)
    cmd = shortcut.terminal_command(Path("/s.sh"))
    assert cmd[0] == "gnome-terminal" and cmd[1] == "--", "gnome-terminal takes -- before the command, not -e"
    monkeypatch.setattr(shortcut.shutil, "which", lambda name: None)
    assert shortcut.terminal_command(Path("/s.sh")) is None, "with no terminal installed, say so instead of guessing"


def test_starter_starts_the_program_by_itself():
    lines = shortcut.starter_text(ROOT).splitlines()
    assert lines[-1] == "learn", "the terminal must start the program on its own, not wait for the learner to type it"


import sys

import pytest


@pytest.mark.skipif(sys.platform != "linux", reason="writes .desktop files; Windows and macOS use other files")
def test_create_writes_a_desktop_icon_and_a_folder_icon(tmp_path, monkeypatch):
    course = tmp_path / "My Course"
    course.mkdir()
    desk = tmp_path / "Desk top"
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    monkeypatch.setattr(shortcut, "desktop_dir", lambda: desk)
    monkeypatch.setattr(shortcut, "terminal_command", lambda starter: ["xterm", "-e", "bash", "--rcfile", str(starter), "-i"])
    message = shortcut.create(course)
    assert (desk / "Python Learning.desktop").exists(), "the Desktop icon must be created"
    assert (course / "Python Learning.desktop").exists(), "the icon in the course folder must be created"
    assert str(course / "Python Learning.desktop") in message, "the user must be told where the icons are"
