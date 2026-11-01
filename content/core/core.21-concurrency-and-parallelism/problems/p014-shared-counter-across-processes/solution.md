## Approach

A process has its own memory. With "spawn" or "forkserver" (the defaults on Windows/macOS and
on Linux in 3.14) the child starts as a new interpreter that imports your module, so module
globals start from their initial values. With "fork" the child gets a **copy** of the parent's
memory, and changes still stay in the copy. Either way, the parent's `count` stays 0.

`multiprocessing.Value("i", 0)` puts one C `int` in **shared memory** that every process can
map. Passing it in `args` when the process is created hands the child a handle to the same
memory. Now all processes really change the same number.

They also change it **at the same time**, on different cores. `counter.value += 1` is read,
add, write, so updates get lost exactly like in p006, only more often (true parallelism, and
each process has its own GIL). `Value` comes with a lock for this: `counter.get_lock()`.

The `Value` is created inside `count_in_processes`, so each call starts at 0, and it is passed
to the children when they start (shared objects must be handed over at creation time, through
`args`, not later through a queue or pipe).

## Code

```python
from multiprocessing import Process, Value


def add_many(counter, times):
    for _ in range(times):
        with counter.get_lock():
            counter.value += 1


def count_in_processes(n_procs, per_proc):
    counter = Value("i", 0)
    procs = [Process(target=add_many, args=(counter, per_proc)) for _ in range(n_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    return counter.value
```

## Complexity

O(n_procs × per_proc) increments, but they run **one at a time** because of the lock, and a
cross-process lock is far slower than a thread lock. On top of that, each process takes tens of
milliseconds to start. This program is slower than a plain loop; it exists to show how sharing
works.

## Another way

The better design is **not to share**: each process counts locally and **returns** its count,
and the parent adds them up:

```python
with ProcessPoolExecutor(n_procs) as pool:
    total = sum(pool.map(count_locally, [per_proc] * n_procs))
```

No lock, no shared memory, and each worker runs at full speed. Reach for `Value`, `Array` or a
`Manager` only when processes must see each other's changes **while** they run.
