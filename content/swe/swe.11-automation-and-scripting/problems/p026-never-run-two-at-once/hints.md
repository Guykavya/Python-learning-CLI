## Hint 1

A `@contextmanager` function runs until `yield`, gives control to the `with` body, and continues after `yield` when the body ends. Where must the clean-up go so it also runs when the body raises? Why is "check if the file exists, then create it" (two steps) not good enough, while `O_CREAT | O_EXCL` (one step) is?

## Hint 2

```text
is_alive = is_alive or pid_alive
try: fd = os.open(path, O_CREAT | O_EXCL | O_WRONLY)
except FileExistsError:
    try: pid = int(read the file .strip())  except ValueError: pid = None
    if pid is not None and is_alive(pid): raise AlreadyRunning(f"already running as process {pid}")
    os.unlink(path)                                   # stale
    fd = os.open(path, O_CREAT | O_EXCL | O_WRONLY)
try:
    os.write(fd, str(os.getpid()).encode()); os.close(fd)
    yield
finally:
    try: os.unlink(path)  except FileNotFoundError: pass
```
