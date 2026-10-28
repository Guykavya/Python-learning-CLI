# Find duplicate files: size first, then hash

Your Downloads folder has the same PDF three times under different names. To find such copies, compare
**content**, not names. Hashing every file works but is slow for big folders. A cheap trick makes it
fast: two files can only be identical if they have the **same size**, and the size is known without
reading the file. So:

1. group all files by size (free);
2. hash only the files that share their size with another file;
3. files with the same hash are duplicates.

Write three functions in `solution.py`:

1. `file_hash(path) -> str`: the SHA-256 hex digest of the file, read in chunks.
2. `find_duplicates(root) -> list[list[str]]`: every group of two or more files under `root` (in all
   sub-folders) with identical content.
   - Paths are relative to `root` with forward slashes (`"docs/a.pdf"`).
   - Each group is sorted; the list of groups is sorted (by first path).
   - **Empty files are ignored** (they are all "equal" but are not interesting).
   - Call `file_hash` (by that name) for hashing, and **only** for files whose size is shared with at
     least one other file. The tests count the calls.
3. `wasted_bytes(root, groups) -> int`: how many bytes you would free by keeping only one file of each
   group: for each group, `size * (len(group) - 1)`.

**Example**

```text
root/
    a.txt          "hello"      (5 bytes)
    b.txt          "hello"      (5 bytes)
    c.txt          "world"      (5 bytes, same size, different content)
    notes/a.txt    "hello"      (5 bytes)
    big.bin        1000 bytes   (unique size: never hashed)
```

```python
groups = find_duplicates("root")
# [['a.txt', 'b.txt', 'notes/a.txt']]      c.txt has the same size but another hash

wasted_bytes("root", groups)              # 10   (5 * (3 - 1))
```

Here `file_hash` is called 4 times (the four 5-byte files), not 5.
