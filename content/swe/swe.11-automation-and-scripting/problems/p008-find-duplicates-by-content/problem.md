# Find duplicates by content

Chapter section 3 (`sha256_of` and `find_duplicates` in `tidylib.py`). Two files are duplicates when their **bytes** are equal, whatever their names. Hashing every file is slow on a big folder, so do the cheap check first: files of different **sizes** can never be equal, so only files that share a size are hashed.

## What to write

```python
def sha256_of(path, chunk=1024 * 1024) -> str: ...
def find_duplicates(root, min_size=1) -> list[list[Path]]: ...
```

- `sha256_of` returns the hex SHA-256 of the file, reading it in blocks of `chunk` bytes (so a 10 GB video never sits in memory at once).
- `find_duplicates`:
  - looks at every regular file under `root`, **recursively**, and skips symbolic links;
  - ignores files smaller than `min_size` bytes (the default `1` ignores empty files: every empty file "equals" every other, which is rarely useful);
  - groups files by size first, and calls **`sha256_of`** only for files whose size is shared by at least one other file (the tests count the calls, so call the module function `sha256_of`, not `hashlib` directly);
  - returns the groups of 2 or more files with identical content; each group sorted, and the list of groups sorted, so the answer is stable.

## Example

```text
root/
  notes.txt        "my notes"
  copy/notes.bak   "my notes"
  other.txt        "my nodes"     (same size, different bytes)
  big.bin          "something longer"
  empty1, empty2   (0 bytes)
```

```python
find_duplicates(root)               # [[root/'copy/notes.bak', root/'notes.txt']]
find_duplicates(root, min_size=0)   # also [root/'empty1', root/'empty2']
```
