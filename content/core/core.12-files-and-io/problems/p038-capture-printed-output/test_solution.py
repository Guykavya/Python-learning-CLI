import sys

import pytest

from solution import capture_output


def hello(name, punct="!"):
    print("hi", name + punct)
    print("careful", file=sys.stderr)
    return 42


def test_example(capsys):
    assert capture_output(hello, "Ana") == (42, "hi Ana!\n", "careful\n"), "Return (result, stdout text, stderr text)."
    shown = capsys.readouterr()
    assert shown.out == "" and shown.err == "", "Nothing may reach the real screen while the output is captured."


def test_keyword_arguments():
    assert capture_output(hello, "Bo", punct="?") == (42, "hi Bo?\n", "careful\n"), "Pass *args and **kwargs on to func."


def test_function_without_output():
    assert capture_output(len, "abc") == (3, "", ""), "A quiet function gives two empty strings."


def test_several_prints_keep_order():
    def many():
        for i in range(3):
            print(i, end=" ")
        print()
    assert capture_output(many) == (None, "0 1 2 \n", ""), "All prints go into the same buffer, in order."


def test_streams_restored_after_success():
    before = (sys.stdout, sys.stderr)
    capture_output(hello, "x")
    assert (sys.stdout, sys.stderr) == before, "After the call sys.stdout and sys.stderr must be the old objects again."


def test_error_propagates_and_streams_restored():
    def boom():
        print("partial")
        raise ValueError("bad")
    before = (sys.stdout, sys.stderr)
    with pytest.raises(ValueError):
        capture_output(boom)
    assert (sys.stdout, sys.stderr) == before, "Use redirect_stdout / redirect_stderr in a with block, so the streams are restored even after an error."


def test_later_prints_are_visible(capsys):
    capture_output(hello, "q")
    print("after")
    assert capsys.readouterr().out == "after\n", "Prints after the call must reach the normal stdout."
