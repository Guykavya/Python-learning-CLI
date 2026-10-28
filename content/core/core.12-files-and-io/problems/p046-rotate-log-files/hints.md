## Hint 1

If you move `.1` to `.2` first, what happens to the old `.2`? In which order must you move the files so that nothing
is overwritten too early: from the oldest to the newest, or the other way round?

## Hint 2

```
delete path.<keep>        (missing_ok=True)
for i from keep-1 down to 1:
    if path.i exists: os.replace(path.i, path.<i+1>)
if path exists: os.replace(path, path.1)
```
For `append_log`: `size = path.stat().st_size if path.exists() else 0`, and compare `size + len(new bytes)` with `max_bytes`.
