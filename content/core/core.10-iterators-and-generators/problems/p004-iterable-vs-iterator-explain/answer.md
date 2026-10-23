**1. The difference.** An *iterable* is any object you can ask for an iterator with `iter(x)`: a list, a string, a dict, a file, a `range`. `nums` is an iterable. An *iterator* is the object that does one pass: it remembers where it is and gives the next item when you call `next()`. `it` is an iterator. An iterator is also iterable, because `iter(it)` returns `it` itself.

**2. Why only once.** `it` keeps a position that only moves forward. The first `list(it)` moves it to the end. When it has reached the end it raises `StopIteration` every time, so the second `list(it)` finds nothing and returns `[]`. `nums` holds the data and has no position. Each `list(nums)` or `for` loop calls `iter(nums)`, which builds a new iterator that starts at the beginning.

**3. What `for` does.** `for x in obj` calls `iter(obj)` once, then calls `next()` on the result again and again, and stops quietly when `StopIteration` is raised.

**4. Consequence.** A generator is an iterator. If I write `total = sum(gen)` and later `count = len(list(gen))`, the second line sees an empty generator and gives `0`. I must either make a new generator, or keep a list.
