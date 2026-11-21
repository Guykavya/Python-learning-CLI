## Approach

```python
@contextmanager
def single_instance(lock_path, is_alive=None):
    is_alive = is_alive or pid_alive
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    try:
        fd = os.open(lock_path, flags)                       # fails if the file exists
    except FileExistsError:
        try:
            pid = int(Path(lock_path).read_text(encoding="utf-8").strip())
        except ValueError:
            pid = None
        if pid is not None and is_alive(pid):
            raise AlreadyRunning(f"already running as process {pid}")
        os.unlink(lock_path)                                 # stale lock from a crashed run
        fd = os.open(lock_path, flags)
    try:
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        yield
    finally:
        try:
            os.unlink(lock_path)
        except FileNotFoundError:
            pass
```

`O_EXCL` makes "create if it does not exist" **one** atomic step in the operating system, so two copies starting in the same millisecond cannot both win (a separate `exists()` check could let both through). The pid turns a crash into a recoverable situation: a lock whose owner is dead is stale and can be taken. The `try/finally` around `yield` removes the lock even when the job raises, and `AlreadyRunning` is raised **before** that `try`, so a refused second copy never deletes the first copy's lock. Injecting `is_alive` keeps the tests independent of real process ids (the chapter uses `psutil.pid_exists`, which needs a package).

## Complexity

O(1): a few system calls.

## Another way

On Linux and macOS, `flock -n /tmp/job.lock python job.py` does the same from the crontab line, and the operating system releases the lock automatically when the process dies, so there are no stale locks at all. In Python, `fcntl.flock` (POSIX) or the `portalocker` package give the same kind of lock. A rare race remains in the pid version: two processes taking over the **same** stale lock at the same instant; the second `os.open` with `O_EXCL` then fails with `FileExistsError` for one of them, which is the safe outcome.
