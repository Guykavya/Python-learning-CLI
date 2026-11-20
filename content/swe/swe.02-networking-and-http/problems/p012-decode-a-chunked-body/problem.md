# Decode a chunked body

When a server does not know the length of the body in advance, it sends it in **chunks** (`Transfer-Encoding: chunked`, chapter section 8.4). The body looks like this (spaces added for reading; the real separators are `\r\n`):

```text
4\r\n
Wiki\r\n
5\r\n
pedia\r\n
0\r\n
\r\n
```

Each chunk is: its size in **hexadecimal**, optional **extensions** after a `;`, `\r\n`, exactly that many bytes of data, `\r\n`. A chunk of size `0` ends the body. After it come optional **trailer** header lines (`Name: value\r\n`) and a final empty line `\r\n`.

Write `decode_chunked(data)` returning `(body, trailers)`:

- `body` is the concatenation of all chunk data (bytes);
- `trailers` is a dict with **lower-case** names and stripped values (`{}` if there are none).

Raise `ValueError` for: a size that is not hexadecimal (`zz`, `0x4`, `-1`, `+4`, empty), a chunk shorter than its size, missing `\r\n` after a chunk's data, missing end (no `0` chunk, or the final blank line is missing), a trailer line without a colon. Data may contain `\r\n` inside chunks: the **size** decides where a chunk ends, not a search.

## Example

```python
decode_chunked(b"4\r\nWiki\r\n5;note=x\r\npedia\r\n0\r\nX-Sum: 7\r\n\r\n")
# (b"Wikipedia", {"x-sum": "7"})
```
