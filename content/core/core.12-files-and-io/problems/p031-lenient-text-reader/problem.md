# Read text with bad bytes

Real files are messy. A file may have a few bytes that are not valid UTF-8, for example one old line saved in
Latin-1. With the default `errors="strict"`, `open(...).read()` raises `UnicodeDecodeError` and you get nothing.
With `errors="replace"` every bad byte becomes the character `"\ufffd"` (the replacement character) and you get the rest.

Write `read_text_lenient(path)` in `solution.py`:

- First try to read the whole file as strict UTF-8.
- If that raises `UnicodeDecodeError`, read it again with `errors="replace"`.
- Return a tuple `(text, had_errors)`. `had_errors` is `True` only when the replace fallback was needed.
- A missing file must still raise `FileNotFoundError`.

**Example**

```python
# the file has the bytes  b"caf\xe9 ok"   (\xe9 is Latin-1 for e with an accent, not valid UTF-8)
read_text_lenient(path)    # ("caf\ufffd ok", True)
# the file has the bytes  b"caf\xc3\xa9"    (valid UTF-8)
read_text_lenient(path)    # ("caf\u00e9", False)
```
