## Hint 1

Which five things can go wrong with a save/load pair? What you save is not what you load,
the second save keeps old data, the file does not exist, the file has blank lines, the notes
carry `\n`. One test for each.

## Hint 2

Some bugs cannot be seen through `load_notes` alone (the saved text lacks a final newline but
loads fine). How else can a test look at what `save_notes` wrote? `path.read_text()`.

```
def test_...(tmp_path):
    path = tmp_path / "notes.txt"
    save_notes(path, [...])
    assert path.read_text() == "a\nb\n"     # look at the raw file
    assert load_notes(path) == [...]          # or at the loaded list
```
