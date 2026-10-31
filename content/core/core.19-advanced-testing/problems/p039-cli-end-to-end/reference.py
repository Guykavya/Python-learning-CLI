import json
import subprocess
import sys

import pytest

import wordstat

TEXT = "the cat and the dog and the bird sat"


@pytest.fixture
def textfile(tmp_path):
    path = tmp_path / "words.txt"
    path.write_text(TEXT)
    return path


def lines(capsys):
    return capsys.readouterr().out.splitlines()


def test_default_output_is_top_five(textfile, capsys):
    assert wordstat.main([str(textfile)]) == 0, "Success returns 0."
    assert lines(capsys) == ["the 3", "and 2", "bird 1", "cat 1", "dog 1"], (
        "Default --top is 5; equal counts are listed alphabetically.")


def test_top_option(textfile, capsys):
    assert wordstat.main([str(textfile), "--top", "2"]) == 0
    assert lines(capsys) == ["the 3", "and 2"], "--top 2 shows exactly two words."


def test_case_and_punctuation_are_ignored(tmp_path, capsys):
    path = tmp_path / "t.txt"
    path.write_text("Apple apple APPLE, pear. pear!")
    wordstat.main([str(path)])
    assert lines(capsys) == ["apple 3", "pear 2"], "Words are lower-cased and trimmed of . , ; : ! ?"


def test_min_length(tmp_path, capsys):
    path = tmp_path / "t.txt"
    path.write_text("a bb ccc dd")
    wordstat.main([str(path), "--min-length", "2"])
    assert lines(capsys) == ["bb 1", "ccc 1", "dd 1"], "--min-length 2 keeps words of 2 letters or more."


def test_json_output(textfile, capsys):
    assert wordstat.main([str(textfile), "--json", "--top", "3"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data == {"the": 3, "and": 2, "bird": 1}, "--json prints one JSON object {word: count}."
    assert list(data) == ["the", "and", "bird"], "The order of the object keys is the ranking."


def test_missing_file_returns_2_and_writes_to_stderr(tmp_path, capsys):
    code = wordstat.main([str(tmp_path / "nope.txt")])
    captured = capsys.readouterr()
    assert code == 2, "A missing file returns 2 (and must not raise)."
    assert captured.out == "", "Nothing may be printed to standard output on an error."
    assert "nope.txt" in captured.err, "The error message on standard error names the file."


def test_unknown_option_is_a_usage_error(textfile):
    with pytest.raises(SystemExit) as info:
        wordstat.main([str(textfile), "--bogus"])
    assert info.value.code == 2, "argparse exits with code 2 on a usage error."


def test_real_program_exit_codes(textfile, tmp_path):
    ok = subprocess.run([sys.executable, wordstat.__file__, str(textfile), "--top", "1"],
                        capture_output=True, text=True, timeout=30)
    assert ok.returncode == 0 and ok.stdout.strip() == "the 3", "The script prints the top word and exits 0."
    bad = subprocess.run([sys.executable, wordstat.__file__, str(tmp_path / "nope.txt")],
                         capture_output=True, text=True, timeout=30)
    assert bad.returncode == 2, "Run as a script, a missing file must give exit code 2."
    assert "nope.txt" in bad.stderr, "The message is on standard error."
