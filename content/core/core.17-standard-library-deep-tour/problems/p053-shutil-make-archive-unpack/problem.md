# Archives the easy way: `shutil.make_archive` and `unpack_archive`

`shutil` can create and unpack whole archives in one call, in several formats:

```python
>>> shutil.make_archive("out/bk", "zip", root_dir="src")
'/home/you/.../out/bk.zip'                       # absolute path (machine-specific)
>>> shutil.make_archive("out/bk", "gztar", root_dir="src")
'/home/you/.../out/bk.tar.gz'
>>> shutil.get_archive_formats()
[('bztar', "bzip2'ed tar-file"), ('gztar', "gzip'ed tar-file"), ('tar', 'uncompressed tar file'),
 ('xztar', "xz'ed tar-file"), ('zip', 'ZIP file'), ('zstdtar', "zstd'ed tar-file")]   # Python 3.14
```

Things to know (all seen in real runs, for a folder `src` with `a.txt` and `sub/b.txt`):

- `base_name` is the name **without** extension; `make_archive` adds `.zip` or `.tar.gz` itself.
- `root_dir` is the folder whose **contents** go into the archive.
- The names stored are not the same in each format:
  - zip: `['sub/', 'a.txt', 'sub/b.txt']` (a folder entry `sub/`);
  - gztar: `['.', './a.txt', './sub', './sub/b.txt']` (everything starts with `./`, folders included).
- `shutil.unpack_archive(archive, dest)` guesses the format from the extension. For tar archives pass
  `filter="data"`: it refuses dangerous members (absolute paths, `..`, device files). The zip
  unpacker does **not** accept a `filter` argument, so pass it only for tar formats.

Write four functions in `solution.py`:

1. `archive_formats() -> list[str]`: the sorted names of the formats this Python can write
   (`"zip"`, `"gztar"`, ...).
2. `make_backup(src_dir, out_dir, name, fmt="zip") -> Path`: archive the contents of `src_dir` into
   `out_dir/name.<ext>` (create `out_dir` if needed) and return the archive's path as a `Path`.
   An unknown `fmt` raises `ValueError`.
3. `archive_members(archive) -> list[str]`: the sorted names of the **files** inside a zip or tar
   archive, normalised: no folder entries and no leading `./`. Use `zipfile.is_zipfile` /
   `tarfile.is_tarfile` to tell the type; anything else raises `ValueError`.
4. `restore(archive, dest) -> list[str]`: unpack into `dest` (with `filter="data"` for tar archives)
   and return the sorted relative paths (with `/`) of all files now under `dest`.

**Example**

```python
p = make_backup("src", "out", "bk", "gztar")     # Path('out/bk.tar.gz')
archive_members(p)                               # ['a.txt', 'sub/b.txt']
restore(p, "restored")                           # ['a.txt', 'sub/b.txt']
make_backup("src", "out", "bk", "rar")           # ValueError
```
