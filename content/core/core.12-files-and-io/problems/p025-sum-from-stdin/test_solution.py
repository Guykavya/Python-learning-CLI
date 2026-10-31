import io
import sys

import pytest

from solution import total_from_stdin


def feed(monkeypatch, text):
    monkeypatch.setattr(sys, "stdin", io.StringIO(text))


def test_example(monkeypatch, capsys):
    feed(monkeypatch, "10\n 5\n\n-3\n")
    assert total_from_stdin() == 12, "10 + 5 - 3 is 12; the blank line is skipped."
    assert capsys.readouterr().out == "total: 12\n", "Print 'total: 12' to stdout."


def test_empty_input(monkeypatch, capsys):
    feed(monkeypatch, "")
    assert total_from_stdin() == 0, "No input gives 0."
    assert capsys.readouterr().out == "total: 0\n", "Still print the total line."


def test_spaces_only_lines(monkeypatch):
    feed(monkeypatch, "   \n7\n\t\n")
    assert total_from_stdin() == 7, "A line with only spaces counts as blank."


def test_last_line_without_newline(monkeypatch):
    feed(monkeypatch, "1\n2\n3")
    assert total_from_stdin() == 6, "The last line may have no newline."


def test_bad_line_raises(monkeypatch):
    feed(monkeypatch, "1\nabc\n")
    with pytest.raises(ValueError):
        total_from_stdin()


def test_reads_line_by_line(monkeypatch):
    class Lines:
        """Only offers iteration. read() would fail."""
        def __iter__(self):
            return iter(["1\n", "2\n"])

        def read(self, *a):
            raise AssertionError("Do not call sys.stdin.read(): loop over sys.stdin instead.")

        readlines = read

    monkeypatch.setattr(sys, "stdin", Lines())
    assert total_from_stdin() == 3, "Loop over sys.stdin line by line."
