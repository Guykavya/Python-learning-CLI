## Approach

```python
MAX_LINE = 64 * 1024


class LineReader:
    def __init__(self):
        self.buffer = b""

    def feed(self, chunk):
        self.buffer += chunk
        lines = []
        while True:
            i = self.buffer.find(b"\n")
            if i == -1:
                break
            raw, self.buffer = self.buffer[:i], self.buffer[i + 1:]
            if raw.endswith(b"\r"):
                raw = raw[:-1]
            lines.append(raw.decode("utf-8"))
        if len(self.buffer) > MAX_LINE:
            raise ValueError("line too long")
        return lines
```

The reader works on **bytes** and decodes only complete lines: a character such as `é` is two bytes, and if the chunk boundary falls between them, decoding each chunk would raise `UnicodeDecodeError`. The leftover after the last newline stays in `self.buffer`. The length check is made on that leftover, after complete lines were taken out, so a long but properly terminated stream of lines is fine.

Example: `feed(b"hel")` finds no newline: buffer `hel`, returns `[]`. `feed(b"lo\r\nwor")`: buffer `hello\r\nwor`; the first newline ends `hello\r`; the `\r` is dropped; buffer `wor`.

## Complexity

`O(total bytes)` (each slice copies the buffer; for very large inputs use `bytearray` or an index).

## Another way

`sock.makefile("rb")` and `readline(limit)` do this for sockets. A reader you feed by hand is easy to test and works with any source (a file, a test list, an `asyncio` stream).

## Why it matters

Line protocols (SMTP, Redis in its old form, log streams, HTTP headers) all need exactly this: a buffer that survives between `recv` calls.
