import sys

import pytest

from solution import capture, remove_if_exists, to_int_or


def noisy(n):
    print("hello", n)
    print("warning!", file=sys.stderr)
    print("line two")
    return n * 2


def test_capture_returns_result_and_text():
    result, out, err = capture(noisy, 4)
    assert result == 8, "capture returns the function's return value first."
    assert out == "hello 4\nline two\n", "Second item: everything the function printed to stdout (as one string, with newlines)."
    assert err == "warning!\n", "Third item: everything printed to stderr. Use redirect_stderr as well."


def test_capture_does_not_print_to_the_real_stdout(capsys):
    capture(noisy, 1)
    seen = capsys.readouterr()
    assert seen.out == "" and seen.err == "", "While captured, nothing may reach the real stdout or stderr."


def test_capture_restores_stdout_afterwards(capsys):
    capture(noisy, 1)
    print("after")
    assert capsys.readouterr().out == "after\n", "stdout must work normally again after capture() returns: use redirect_stdout in a `with`."


def test_capture_passes_args_and_kwargs():
    def f(a, b=0, *, c=0):
        print(a, b, c)
        return a + b + c

    assert capture(f, 1, 2, c=3) == (6, "1 2 3\n", ""), "Forward *args and **kwargs to the function."


def test_capture_function_without_output():
    assert capture(len, "abc") == (3, "", ""), "No output gives empty strings, not None."


def test_capture_restores_stdout_when_function_raises(capsys):
    def boom():
        print("partial")
        raise RuntimeError("x")

    with pytest.raises(RuntimeError):
        capture(boom)
    print("visible")
    assert capsys.readouterr().out == "visible\n", "Even if the function raises, stdout is restored (the exception propagates). `with redirect_stdout(...)` does it for you."


def test_remove_if_exists(tmp_path):
    p = tmp_path / "x.txt"
    p.write_text("x")
    assert remove_if_exists(str(p)) is True, "An existing file is removed and the function returns True."
    assert not p.exists(), "The file must be gone."
    assert remove_if_exists(str(p)) is False, "A missing file is not an error: return False. Use `with suppress(FileNotFoundError):`."


def test_remove_if_exists_other_errors_propagate(tmp_path):
    with pytest.raises(IsADirectoryError):
        remove_if_exists(str(tmp_path))


def test_to_int_or():
    assert to_int_or("42") == 42 and to_int_or(" 7 ") == 7, "Valid text converts."
    assert to_int_or("x") is None, "Invalid text gives the default, None if none is given."
    assert to_int_or("x", 0) == 0 and to_int_or("3.5", -1) == -1, "The default comes from the second argument."
    assert to_int_or(None, 9) == 9, "int(None) raises TypeError: suppress it as well."
    assert to_int_or(3.9) == 3, "int(3.9) is 3: a number is converted."


def test_to_int_or_does_not_hide_other_errors():
    class Weird:
        def __int__(self):
            raise ZeroDivisionError("bug")

    with pytest.raises(ZeroDivisionError):
        to_int_or(Weird())
