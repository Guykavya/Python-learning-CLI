# Write tests: save and load notes with tmp_path

Code that touches files is tested with pytest's built-in **`tmp_path`** fixture: a brand-new
empty folder (a `pathlib.Path`) for each test, deleted for you later. Your tests never touch
real files and never leave anything behind.

The code under test:

```python
def save_notes(path, notes):
    """Write one note per line, replacing the file. Every line ends with a newline."""
    with open(path, "w", encoding="utf-8") as f:
        for note in notes:
            f.write(note + "\n")


def load_notes(path):
    """Return the notes as a list of strings. Blank lines are skipped, a missing file gives []."""
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return []
    return [line for line in lines if line.strip()]
```

In `solution.py` write tests (import with `from target import save_notes, load_notes`) that

- **pass** on the code above,
- **fail** on each of seven buggy versions the checker tries (it names the surviving bug),
- take `tmp_path` as a parameter in **at least four** tests, and
- contain at least five test functions.

Save the code above as `target.py` next to your `solution.py` and run
`python -m pytest solution.py` to try your tests. Give every `assert` a message.

**Example of one test**

```python
def test_round_trip(tmp_path):
    path = tmp_path / "notes.txt"
    save_notes(path, ["buy milk", "call Ana"])
    assert load_notes(path) == ["buy milk", "call Ana"], "What you save must load back unchanged."
```
