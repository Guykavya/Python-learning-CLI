# Where does each file go?

Chapter section 3 (`tidylib.py`). Two small functions decide where `tidy` puts a file, and one of them carries a safety rule: **never overwrite**.

## What to write

```python
def category_for(path) -> str: ...
def unique_destination(dst: Path) -> Path: ...
```

- `category_for(path)` looks up the file's **suffix** (the last one, so `a.tar.gz` is `.gz`) in the `CATEGORIES` table of the starter, **ignoring case** (`holiday.JPG` is an image). Anything not in the table, including a name with no suffix, is `"other"`. `path` may be a `str` or a `Path`.
- `unique_destination(dst)` returns `dst` itself if nothing exists there. Otherwise it tries `stem (1)suffix`, `stem (2)suffix`, ... in the same folder and returns the first name that does **not** exist. A folder with that name counts as "exists" too. It never creates anything.

## Example

```python
category_for("holiday.JPG")        # 'images'
category_for("backup.tar.gz")      # 'archives'   (suffix .gz)
category_for("README")             # 'other'
# documents/ already holds a.txt and "a (1).txt":
unique_destination(Path("documents/a.txt"))     # Path('documents/a (2).txt')
unique_destination(Path("documents/README"))    # Path('documents/README') if free, else 'README (1)'
```
