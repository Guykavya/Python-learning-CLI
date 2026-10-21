## Approach

`rpartition(".")` cuts at the last dot and always returns three strings:

| Input | head | dot | tail |
|---|---|---|---|
| `archive.tar.GZ` | `archive.tar` | `.` | `GZ` |
| `README` | (empty) | (empty) | `README` |
| `draft.` | `draft` | `.` | (empty) |

- Name: `head`, but when `head` is empty (no dot) use `tail`. That is `head or tail`.
- Extension: `tail`, but only if there was a dot. `dot and tail` gives `""` when there was no dot. Then `or "(none)"` handles every empty case.

## Code

```python
name = input()
head, dot, tail = name.rpartition(".")
print(f"Name: {head or tail}")
print(f"Extension: {(dot and tail).lower() or '(none)'}")
```

## Another way

`os.path.splitext(name)` from the standard library does this job in real code. It also knows that `.bashrc` is a hidden file with no extension, which is why this task excluded names starting with a dot. Once you know `if` (core.07), the logic can be written more plainly.
