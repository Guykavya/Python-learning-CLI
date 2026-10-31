import inspect

import pytest

import solution
from solution import echo_args, run_or_raise, run_python

# Every child process here is `sys.executable -c ...`: the same Python that runs the tests,
# so these tests work the same on Linux, macOS and Windows, with no shell commands.


def test_uses_sys_executable_and_a_timeout():
    src = inspect.getsource(solution)
    assert "sys.executable" in src, (
        "Start the child with [sys.executable, '-c', code]. 'python' or 'python3' may not exist, or may be a "
        "different Python (without your packages)."
    )
    assert "timeout" in src, "Always pass timeout= to subprocess.run, so a stuck child cannot hang your program."
    assert "shell=True" not in src, "No shell: pass a list of arguments. shell=True is never needed here."


def test_run_python_stdout():
    code, out, err = run_python("print('hello'); print(6 * 7)")
    assert code == 0, "A program that ends normally exits with code 0."
    assert out == "hello\n42\n", (
        "Capture stdout as TEXT (capture_output=True, text=True). With text=True Windows '\\r\\n' becomes '\\n'. "
        "Return it exactly: do not strip it."
    )
    assert err == "", "Nothing was written to stderr."


def test_run_python_returns_str():
    _, out, err = run_python("print('x')")
    assert isinstance(out, str) and isinstance(err, str), "Without text=True you get bytes (b'x\\n'). Pass text=True."


def test_run_python_stdin():
    code, out, _ = run_python("import sys; print(len(sys.stdin.read().splitlines()))", "a\nb\nc\n")
    assert (code, out) == (0, "3\n"), "Send stdin_text with input=stdin_text; the child read 3 lines."


def test_run_python_empty_stdin_does_not_hang():
    code, out, _ = run_python("import sys; print(repr(sys.stdin.read()))")
    assert (code, out) == (0, "''\n"), (
        "With input='' the child sees an empty stdin and does not wait for the keyboard. Always pass input=..."
    )


def test_run_python_exit_code_and_stderr():
    code, out, err = run_python("import sys; print('partial'); sys.stderr.write('bad thing\\n'); sys.exit(3)")
    assert code == 3, "Return the child's exit code (proc.returncode): sys.exit(3) gives 3."
    assert out == "partial\n" and err == "bad thing\n", "Capture stdout and stderr SEPARATELY."


def test_run_python_does_not_raise_on_failure():
    code, _, err = run_python("1 / 0")
    assert code == 1, "An uncaught exception makes Python exit with code 1. run_python reports it; it must not raise."
    assert "ZeroDivisionError" in err, "The traceback goes to stderr."


def test_run_or_raise_ok():
    assert run_or_raise("print('fine')") == "fine\n", "On success, return the child's stdout."


def test_run_or_raise_failure_message():
    with pytest.raises(RuntimeError) as info:
        run_or_raise("1 / 0")
    assert str(info.value) == "ZeroDivisionError: division by zero", (
        "The error message must be the LAST non-empty line of the child's stderr, where the traceback names the error."
    )


def test_run_or_raise_exit_without_stderr():
    with pytest.raises(RuntimeError) as info:
        run_or_raise("import sys; sys.exit(4)")
    assert "4" in str(info.value), "With an empty stderr, say which exit code the child returned."


@pytest.mark.parametrize("args", [
    ["plain"],
    ["two words", "it's", 'say "hi"'],
    ["x; echo hacked", "$HOME", "*.py", "a|b", "&&"],
    ["", "--flag=1", "café"],
    [],
])
def test_echo_args_arrive_unchanged(args):
    assert echo_args(args) == args, (
        "Put the arguments in the LIST after the code: [sys.executable, '-c', code, *args]. With no shell in "
        "between, spaces, quotes, ; $ * | and empty strings arrive exactly as they were."
    )
