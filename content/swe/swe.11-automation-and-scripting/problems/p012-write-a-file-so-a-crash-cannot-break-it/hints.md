## Hint 1

`tempfile.mkstemp` returns two things: an OS-level file descriptor and the temp path. How do you turn the descriptor into a normal Python file object with an encoding? (`os.fdopen`.) Which statement lets you clean up on *any* failure and still let the error travel on?

## Hint 2

```text
path = Path(path)
fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)
except BaseException:
    Path(tmp).unlink(missing_ok=True)
    raise
```
