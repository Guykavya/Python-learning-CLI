# Never run two at once

Chapter section 12.4 (never run two at once). If a job takes longer than its interval, or you start it by hand while cron starts it too, two copies run together and fight over the same files. A **single-instance lock** prevents that: the first copy creates a lock file *exclusively* and writes its process id (pid) in it; a second copy finds the file and stops. If the first copy crashed and left the file behind, the pid inside belongs to no living process, and the next run may take the lock over.

## What to write

The starter gives `AlreadyRunning` and `pid_alive(pid)` (it asks the operating system whether a process exists; it works on Linux, macOS and Windows). Write the context manager:

```python
@contextmanager
def single_instance(lock_path, is_alive=None): ...
```

- `is_alive` is a function `pid -> bool`; when it is `None`, use `pid_alive`. (The tests pass their own, so they can pretend a process is alive or dead.)
- Create the lock with `os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)`: the operating system guarantees that only one process can create the file; for everyone else it raises `FileExistsError`. Write `str(os.getpid())` into it and close it.
- If the file exists: read the pid (an integer; anything else, such as an empty or garbled file, counts as "no pid"). If there is a pid and `is_alive(pid)` is true, raise `AlreadyRunning(f"already running as process {pid}")` **without touching the file** (it belongs to the other copy). Otherwise the lock is stale: delete it and create it again exclusively.
- On leaving the `with` block, **always** delete the lock file, also when the body raised an exception (which must still propagate). A lock that is already gone is not an error.

## Example

```python
with single_instance("job.lock"):
    # job.lock contains our pid
    with single_instance("job.lock"):        # AlreadyRunning: already running as process 120615
        ...
# job.lock is gone

Path("job.lock").write_text("99999999")       # a crashed run left this behind
with single_instance("job.lock"):            # stale: taken over
    ...
```

Besides the tests with a fake `is_alive`, one test starts a real second Python process that holds the lock, so keep the default `pid_alive`.
