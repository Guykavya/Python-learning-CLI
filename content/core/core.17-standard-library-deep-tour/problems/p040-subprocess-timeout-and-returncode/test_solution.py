import inspect
import time

import solution
from solution import describe_exit, first_success, run_limited

# All children are `sys.executable -c ...`. The only slow child sleeps for 10 seconds and must be
# stopped by a 0.5-second timeout, so a correct solution runs the whole file in about a second.

SLEEPER = "import time; time.sleep(10); print('too late')"


def test_ok():
    assert run_limited("print('hi')", 5) == ("ok", 0, "hi\n"), "Exit code 0 means 'ok'; return the captured stdout as text."


def test_failed_keeps_code_and_output():
    assert run_limited("import sys; print('half'); sys.exit(2)", 5) == ("failed", 2, "half\n"), (
        "A non-zero exit code is 'failed'. Keep the real returncode and whatever was printed before it stopped."
    )
    status, code, _ = run_limited("raise ValueError('x')", 5)
    assert (status, code) == ("failed", 1), "An uncaught exception exits with code 1."


def test_sys_exit_with_message_is_code_1():
    status, code, out = run_limited("import sys; sys.exit('giving up')", 5)
    assert (status, code, out) == ("failed", 1, ""), (
        "sys.exit('a message') prints the message to STDERR and exits with code 1."
    )


def test_sys_exit_zero_and_none_are_ok():
    assert run_limited("import sys; sys.exit(0)", 5)[:2] == ("ok", 0), "sys.exit(0) is success."
    assert run_limited("import sys; sys.exit()", 5)[:2] == ("ok", 0), "sys.exit() with no argument is also exit code 0."


def test_timeout_is_enforced():
    start = time.monotonic()
    result = run_limited(SLEEPER, 0.5)
    elapsed = time.monotonic() - start
    assert result == ("timeout", None, ""), (
        "Pass timeout= to subprocess.run and catch subprocess.TimeoutExpired: return ('timeout', None, '')."
    )
    assert elapsed < 5, (
        f"run_limited took {elapsed:.1f} s for a 0.5 s timeout. subprocess.run(timeout=...) kills the child; "
        "do not wait for it to finish."
    )


def test_timeout_does_not_raise():
    try:
        run_limited(SLEEPER, 0.5)
    except Exception as e:  # noqa: BLE001
        raise AssertionError(f"run_limited let {type(e).__name__} escape. Catch subprocess.TimeoutExpired.") from None


def test_describe_exit():
    assert describe_exit(None) == "timed out", "None (no exit code) means the child was stopped by the timeout."
    assert describe_exit(0) == "success", "0 means success."
    assert describe_exit(2) == "error (exit code 2)", "A positive code is the program's own error code."
    assert describe_exit(-9) == "killed by signal 9", (
        "On Linux and macOS a NEGATIVE returncode -N means the child was killed by signal N (for example 9, SIGKILL)."
    )
    assert describe_exit(-15) == "killed by signal 15", "-15: killed by signal 15 (SIGTERM)."


def test_first_success_order_and_stopping(tmp_path):
    marker = tmp_path / "ran.txt"
    later = f"open({str(marker)!r}, 'w').close()"
    snippets = ["import sys; sys.exit(1)", SLEEPER, "print('ok')", later]
    start = time.monotonic()
    assert first_success(snippets, 0.5) == 2, (
        "Index 0 fails, index 1 times out (that is not a success), index 2 succeeds: return 2."
    )
    assert time.monotonic() - start < 6, "The sleeping snippet must be cut off by the timeout."
    assert not marker.exists(), "Stop at the first success: the snippet after it must NOT be run."


def test_first_success_none():
    assert first_success(["import sys; sys.exit(3)", "1/0"], 5) == -1, "No snippet succeeds: -1."
    assert first_success([], 5) == -1, "No snippets: -1."


def test_no_shell():
    src = inspect.getsource(solution)
    assert "shell=True" not in src, "Do not use shell=True; pass [sys.executable, '-c', code]."
