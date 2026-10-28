# A checksum of a file in chunks

A checksum (hash) tells you whether two files are the same. A video can be 4 GB, so you must not read it with
one `read()`. Read it in **chunks** and feed each chunk to the hash object: `h.update(chunk)`.

Write `file_sha256(path, chunk_size=65536)` in `solution.py`:

- Open the file in **binary** mode (`"rb"`).
- Read it with `f.read(chunk_size)` again and again, until `read` returns `b""`.
  Use the two-argument form `iter(callable, sentinel)`: `iter(lambda: f.read(chunk_size), b"")`.
- Return the hex digest (a string of 64 characters) of `hashlib.sha256`.
- The result must be the same as `hashlib.sha256(whole_file_bytes).hexdigest()`.
- Never read more than `chunk_size` bytes at once.

**Example**

```python
file_sha256("hello.txt")   # file with the bytes b"abc"
# 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
```
