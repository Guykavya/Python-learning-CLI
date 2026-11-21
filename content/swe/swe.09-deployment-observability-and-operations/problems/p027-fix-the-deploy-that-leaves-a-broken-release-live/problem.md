# Fix the deploy that leaves a broken release live

Chapter section 12.3 (a deployment script with automatic rollback), 12.5 (deployment hygiene: "roll back first, investigate second") and "Try it: why did the rollback work?". A teammate wrote a deploy function for the folder layout of problem p025 (`root/releases/<version>/` and a pointer file `root/current`). It works on the happy path. On the bad path it takes the site down: after a failed health check, **users keep getting the broken release**, and sometimes **there is no old release left to go back to**. The code of `solution.py` is the teammate's. Fix it.

```python
def deploy(root, version, files, health_check) -> bool:
    root = Path(root)
    releases = root / "releases"
    previous = current_version(root)

    (root / "current").write_text(version, encoding="utf-8")            # switch first...
    target = releases / version
    for rel, text in files.items():                                       # ...then write the release
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    if previous:                                                          # "save disk space"
        shutil.rmtree(releases / previous)

    return bool(health_check(target))                                     # and hope
```

## Your task

1. Find the **three** bugs. Name each one (a sentence in your head or in a comment) before you change the code.
2. Fix `deploy` so that:
   - the release is written into a temporary folder and **published with `os.replace`**, so `releases/<version>` is either complete or absent. If writing fails, remove the temporary folder, leave everything else as it was, and let the exception go;
   - the pointer is switched with a temporary file and `os.replace`, and **only after** the release exists;
   - the **previous release is never deleted** by `deploy`;
   - if `health_check(target)` returns a falsy value **or raises**, the pointer goes back to `previous` (or is removed when there was none) and `deploy` returns `False`; otherwise it returns `True`.

`current_version(root)` is given and must not change. The release folder of a failed deploy may stay.

## Example

```python
deploy(root, "1.0.0", {"app.txt": "v1"}, lambda d: True)    # True,  current -> 1.0.0
deploy(root, "2.0.0", {"app.txt": "v2"}, lambda d: False)   # False, current -> 1.0.0, releases/1.0.0/app.txt still "v1"
```
