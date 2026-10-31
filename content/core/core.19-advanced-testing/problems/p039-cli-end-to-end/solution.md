## Approach

Most bugs are found by calling `main(argv)` directly: it is fast, needs no process, and `capsys` captures `out` and `err` separately.
Each test uses a tiny file where the right answer is obvious:

- `"the cat and the dog and the bird sat"`: counts 3, 2, then four words with count 1. It checks the default top 5 (the 6th word is
  cut), the alphabetical order among equal counts (`cat` was seen before `bird`), and the order of keys in JSON.
- `"Apple apple APPLE, pear. pear!"`: case and punctuation.
- `"a bb ccc dd"` with `--min-length 2`: the border of `>=`.
- a missing file: return value 2, nothing on standard output, the file name on standard error. Checking `out == ""` and
  `err` separately catches the message printed on the wrong stream.

`sys.exit(main())` is not run when you import the module, so no direct call can see it. One subprocess test covers it: with the correct
code the process exits with 2 for a missing file; with `main()` instead the exit code is always 0. Everything else stays in fast, direct
tests, and only one process is started, because starting processes is slow.

## Code

```python
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
```

## Cost

Seven fast tests and one subprocess (about 50 ms of interpreter start-up). The direct tests dominate in number; the subprocess test is the only one of its kind.

## Another way

`pytest.mark.parametrize` over `(text, argv, expected_lines)` rows would shorten the direct tests. Or use `runpy.run_path(wordstat.__file__, run_name="__main__")`
inside `pytest.raises(SystemExit)`: it runs the last lines in-process, without a new interpreter. A real subprocess is the most
honest end-to-end check, because it also covers the interpreter and the command line.
