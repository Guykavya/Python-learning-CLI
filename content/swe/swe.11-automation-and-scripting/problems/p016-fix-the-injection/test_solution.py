import inspect
import subprocess

import pytest

import solution
from solution import count_lines


def make(folder, name, lines):
    path = folder / name
    path.write_text("".join(f"line {i}\n" for i in range(lines)), encoding="utf-8")
    return path


def test_plain_name(tmp_path):
    assert count_lines(make(tmp_path, "notes.txt", 3)) == 3, "notes.txt has 3 lines."


def test_space_in_the_name(tmp_path):
    assert count_lines(make(tmp_path, "my notes.txt", 2)) == 2, \
        "With a shell string, 'my notes.txt' becomes two arguments. Pass a LIST so the name stays one argument."


def test_semicolon_cannot_start_a_second_command(tmp_path):
    path = make(tmp_path, "x; echo HACKED", 2)
    try:
        result = count_lines(path)
    except (ValueError, IndexError):
        pytest.fail("The shell treated ';' as a command separator and ran 'echo HACKED'. Do not use shell=True; pass a list.")
    assert result == 2, "The whole name 'x; echo HACKED' is one file with 2 lines."


def test_quote_in_the_name(tmp_path):
    assert count_lines(make(tmp_path, "it's.txt", 4)) == 4, "A single quote must not break anything: no shell, no quoting problems."


def test_dollar_in_the_name(tmp_path):
    assert count_lines(make(tmp_path, "$(echo hi).txt", 1)) == 1, "'$(...)' must stay text, not become a command substitution."


def test_missing_file_raises(tmp_path):
    with pytest.raises(subprocess.CalledProcessError):
        count_lines(tmp_path / "missing.txt")


def test_no_shell_and_a_timeout():
    source = inspect.getsource(solution.count_lines)
    assert "shell=True" not in source, "Remove shell=True: the list form needs no shell."
    assert "timeout" in source, "Give the child a timeout so a stuck process cannot freeze the caller."
    assert "check=True" in source, "Use check=True so a failing child raises CalledProcessError."
