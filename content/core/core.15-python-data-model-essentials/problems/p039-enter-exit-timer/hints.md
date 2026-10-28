## Hint 1

`with Timer() as t:` does `t = Timer().__enter__()` and later `__exit__(exc_type, exc, tb)`. What must `__enter__` return so that `t` is the timer and you can read `t.elapsed`? What do the three arguments of `__exit__` hold when the block ends normally?

## Hint 2

`__exit__` returns a true value only if it wants to **swallow** the exception. Return `False` (or nothing) to let the exception continue. `elapsed` needs two cases, depending on `self.running`.

## Hint 3

```
__enter__: self._start = clock() ; running = True ; return self
__exit__(exc_type, exc, tb): self._elapsed = clock() - _start ; running = False ; return False
elapsed (property): if running: return clock() - _start   else: return _elapsed
```
