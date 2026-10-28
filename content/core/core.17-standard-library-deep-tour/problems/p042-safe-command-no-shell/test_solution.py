import json
import subprocess
import sys
from pathlib import Path

import pytest

from solution import build_command, run_script

ECHO = "import json, sys\nprint(json.dumps(sys.argv[1:]))\n"


@pytest.fixture
def echo(tmp_path):
    script = tmp_path / "echo_args.py"
    script.write_text(ECHO, encoding="utf-8")
    return script


def test_build_command_list():
    cmd = build_command("tool.py", ["a b", "c"])
    assert isinstance(cmd, list), "build_command must return a LIST of strings, not one command string."
    assert cmd == [sys.executable, "tool.py", "a b", "c"], (
        "Expected [sys.executable, script, *args]. 'a b' stays ONE item: never split arguments on spaces."
    )


def test_build_command_uses_sys_executable():
    cmd = build_command("tool.py", [])
    assert cmd[0] == sys.executable, (
        "The first item must be sys.executable (the Python running now), not 'python', which may be another interpreter."
    )
    assert cmd == [sys.executable, "tool.py"], "No arguments: just the interpreter and the script."


def test_build_command_path_and_tuple(tmp_path):
    script = tmp_path / "x.py"
    args = ("1", "2")
    cmd = build_command(script, args)
    assert cmd == [sys.executable, str(script), "1", "2"], "Convert a Path script with str(script); args may be a tuple."
    assert all(isinstance(part, str) for part in cmd), "Every item of the command must be a str."


def test_build_command_rejects_non_str():
    with pytest.raises(TypeError):
        build_command("tool.py", ["ok", 3])


def test_run_script_simple(echo):
    out = run_script(echo, ["one", "two"])
    assert isinstance(out, str), "Return stdout as text: pass text=True (or encoding=...) to subprocess.run."
    assert json.loads(out) == ["one", "two"], "The helper should receive exactly the two arguments you passed."


PAYLOADS = [
    "Asha Rao",
    "Asha; echo HACKED",
    "x && echo HACKED",
    "x | echo HACKED",
    "$(echo HACKED)",
    "`echo HACKED`",
    "%PATH%",
    "*.py",
    'say "hi"',
    "it's",
    "a > out.txt",
    "",
]


@pytest.mark.parametrize("payload", PAYLOADS)
def test_dangerous_text_arrives_unchanged(echo, payload):
    out = run_script(echo, [payload])
    assert json.loads(out) == [payload], (
        f"The argument {payload!r} must arrive as ONE unchanged argument. If it was split, expanded or "
        "ran a second command, a shell read it: pass a list and do not use shell=True."
    )


def test_no_file_created_by_injection(echo, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run_script(echo, ["x; echo pwned > pwned.txt", "x & echo pwned > pwned.txt"])
    assert not (tmp_path / "pwned.txt").exists(), "A shell ran the '>' redirection: never use shell=True with user text."


def test_uses_subprocess_run_safely(echo, monkeypatch):
    calls = []
    real_run = subprocess.run

    def spy(*args, **kwargs):
        calls.append((args, kwargs))
        return real_run(*args, **kwargs)

    monkeypatch.setattr(subprocess, "run", spy)
    run_script(echo, ["a"], timeout=7)
    assert calls, "Call subprocess.run (with `import subprocess`) so the tests can check how you run the program."
    args, kwargs = calls[0]
    command = args[0] if args else kwargs.get("args")
    assert isinstance(command, list), "The command passed to subprocess.run must be a list, not a string."
    assert not kwargs.get("shell", False), "shell=True lets the shell interpret the text: leave shell at its default False."
    assert kwargs.get("timeout") == 7, "Pass timeout=timeout to subprocess.run so a stuck helper cannot hang forever."


def test_nonzero_exit_raises(tmp_path):
    bad = tmp_path / "fail.py"
    bad.write_text("import sys\nprint('oops', file=sys.stderr)\nsys.exit(3)\n", encoding="utf-8")
    with pytest.raises(subprocess.CalledProcessError) as info:
        run_script(bad, [])
    assert info.value.returncode == 3, "The CalledProcessError should carry the helper's exit code (3)."


def test_script_path_with_spaces(tmp_path):
    folder = tmp_path / "my scripts"
    folder.mkdir()
    script = folder / "echo args.py"
    script.write_text(ECHO, encoding="utf-8")
    out = run_script(script, ["ok"])
    assert json.loads(out) == ["ok"], "A script path with spaces must work: as a list item it is never split."
