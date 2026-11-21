## Approach

The three bugs and their fixes:

| Bug | What goes wrong | Fix |
|---|---|---|
| The pointer is switched first and the release is written in place | a crash or an error while writing leaves `current` naming a half-written (or missing) release | build in `.<version>.tmp`, publish with `os.replace`, switch the pointer **after** |
| `shutil.rmtree(releases / previous)` | the version you would roll back to is gone before you know the new one works | never delete the previous release in `deploy` (prune old ones later, by age, keeping the live one: problem p025) |
| the result of the health check is only returned | after a failed check the pointer still names the broken release, so users keep getting it | on failure restore the pointer to `previous` (or remove it when there was none), and treat an exception as a failure |

```python
def deploy(root, version, files, health_check):
    ...
    _write_pointer(root, version)
    try:
        healthy = bool(health_check(target))
    except Exception:
        healthy = False
    if healthy:
        return True
    if previous is not None:
        _write_pointer(root, previous)
    else:
        (root / "current").unlink()
    return False
```

Chapter 12.3 says it in one sentence: a good deployment **records what is running now**, starts the new version, **waits until it is healthy**, verifies it, and **goes back by itself** if anything fails. The chapter's script captured the failed container's logs before the rollback removed them; here the failed folder simply stays.

## Complexity

O(files written). A rollback is one `os.replace` of a tiny file, however large the release is.

## Another way

Keep the "switch before check" order only if the check needs the live pointer (a real health check hits the running service). If the check can run against the release folder alone, run it **before** switching: then a bad release never becomes live at all. Blue/green deployments (chapter 12.2) do exactly that: start the new version beside the old one, check it, then flip.
