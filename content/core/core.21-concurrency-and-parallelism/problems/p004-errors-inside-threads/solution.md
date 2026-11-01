## Approach

An exception travels up the **call stack of the thread it was raised in**. The main thread
has its own stack, so a `try` around `t.start()` or `t.join()` never sees it. When the
exception reaches the top of the worker thread's stack, Python calls `threading.excepthook`,
which prints the traceback, and the thread ends. `join()` then returns normally.

So the catching must happen **inside the thread**: the wrapper function `call` runs `func()`
in a `try`, and stores either `("ok", value)` or `("error", exc)` at its index. The main
thread reads the slots after `join()`.

## Code

```python
import threading


def run_and_collect(funcs):
    results = [None] * len(funcs)

    def call(index, func):
        try:
            results[index] = ("ok", func())
        except Exception as exc:
            results[index] = ("error", exc)

    threads = [threading.Thread(target=call, args=(i, f)) for i, f in enumerate(funcs)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results
```

## Complexity

One thread per function; wall time is about the slowest function when they wait on I/O.
Memory O(n).

## Another way

`concurrent.futures` does this for you: `future = executor.submit(func)` and then
`future.result()` **re-raises** the thread's exception in the caller, and
`future.exception()` returns it. That is one of the biggest reasons to prefer executors over
bare threads (p017, p019).

For logging only, you can set `threading.excepthook = my_hook` to decide what happens with
uncaught thread exceptions. But a hook only observes; it cannot hand the error back to the code
that wanted the result.
