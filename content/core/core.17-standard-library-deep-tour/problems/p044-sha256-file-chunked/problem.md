# SHA-256 of a file, read in chunks

A **hash** like SHA-256 turns any amount of bytes into a fixed 32-byte fingerprint. The same bytes
always give the same fingerprint; changing one bit changes it completely. That is how download pages
let you check a file, and how backup tools notice that a file changed.

A hash object can be fed **piece by piece** with `.update(chunk)`. The result is the same as hashing
everything at once, but you never hold a 4 GB video in memory.

Write four functions in `solution.py`:

1. `sha256_text(text) -> str`: the hex digest of the text encoded as UTF-8.
2. `sha256_stream(f, chunk_size=65536) -> str`: `f` is a file object opened in **binary** mode. Read it
   with `f.read(chunk_size)` until it returns `b""`, feeding each chunk to the hash. Never call
   `f.read()` with no size (that reads everything at once).
3. `sha256_file(path, chunk_size=65536) -> str`: open the file in binary mode and use `sha256_stream`.
4. `matches(path, expected_hex) -> bool`: does the file's digest equal `expected_hex`? Ignore upper/lower
   case and spaces around `expected_hex` (people copy digests from web pages).

All digests are returned as 64 lowercase hex characters (`.hexdigest()`).

**Example**

```python
sha256_text("abc")
# 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'

sha256_text("")
# 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'

# a file containing the bytes b"abc"
sha256_file("abc.bin")                    # same as sha256_text("abc")
matches("abc.bin", "  BA7816BF8F01CFEA414140DE5DAE2223B00361A396177A9CB410FF61F20015AD\n")   # True
```
