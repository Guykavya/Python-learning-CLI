# Zip a folder, list it, extract it safely

`zipfile.ZipFile` reads and writes `.zip` archives. Three details matter in real code:

- **Member names.** `zf.write(path, arcname=...)` stores the file under `arcname`. Without it, the
  name is built from `path` itself, so you may get `home/you/tmp/...` inside the archive. Inside a zip,
  folders are always separated by `/`, on every operating system.
- **Compression.** The default is `ZIP_STORED` (no compression at all). Pass
  `compression=zipfile.ZIP_DEFLATED` to really compress.
- **Zip slip.** A zip made by someone else can contain a member named `../../evil.txt` or
  `/etc/evil`. Extracting it blindly would write *outside* the target folder. Check every name first.

Write four functions in `solution.py`:

1. `zip_folder(src, dest_zip) -> list[str]`: put every file under `src` (all sub-folders) into a new
   archive `dest_zip` with `ZIP_DEFLATED`. Each member name is the path relative to `src` with `/`
   separators (`"docs/a.txt"`). Only files are added (no folder entries). If `dest_zip` is itself
   inside `src`, do not add it to itself. Return the sorted member names.
2. `list_zip(zip_path) -> list[str]`: the sorted names of the **files** in an archive (skip names
   that end in `/`, which are folder entries).
3. `read_member(zip_path, name) -> bytes`: the content of one member. A missing name raises
   `KeyError` (that is what `ZipFile.read` does).
4. `safe_extract(zip_path, dest) -> list[str]`: extract all members into `dest` and return the sorted
   file names. But **first** check every name; if any name is unsafe, raise `ValueError` and extract
   **nothing**. A name is unsafe if it starts with `/` or `\`, contains `\`, has a drive like `C:` in
   its first part, or has a `..` part.

**Example**

```text
project/
    readme.md
    src/main.py
    src/util/helpers.py
```

```python
zip_folder("project", "out/project.zip")
# ['readme.md', 'src/main.py', 'src/util/helpers.py']

list_zip("out/project.zip")                  # the same list
read_member("out/project.zip", "src/main.py")    # b'print("hi")\n'

# a downloaded archive with a member named '../evil.txt'
safe_extract("evil.zip", "target")           # ValueError, and nothing is written
```
