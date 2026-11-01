**1. Why the lambda fails.** Worker processes have their own memory, so arguments and the
function itself are sent to them as bytes, with `pickle`. `pickle` does **not** send a
function's code: it sends its **module and qualified name** (`"__main__"`, `"double"`), and the
worker imports that module and looks the name up. A lambda's name is `<lambda>`, which cannot be
looked up, so pickling fails. The same goes for functions defined inside other functions and
classes defined inside functions. The worker function must be a **top-level `def`** in an
importable module.

**2. What must be picklable.** Everything that crosses the boundary: the function, every
argument, every **return value**, and any **exception** raised in the worker (it is sent back to
be re-raised). Also the `initializer` and `initargs` of a pool, and items put on a
`multiprocessing.Queue`. Locks, open files, sockets, database connections and generators are not
picklable; pass plain data (paths, ids, numbers, strings, lists, dicts) instead.

**3. The `__main__` guard.** With `spawn` and `forkserver` each child **imports your script**
(as `__mp_main__`) to find the function. Any top-level code runs again in the child. If the pool
creation is at top level, every child would try to create a pool too: an endless chain, which
Python stops with a `RuntimeError` about the bootstrapping phase. Put process-starting code under
`if __name__ == "__main__":` so it runs only in the parent.

**4. Start methods.** `spawn` starts a fresh interpreter and imports the script: slow but clean
and safe. It is the default on Windows and macOS. `fork` (Linux/macOS only) copies the parent
process as it is: fast, and the child sees the parent's globals, but it is dangerous when the
parent has **threads**: only the forking thread is copied, so a lock held by another thread at
that moment stays locked forever in the child (deadlocks in logging, for example). `forkserver`
starts one clean server process early and forks children from it, so children are cheap but
free of the parent's threads. It is the default on Linux since **Python 3.14** (it was `fork`
before). Choose one with `multiprocessing.set_start_method(...)` or `get_context(...)`.

**5. Cost.** A process needs a new interpreter (tens of MB of memory, tens to hundreds of
milliseconds to start with spawn), and every call pays to pickle the input, copy it to another
process, and pickle the result back. Threads share memory and start in microseconds. So send
**few, big** tasks to processes (chunks), never one tiny task per item.

**6. Fixed version.**

```python
from multiprocessing import Pool

def double(x):
    return x * 2

if __name__ == "__main__":
    with Pool(4) as pool:
        print(pool.map(double, [1, 2, 3]))      # [2, 4, 6]
```
