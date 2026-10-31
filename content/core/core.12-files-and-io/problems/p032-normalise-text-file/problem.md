# Remove the BOM and fix line endings

Files from Windows tools often start with a **BOM** (the three bytes `EF BB BF`) and end every line with `\r\n`.
Old Mac files use only `\r`. Your tools want clean UTF-8 with `\n`.

Write `normalise_text_file(src, dst)` in `solution.py`:

- Read `src` as text with the encoding `"utf-8-sig"`. This removes a BOM if there is one, and works without one.
  In text mode, Python also turns `\r\n` and `\r` into `\n` when reading.
- Write `dst` as UTF-8 **without** a BOM, with every line ending exactly `\n`
  (use `newline="\n"` when opening for writing, so Windows does not change it again).
- Do not add a final newline that was not there, and do not change `src`.
- Return the number of lines of the text (`len(text.splitlines())`).

**Example**

```python
# src bytes:  b"\xef\xbb\xbfname\r\nZo\xc3\xab\r\nlast"
normalise_text_file(src, dst)    # returns 3
# dst bytes:  b"name\nZo\xc3\xab\nlast"
```
