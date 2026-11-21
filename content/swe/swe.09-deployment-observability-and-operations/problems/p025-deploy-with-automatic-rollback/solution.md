## Approach

The full code is `reference.py`. The three decisions that matter:

```python
def _write_pointer(root, version):
    pointer = Path(root) / "current"
    tmp = pointer.with_name("current.tmp")
    tmp.write_text(version + "\n", encoding="utf-8")
    os.replace(tmp, pointer)             # atomic: a reader sees the old pointer or the new one

# in deploy():
tmp = releases / f".{version}.tmp"       # build the release out of sight ...
...
os.replace(tmp, final)                   # ... and make it appear complete, or not at all

try:
    healthy = bool(health_check(final))
except Exception as exc:
    healthy, error = False, f"{type(exc).__name__}: {exc}"
if healthy: ...
elif previous is not None:
    _write_pointer(root, previous)       # roll back by pointing at the old release again
else:
    (root / "current").unlink()          # nothing good to point at
```

How this maps to the chapter's script and its "Try it: why did the rollback work?": (1) a **health check** that fails for a broken release (here the injected function); (2) **immutable, versioned releases**: the old folder still exists, so a rollback is "point at it again", never "rebuild"; (3) the script **records the previous version**; (4) **verification after the switch**; (5) **evidence is kept**: the failed folder stays. Pruning by deploy order, never deleting the live release, is the "keep the last several images, prune by age" habit of 12.5.

## Complexity

O(files written) per deploy; the switch and the rollback are one rename each, so a rollback takes the same time however large the release is.

## Another way

Symlinks (`current -> releases/1.1.0`, replaced with `ln -sfn` or `os.replace` of a new link) are the classic form of this pattern on Linux servers; a pointer file is used here because creating symlinks needs extra privileges on Windows. With Docker the "pointer" is the image tag in the Compose file and the "release folder" is the image in the registry.
