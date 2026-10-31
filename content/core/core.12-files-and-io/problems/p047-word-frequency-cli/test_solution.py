import io
import sys

import pytest

from solution import main


def feed(monkeypatch, text):
    monkeypatch.setattr(sys, "stdin", io.StringIO(text))


def test_example_from_stdin(monkeypatch, capsys):
    feed(monkeypatch, "The cat and the hat.\nThe end")
    assert main(["-n", "2"]) == 0, "A normal run returns 0."
    assert capsys.readouterr().out == "the 3\nand 1\n", "Highest count first, equal counts in A to Z order ('and' before 'cat'). Punctuation is not part of a word."


def test_default_top_ten(monkeypatch, capsys):
    feed(monkeypatch, " ".join(f"word{chr(97 + i)}" for i in range(15)) + "\n")
    main([])
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 10, "The default for -n is 10."
    assert lines[0] == "worda 1", "With equal counts the words are sorted A to Z."


def test_case_and_apostrophes(monkeypatch, capsys):
    feed(monkeypatch, "Don't STOP, stop; DON'T go!\n")
    main([])
    assert capsys.readouterr().out == "don't 2\nstop 2\ngo 1\n", "Lower-case everything. Keep the apostrophe inside a word. Commas and ; and ! separate words."


def test_digits_separate_words(monkeypatch, capsys):
    feed(monkeypatch, "abc123abc 42 abc\n")
    main([])
    assert capsys.readouterr().out == "abc 3\n", "Only letters and apostrophes belong to words. Digits separate them."


def test_min_option(monkeypatch, capsys):
    feed(monkeypatch, "a a a b b c\n")
    main(["--min", "2"])
    assert capsys.readouterr().out == "a 3\nb 2\n", "--min 2 hides words that occur only once."


def test_files_are_counted_together(tmp_path, capsys):
    one = tmp_path / "one.txt"
    two = tmp_path / "two.txt"
    one.write_text("red green red\n", encoding="utf-8")
    two.write_text("green blue green\n", encoding="utf-8")
    assert main([str(one), str(two)]) == 0, "Reading files must work and return 0."
    assert capsys.readouterr().out == "green 3\nred 2\nblue 1\n", "Counts of all files are added together."


def test_dash_means_stdin(tmp_path, monkeypatch, capsys):
    one = tmp_path / "one.txt"
    one.write_text("x y\n", encoding="utf-8")
    feed(monkeypatch, "y z\n")
    main([str(one), "-"])
    assert capsys.readouterr().out == "y 2\nx 1\nz 1\n", "A '-' in the file list means stdin."


def test_missing_file(tmp_path, capsys):
    code = main([str(tmp_path / "nope.txt")])
    shown = capsys.readouterr()
    assert code == 2, "A file that cannot be read gives exit code 2."
    assert shown.out == "", "Print nothing to stdout when a file is missing."
    assert "error: cannot read" in shown.err and "nope.txt" in shown.err, "Print 'error: cannot read <path>' to stderr."


def test_no_words(monkeypatch, capsys):
    feed(monkeypatch, "123 456 !!!\n")
    code = main([])
    shown = capsys.readouterr()
    assert code == 1, "No words at all gives exit code 1."
    assert shown.out == "" and "no words" in shown.err, "Print 'no words' to stderr."


@pytest.mark.parametrize("bad", [["-n", "abc"], ["-n", "0"], ["-n", "-3"], ["--min", "x"]])
def test_bad_options_exit_2(bad, monkeypatch):
    feed(monkeypatch, "a b\n")
    with pytest.raises(SystemExit) as info:
        main(bad)
    assert info.value.code == 2, "A bad option value makes argparse exit with code 2. Use type=int, and parser.error for -n below 1."


def test_big_input_streams(monkeypatch, capsys):
    class Lines(io.StringIO):
        def read(self, *args):
            raise AssertionError("Do not call stdin.read(). Loop over sys.stdin line by line.")

        def readlines(self, *args):
            raise AssertionError("Do not call stdin.readlines(). Loop over sys.stdin line by line.")

    feed_text = "".join("alpha beta alpha\n" for _ in range(20000))
    monkeypatch.setattr(sys, "stdin", Lines(feed_text))
    assert main(["-n", "1"]) == 0, "The run must succeed."
    assert capsys.readouterr().out == "alpha 40000\n", "20000 lines with alpha twice each."
