# Checkpoint files: atomic save, safe load

A checkpoint is a small JSON file that says how far a run got, for example
`{"run_id": "r7", "cursor": "tok006x", "loaded": 6}`. It is only useful if it can be trusted
after a crash. `path.write_text(...)` is **not** safe: it first empties the file and then writes
the new text, so a crash (or a power cut, or Ctrl+C) in between leaves an empty or half-written
checkpoint, and the old one is gone.

The standard fix is the **atomic write**: write the new content to a temporary file in the
**same directory**, then `os.replace(temp, path)`. Replacing a file by renaming is atomic on
Windows, macOS and Linux: afterwards the path holds either the complete old file or the complete
new one, never a mix. (The same directory matters: a rename cannot move a file atomically to
another disk.)

Write two functions:

```python
def save_checkpoint(path, state: dict) -> None:
def load_checkpoint(path, default: dict | None = None) -> dict:
```

`path` may be a `str` or a `pathlib.Path`.

**`save_checkpoint`**

- Create the parent directories if they are missing.
- Write `state` as JSON (UTF-8) to a temporary file next to `path` (use
  `path.with_name(path.name + ".tmp")`), then move it into place with `os.replace(tmp, path)`
  (or `tmp.replace(path)`, which calls it). Write it as `import os` ... `os.replace(...)`: the
  tests simulate a crash at the worst moment by making `os.replace` fail.
- If `state` cannot be converted to JSON (`json` raises `TypeError`), let the error propagate;
  the old checkpoint must still be intact.
- After a successful save no `.tmp` file may be left over.

**`load_checkpoint`**

- If the file does not exist, return a **copy** of `default` (or `{}` when `default` is `None`).
- If the file exists and contains a JSON object, return it as a dict.
- If the file is **corrupt** (empty, truncated, not valid UTF-8, not valid JSON, or valid JSON
  that is not an object, such as `[1, 2]`): do not crash. Log one `WARNING` on the logger
  `"pipeline"` that names the file, move the bad file aside to `<name>.corrupt` (for example
  `cp.json.corrupt`, replacing an older one) so a human can inspect it, and return a copy of the
  default.
- Ignore any leftover `.tmp` file; only `path` itself counts.

Hint for the corrupt cases: `json.JSONDecodeError` and `UnicodeDecodeError` are both subclasses
of `ValueError`.

**Example**

```python
save_checkpoint(tmp / "state" / "cp.json", {"cursor": "tok003x", "loaded": 3})
load_checkpoint(tmp / "state" / "cp.json")              # {'cursor': 'tok003x', 'loaded': 3}
load_checkpoint(tmp / "missing.json", {"cursor": None}) # {'cursor': None}

(tmp / "bad.json").write_text('{"cursor": "tok0', encoding="utf-8")   # truncated by a crash
load_checkpoint(tmp / "bad.json", {"cursor": None})
# {'cursor': None}   WARNING logged, file renamed to bad.json.corrupt
```
