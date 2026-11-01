**A. `role is "admin"`**

Detail: **string interning**. CPython interns string literals and many short identifier-like
strings, so two equal strings are often the *same object* and `is` happens to return `True`.
Breaks: a string built at run time is usually a new object: the JSON parser, `input()`,
`"ad" + "min"` computed from variables, or `"admin\n".strip()` all give an equal string that is
not the interned literal, so `can_delete` returns `False` for a real admin. Whether a given string
is interned also differs between versions and implementations (PyPy has different rules). That
is why Python 3.8+ prints `SyntaxWarning: "is" with 'str' literal`.
Fix: compare values: `return role == "admin"`. Use `is` only for singletons (`None`, sentinels).

**B. `open(path, "w").write(text)`**

Detail: **reference counting frees objects immediately**. In CPython the file object's refcount
drops to zero at the end of the line, so it is closed and its buffer flushed before the `open` for
reading. Breaks: on PyPy (tracing GC) or GraalPy, the file object stays open until a later garbage
collection, so the data may still be in the write buffer and the read returns `""` or a partial
file; it also leaks file handles in a loop and, on Windows, may block reopening the file. Even on
CPython, if anything keeps a reference (a traceback in a debugger), the file stays open.
Fix: deterministic cleanup with a context manager:

```python
with open(path, "w") as f:
    f.write(text)
with open(path) as f:
    return f.read() == text
```

**C. `sys.getsizeof(cache)`**

Detail: **object sizes**. `getsizeof` returns the size of the dict's own table only, not of the
keys and values it refers to, and that size depends on the version, the platform and the dict's
history (over-allocation). Breaks: a cache of a few thousand 1 MB strings is gigabytes, while
`getsizeof(cache)` reports a few hundred kilobytes, so `clear()` never happens. On PyPy
`getsizeof` may raise `TypeError`, crashing the function.
Fix: limit what you control, the number of entries: `if len(cache) >= 10_000: cache.clear()`, or
use `functools.lru_cache(maxsize=10_000)`. If bytes really matter, measure with `tracemalloc`
while developing and keep a running total of `len(value)` for byte strings.

**D. `list(set(tags))[0]`**

Detail: **hash table order**. A set's iteration order follows hash values and table size. String
hashes are randomised per process (`PYTHONHASHSEED`), so the order changes from run to run even on
the same CPython; it also changes with the set's size, insertion history and version. Breaks: the
test passes once and fails on the next run (or on the CI machine) with `"python.txt"`.
Fix: choose a defined order: `sorted(set(tags))[0]` (alphabetical, gives `"git"`), or
`next(iter(dict.fromkeys(tags)))` for first-seen order (insertion order of dicts is guaranteed
since 3.7).

**How to tell.** A guarantee is written in the **Language Reference** or the library docs as a
rule ("dicts preserve insertion order"). Details are marked as **"CPython implementation detail"**
in the docs, or are not documented at all (refcount values, `id()` reuse, interning, sizes,
set order). If behaviour is only something you *observed*, assume it can change.
