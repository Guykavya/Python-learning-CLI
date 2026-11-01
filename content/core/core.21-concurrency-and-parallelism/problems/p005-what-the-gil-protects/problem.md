# Explain: what the GIL does and does not protect

A classmate says three things:

> "Python has the GIL, so only one thread runs at a time. That means my threads can never have
> race conditions, so `counter += 1` from many threads is safe. But it also means threads are
> useless in Python: they never make anything faster."

Each sentence is partly right and partly wrong. Write `answer.md` (about 300 to 450 words)
that explains, in your own words:

1. **What the GIL is**: what it protects, and when a thread gives it up (two different
   reasons).
2. **Why `counter += 1` is still a race.** Use the bytecode below to point at the exact gap.
3. **Why CPU-bound threads do not get faster** in normal CPython, and why **I/O-bound** threads
   do.
4. **Free-threaded Python**: what changed in the `3.13t` / `3.14t` builds, how a program can
   check which mode it is running in, and what that means for code like `counter += 1`.
5. One sentence of advice that is true **with and without** the GIL.

`dis.dis("counter += 1")` on Python 3.14 shows (simplified):

```text
LOAD_NAME     counter      # read the current value
LOAD_SMALL_INT 1
BINARY_OP     += (inplace add)
STORE_NAME    counter      # write the new value back
```

**Example of the level of detail expected (a different question)**

> *"Is `my_list.append(x)` from two threads safe?"* In CPython, yes in practice: `append` is a
> single call into C code that finishes before another thread can run Python code on that
> list (and the free-threaded build adds a per-object lock to lists). But "append then read
> `len()` then decide" is several steps and is **not** atomic. Use a `Lock` or a `queue.Queue`
> as soon as there is more than one step.
