## Hint 1

For each snippet, ask two questions:

1. *Which chapter section explains why it works today?* (Interning and caches; reference
   counting; `sys.getsizeof` and what it does not count; how `set` stores its items and string
   hash randomisation.)
2. *What would have to be different for it to fail?* A string that was built at run time, a
   Python whose garbage collector does not free objects immediately, values much larger than the
   container, another process with another hash seed.

## Hint 2

```
A: interning makes equal strings share one object  -> breaks for strings built at run time
                                                      (JSON, input(), joins); fix: ==
B: refcount 0 at end of line closes + flushes       -> breaks on PyPy (tracing GC): read before flush,
                                                      leaked handles; fix: with open(...)
C: getsizeof = container only, version dependent    -> huge values never trigger clear(); TypeError on PyPy;
                                                      fix: len(cache) limit / lru_cache(maxsize=...)
D: set order = hash order, str hash randomised      -> differs between runs; fix: sorted(...) or
                                                      dict.fromkeys(...) for first-seen order
guarantee = written as a rule in the docs; detail = "CPython implementation detail" note or undocumented
```
