# A counter shared between processes

Threads share memory: a global list changed by one thread is seen by all. **Processes do
not.** Each process has its own copy of every variable, so `global count; count += 1` in a
child process changes the child's copy only, and the parent never sees it.

`starter.py` tries anyway. It starts `n_procs` processes that each add `per_proc` to a module
global, and it returns `0` every time.

To really share a number, put it in **shared memory** with `multiprocessing.Value`:

```python
from multiprocessing import Value
counter = Value("i", 0)        # "i" = C int, starting at 0
counter.value                  # read it
with counter.get_lock():       # the lock that comes with the Value
    counter.value += 1         # read-modify-write: needs the lock, like p006
```

Write two **top-level** functions:

- `add_many(counter, times)`: add 1 to `counter.value`, `times` times, each time under
  `counter.get_lock()`. This runs inside the child processes.
- `count_in_processes(n_procs, per_proc)`: create a `Value("i", 0)`, start `n_procs`
  `multiprocessing.Process`es that each run `add_many(counter, per_proc)`, `join` them all, and
  return the final value.

**Example**

```python
if __name__ == "__main__":
    print(count_in_processes(4, 1000))
```

```text
4000
```

`counter.value += 1` **without** the lock loses updates: the processes really do run at the
same time on different cores, and the GIL does not help here at all, because each process has
its own GIL. On one test machine, 4 processes × 20,000 increments without the lock gave
numbers like `36897` and `40871` instead of `80000`, different on every run. (With only 1,000
increments each, every process may finish before the next one has even started, so the bug
hides. Small tests can lie.)
