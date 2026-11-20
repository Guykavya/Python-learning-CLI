# A line reader that keeps the leftovers

A protocol with **lines** (chapter section 6.5) receives bytes in pieces that can cut a line anywhere. Write a class

```python
class LineReader:
    def feed(self, chunk: bytes) -> list[str]: ...
```

- `feed` takes the next chunk of bytes and returns the **complete lines** found so far, as `str` (UTF-8), **without** the line ending.
- A line ends with `\n` or `\r\n`; the `\r` is removed too. An empty line is returned as `""`.
- Bytes after the last newline are **kept** inside the reader and are part of the next line when the next chunk arrives.
- A multi-byte character may be split between two chunks: it must come out right.
- If more than **65 536 bytes** are waiting without a newline, `feed` raises `ValueError` (otherwise a peer that never sends a newline fills your memory).
- `feed(b"")` returns `[]`.

## Example

```python
r = LineReader()
r.feed(b"hel")                 # []
r.feed(b"lo\r\nwor")           # ["hello"]
r.feed(b"ld\n\nx\n")           # ["world", "", "x"]
```
