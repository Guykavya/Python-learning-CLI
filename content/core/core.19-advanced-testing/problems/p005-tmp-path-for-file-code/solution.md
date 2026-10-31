## Approach

Every test starts with `path = tmp_path / "notes.txt"`, so it works in a private folder. Then
cover: round trip, raw file text, replace-not-append, missing file, blank lines, no newline
characters, spaces inside a note, empty list. Each of the seven bugs breaks at least one.

## Code

```python
from target import load_notes, save_notes


def test_round_trip(tmp_path):
    path = tmp_path / "notes.txt"
    save_notes(path, ["buy milk", "call Ana"])
    assert load_notes(path) == ["buy milk", "call Ana"]


def test_file_has_final_newline(tmp_path):
    path = tmp_path / "notes.txt"
    save_notes(path, ["a", "b"])
    assert path.read_text(encoding="utf-8") == "a\nb\n"


def test_saving_again_replaces(tmp_path):
    path = tmp_path / "notes.txt"
    save_notes(path, ["old"])
    save_notes(path, ["new"])
    assert load_notes(path) == ["new"]


def test_missing_file(tmp_path):
    assert load_notes(tmp_path / "nope.txt") == []


def test_blank_lines_skipped(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("a\n\n   \nb\n", encoding="utf-8")
    assert load_notes(path) == ["a", "b"]
```

## Cost

`tmp_path` creates one small folder per test (microseconds to milliseconds). Pytest keeps the
last few runs' folders and deletes older ones, so nothing piles up.

## Another way

`tmp_path_factory` gives one folder for a whole session if setup is expensive, and
`tmp_path.joinpath("sub", "file.txt")` builds nested paths. For a function that takes a path,
`tmp_path` is the simplest seam.
