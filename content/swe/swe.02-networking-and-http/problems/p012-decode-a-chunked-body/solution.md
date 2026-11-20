## Approach

```python
import re

_HEX = re.compile(rb"[0-9a-fA-F]+")


def decode_chunked(data):
    pos = 0
    body = []
    while True:
        end = data.find(b"\r\n", pos)
        if end == -1:
            raise ValueError("missing chunk size line")
        size_text = data[pos:end].split(b";", 1)[0].strip()
        if not _HEX.fullmatch(size_text):
            raise ValueError(f"chunk size is not hexadecimal: {size_text!r}")
        size = int(size_text, 16)
        pos = end + 2
        if size == 0:
            break
        chunk = data[pos:pos + size]
        if len(chunk) < size:
            raise ValueError("chunk cut short")
        pos += size
        if data[pos:pos + 2] != b"\r\n":
            raise ValueError("missing CRLF after chunk data")
        pos += 2
        body.append(chunk)
    trailers = {}
    while True:
        end = data.find(b"\r\n", pos)
        if end == -1:
            raise ValueError("unterminated trailers")
        line = data[pos:end]
        pos = end + 2
        if line == b"":
            break
        name, colon, value = line.decode("latin-1").partition(":")
        if not colon:
            raise ValueError("malformed trailer line")
        trailers[name.strip().lower()] = value.strip()
    return b"".join(body), trailers
```

The decoder never searches for a pattern inside the data: it reads a **size line** (found by the next `\r\n`), then takes exactly `size` bytes with a slice, then checks the two bytes after. A chunk may therefore contain `\r\n` or even `0\r\n\r\n` and still be decoded right. After the zero-size chunk the same "read a line" step reads trailers until the empty line.

Example: `4\r\nWiki\r\n5;note=x\r\npedia\r\n0\r\nX-Sum: 7\r\n\r\n`: chunk 1 is `Wiki`; chunk 2's size line is `5;note=x`, so size 5 and `pedia`; then `0`; the trailer `X-Sum: 7` becomes `{"x-sum": "7"}`; the empty line ends everything.

## Complexity

`O(len(data))`.

## Another way

Read from a file object (`makefile`) with `readline()` and `read(n)`: the same logic works on a stream, which is what real clients do, because they do not have all the data yet.

## Why it matters

Streaming responses, large downloads and server-sent data use chunked encoding. A client library hides it, but a proxy or a test double must decode it correctly.
