**1. The two protocols.** An *iterable* is anything you can pass to `iter()`: it has `__iter__`, which
returns an *iterator*. An *iterator* is the object that does the walking: it has `__next__` (give the next
value, or raise `StopIteration` when finished) and `__iter__` that returns **itself**. A `for` loop calls
`iter(obj)` once, then calls `next()` on the result again and again until `StopIteration`.

**2. Why the second `list(c)` is empty.** `CountDown.__iter__` returns `self`, so the object is its own
iterator and carries one counter, `self.n`. The first `list(c)` runs the counter down to 0 and raises
`StopIteration`. The second `list(c)` calls `iter(c)`, gets the *same* exhausted object, and stops at
once: `[]`. That is also why `max(c)` followed by `min(c)` breaks: `min` sees nothing and raises
`ValueError`.

**3. Why `Range3` works twice.** `Range3.__iter__` is a generator function. Every call to
`iter(r)` creates a **fresh** generator object with its own position. The `Range3` object itself holds no
position, so it can start over as often as you like. It is an iterable, not an iterator.

**4. The fix.** Separate the two roles: keep `CountDown` as the iterable (just stores `start`) and make
`__iter__` return a new iterator each time, either a generator (`while n > 0: yield n; n -= 1`) or a small
separate iterator class.

**5. Which is "correct"?** Iterators *must* be single-pass (they are used up), and Python even expects
`iter(it) is it`. Containers and ranges (`list`, `range`, `Range3`) should be iterables that return a fresh
iterator, so you can loop over them twice, nest loops over the same object, and call `max` and `min` on them.
Mixing both roles into one object (like `CountDown`) is only right for a one-shot stream such as a file
or a generator.
