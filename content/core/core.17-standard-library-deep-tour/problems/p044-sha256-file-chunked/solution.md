## Approach

A hash object keeps a running state. `h.update(a); h.update(b)` gives the same digest as
`h.update(a + b)`, so we can read a file a piece at a time and memory use stays at one chunk.
`f.read(n)` returns at most `n` bytes and returns `b""` only at the end of the file, so that is the
stop condition. Files are opened in binary mode: a hash is about **bytes**, and text mode would
decode them and translate line endings.

## Code

```python
import hashlib


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_stream(f, chunk_size=65536):
    h = hashlib.sha256()
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        h.update(chunk)
    return h.hexdigest()


def sha256_file(path, chunk_size=65536):
    with open(path, "rb") as f:
        return sha256_stream(f, chunk_size)


def matches(path, expected_hex):
    return sha256_file(path) == expected_hex.strip().lower()
```

## Complexity

O(n) time for n bytes; O(chunk_size) memory, whatever the file size.

## Another way

Python 3.11+ has this loop built in: `hashlib.file_digest(f, "sha256").hexdigest()`. The loop can
also be written with the two-argument `iter`: `for chunk in iter(lambda: f.read(size), b""):`, which
calls the lambda until it returns the sentinel `b""`. When comparing digests that are **secrets**
(for example message signatures), use `hmac.compare_digest` so the comparison time does not leak how
many characters matched; for public file checksums `==` is fine.
