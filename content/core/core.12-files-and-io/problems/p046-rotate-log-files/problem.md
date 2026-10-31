# Rotate log files

A log file must not grow for ever. Programs **rotate** it: `app.log` becomes `app.log.1`, the old `app.log.1`
becomes `app.log.2`, and so on. The oldest file is deleted.

Write two functions in `solution.py`.

**`rotate_logs(path, keep=3)`**

- Keep at most `keep` old files: `path.1` (newest old file) up to `path.<keep>` (oldest).
- The oldest one, `path.<keep>`, is deleted if it exists.
- Every other `path.i` moves to `path.<i+1>`. Then `path` itself moves to `path.1`.
- Files that do not exist are skipped. A gap (for example no `.2`) is fine.
- After the call, `path` itself does **not** exist. If `path` does not exist, only the older files are shifted.
- Other files in the folder (for example `app.log.old`, `other.log`) must not be touched.
- `keep < 1` raises `ValueError`.

**`append_log(path, line, max_bytes=1000, keep=3)`**

- If adding `line + "\n"` would make the file bigger than `max_bytes`, call `rotate_logs` first.
  (A file that does not exist counts as 0 bytes. Use `len(text.encode("utf-8"))` for the size of the new text.)
- Then append `line + "\n"` to `path` (UTF-8).

**Example** (`keep=3`)

```text
before:  app.log   app.log.1   app.log.2   app.log.3
after:   app.log.1 (old app.log)   app.log.2 (old .1)   app.log.3 (old .2)     old .3 is gone
```
