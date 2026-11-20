# Resolve conflict markers

During a merge conflict git writes both versions into the file between **markers** (chapter section 6.3):

```text
PRICES = {
<<<<<<< HEAD
    "tea": 15,
=======
    "tea": 25,
>>>>>>> feature
    "coffee": 30,
}
```

Write `resolve(text, choose)` that returns the file text with **every block resolved and all marker lines removed**.

- `choose = "ours"` keeps the lines between `<<<<<<<` and `=======` (the branch you are on).
- `choose = "theirs"` keeps the lines between `=======` and `>>>>>>>`.
- `choose = "both"` keeps ours, then theirs.
- `choose` can also be a **function** `f(ours_lines, theirs_lines)` returning the list of lines to write; it is called once per block.
- Any other value of `choose` raises `ValueError`.

A file may contain several blocks. Lines outside the blocks stay as they are, including the final newline (or its absence). A file with no markers is returned unchanged; a `=======` line **outside** a block is ordinary text (Markdown and reStructuredText use it for headings).

A marker line is `<<<<<<<` or `>>>>>>>` followed by nothing or by a space and a label. The divider is exactly `=======`.

Broken files raise `ValueError`, and the message must contain `line N` with the 1-based number of the **offending** line:

- a `>>>>>>>` with no open block;
- a second `<<<<<<<` inside an open block;
- a block that is never closed (name the line where it began);
- `>>>>>>>` before `=======`, or a second `=======` inside one block.

## Example

```python
text = 'A = 1\n<<<<<<< HEAD\nB = 2\n=======\nB = 3\n>>>>>>> feature\nC = 4\n'
resolve(text, "ours")     # 'A = 1\nB = 2\nC = 4\n'
resolve(text, "theirs")   # 'A = 1\nB = 3\nC = 4\n'
resolve(text, "both")     # 'A = 1\nB = 2\nB = 3\nC = 4\n'
```
