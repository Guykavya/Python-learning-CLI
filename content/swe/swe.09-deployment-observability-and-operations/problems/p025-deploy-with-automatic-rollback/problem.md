# Deploy with automatic rollback

Chapter sections 12.1 to 12.3 (build, release, deploy; strategies; the deployment script with automatic rollback) and "Try it: why did the rollback work?". This is the second outcome of the module: **roll back a bad deployment.** The chapter's `deploy.sh` records the previous version, starts the new one, waits for health, verifies, and goes back by itself on failure. Docker is never run by the tests, so you write the same logic over **folders**: each release is a folder, and a one-line file says which one is live.

```text
root/
  releases/
    1.0.0/        (app files of version 1.0.0)
    1.1.0/
  current         a text file: "1.1.0"   <- what is live
  history.txt     one line per deployed version, oldest first
```

## What to write

```python
def current_version(root) -> str | None: ...
def deploy(root, version, files, health_check, keep=5) -> dict: ...
```

- `current_version(root)`: the text of `root/current` (stripped), or `None` if the file does not exist.
- `deploy(root, version, files, health_check, keep=5)`:
  - `version` must match `^[A-Za-z0-9][A-Za-z0-9._-]*$`; `files` maps **relative paths** (`"app/main.py"`) to text. A path that is absolute, empty, or has a `..` part is invalid. Raise `ValueError` for any invalid input **before writing anything**. If `releases/<version>` already exists, also raise `ValueError`: **releases are immutable**.
  - **Write the release** into a temporary folder `releases/.<version>.tmp` (UTF-8), then rename that folder to `releases/<version>` with `os.replace`: a release folder is either complete or absent. If writing fails, remove the temporary folder and let the exception go (nothing else may have changed).
  - Remember `previous = current_version(root)`. **Switch the pointer** atomically: write `current.tmp`, then `os.replace` it onto `current`. Append the version to `history.txt`.
  - **Run `health_check(release_dir)`** (a `pathlib.Path` of the new release) **after** the switch, the way the chapter's script checks the running service. Healthy means it returns a truthy value. If it returns a falsy value, **or raises an exception**, the deployment failed.
  - On success return `{"version": version, "status": "live", "live": version, "error": None}`.
  - On failure **switch back** (same atomic way) to `previous` and return `status: "rolled_back"` with `live: previous`. If there was **no** previous version, delete the `current` file and return `status: "failed"` with `live: None`. `error` is `"health check failed"` for a falsy result, or `"ExceptionName: message"` for an exception. **The failed release folder stays** for inspection (the chapter captures the evidence before cleaning up).
  - **Prune**: afterwards, if more than `keep` release folders exist, delete the **oldest** ones (by `history.txt` order) until `keep` remain, but **never the live one**.
  - A second failure in a row must still leave the last good version live.

## Example

```python
deploy(root, "1.0.0", {"app.txt": "v1"}, lambda d: True)
# {'version': '1.0.0', 'status': 'live', 'live': '1.0.0', 'error': None}
deploy(root, "2.0.0", {"app.txt": "v2"}, lambda d: False)
# {'version': '2.0.0', 'status': 'rolled_back', 'live': '1.0.0', 'error': 'health check failed'}
current_version(root)        # '1.0.0'
(root / "releases" / "2.0.0" / "app.txt").read_text()    # 'v2'   (kept for inspection)
```

Chapter 12.4 adds one more thing a rollback cannot undo: **the database**. A rollback of code is safe only if the new version's migrations were additive (problem p026).
