## Hint 1

What exactly must be inside the timed code, and what must not? If `factory(range(n))` runs
inside the timed lambda, what are you measuring? How does `timeit.repeat(stmt, number=..., repeat=...)`
report its results: one number, or a list of totals? Which of those numbers is closest to the
true cost of the operation, and how do you turn a total for `number` calls into seconds per call?

For the four operations: why must each one undo what it did?

## Hint 2

```
push_pop_end(c):    c.append(0); c.pop()
push_pop_front(c):  c.insert(0, 0); c.pop(0)
push_pop_left(d):   d.appendleft(0); d.popleft()
search_missing(c):  return -1 in c

time_per_call(op, n, factory, number, repeat):
    container = factory(range(n))                       # once, NOT timed
    totals = timeit.repeat(lambda: op(container), number=number, repeat=repeat)
    return min(totals) / number

measure(...):      {n: time_per_call(op, n, factory, number, repeat) for n in sizes}
growth_kind(...):  "linear" if t_large / t_small >= threshold else "constant"
classify(...):     times = measure(op, [small, large], ...); return growth_kind(times[small], times[large])
```
