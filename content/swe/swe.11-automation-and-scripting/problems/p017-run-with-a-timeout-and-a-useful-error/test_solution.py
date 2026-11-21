import subprocess
import sys
import time

import pytest

from solution import ToolFailed, run_tool

FAIL = "import sys\nfor i in range(1, 9):\n    print(f'line {i}', file=sys.stderr)\nsys.exit(3)"
SLOW = "import sys, time\nprint('starting', file=sys.stderr, flush=True)\ntime.sleep(30)"


def py(code):
    return [sys.executable, "-c", code]


def test_success_returns_stdout():
    assert run_tool(py("print('hello from a child')"), timeout=10) == "hello from a child\n", "Return the child's stdout as text."


def test_non_zero_exit_becomes_tool_failed():
    with pytest.raises(ToolFailed) as info:
        run_tool(py(FAIL), timeout=10)
    e = info.value
    assert e.code == 3, "code is the child's exit code (check=True raises CalledProcessError with .returncode)."
    assert e.command == py(FAIL), "command is the list of arguments that was run."
    assert e.stderr_tail == ["line 4", "line 5", "line 6", "line 7", "line 8"], \
        f"Keep only the LAST 5 lines of stderr; got {e.stderr_tail}"


def test_message_says_what_how_and_why():
    with pytest.raises(ToolFailed) as info:
        run_tool(py(FAIL), timeout=10)
    msg = str(info.value)
    assert "failed with exit code 3" in msg, f"The message names the exit code; got {msg!r}"
    assert sys.executable in msg, "The message starts with the command that ran."
    assert "line 8" in msg and "line 3" not in msg, "The message ends with the 5-line tail (the reason), not the whole stderr."


def test_short_stderr_is_kept_whole():
    with pytest.raises(ToolFailed) as info:
        run_tool(py("import sys; print('fatal: no remote', file=sys.stderr); sys.exit(128)"), timeout=10)
    assert info.value.stderr_tail == ["fatal: no remote"] and info.value.code == 128


def test_timeout_becomes_tool_failed():
    start = time.monotonic()
    with pytest.raises(ToolFailed) as info:
        run_tool(py(SLOW), timeout=1)
    assert time.monotonic() - start < 15, "Pass timeout= to subprocess.run so the child is stopped."
    e = info.value
    assert e.code is None, "A timeout has no exit code: code is None."
    assert "timed out after 1s" in str(e), f"Message: '<command> timed out after 1s'; got {str(e)!r}"
    assert isinstance(e.stderr_tail, list) and all(isinstance(x, str) for x in e.stderr_tail), \
        "stderr_tail is a list of str even on a timeout (TimeoutExpired.stderr may be bytes or None)."


def test_missing_program():
    with pytest.raises(ToolFailed) as info:
        run_tool(["no-such-program-xyz-123"], timeout=5)
    assert info.value.code is None and "could not start" in str(info.value), "FileNotFoundError becomes ToolFailed too."


def test_the_cause_is_chained():
    with pytest.raises(ToolFailed) as info:
        run_tool(py(FAIL), timeout=10)
    assert isinstance(info.value.__cause__, subprocess.CalledProcessError), "Raise ToolFailed(...) from e to keep the original error."
