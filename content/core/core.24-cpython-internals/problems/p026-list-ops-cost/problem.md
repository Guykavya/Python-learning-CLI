# Measure it: which list operations are O(n)?

A CPython `list` is a **dynamic array**: one block of memory holding pointers to the items, in
order. Adding or removing at the **end** touches one slot, but adding or removing at the **front**
has to shift every other pointer by one place. A `collections.deque` is a linked list of blocks,
so both of its ends are cheap. And `x in container` scans a list item by item but jumps straight
to one slot of a set's hash table.

The chapter told you this. Now **prove it** with measurements that work on any machine. Absolute
times are useless for that (a laptop on battery is slower than a desktop), so compare the time of
one operation on a container of **1,000** items with the same operation on **100,000** items:
a constant-time operation takes about the same time; a linear one is roughly 100 times slower.

Copy `starter.py` to `solution.py` and write:

**Four operations**, each doing one thing to `container` and leaving it exactly as it was (so
every timed call sees the same size):

- `push_pop_end(c)`: `append` one item, then `pop()` it.
- `push_pop_front(c)`: `insert(0, ...)` one item, then `pop(0)` it.
- `push_pop_left(d)`: for a deque, `appendleft` one item, then `popleft()` it.
- `search_missing(c)`: return `-1 in c` (never present in `range(n)`, so it is the worst case).

**Measuring:**

- `time_per_call(op, n, factory=list, number=200, repeat=5)`: build the container **once** with
  `factory(range(n))`, then use `timeit.repeat` to time `number` calls of `op(container)`,
  `repeat` times. Return the **best** (smallest) timing divided by `number`: seconds per call.
- `measure(op, sizes, factory=list, number=200, repeat=5)`: a dict `{n: time_per_call(...)}`.
- `growth_kind(t_small, t_large, threshold=5.0)`: `"linear"` if `t_large / t_small` is at least
  `threshold`, otherwise `"constant"`.
- `classify(op, factory=list, small=1_000, large=100_000, number=200, repeat=5)`: measure both
  sizes and return their `growth_kind`.

**Example** (your times will differ; the verdicts will not)

```python
>>> measure(push_pop_front, [1_000, 100_000])
{1000: 8.3e-07, 100000: 0.000101}          # about 120 times slower
>>> classify(push_pop_end)
'constant'
>>> classify(push_pop_front)
'linear'
>>> classify(push_pop_left, deque)
'constant'
>>> classify(search_missing, list), classify(search_missing, set)
('linear', 'constant')
```

Why the **best** of several repeats? Anything that disturbs a measurement (another program,
the garbage collector, the CPU changing speed) only ever makes it *slower*. The minimum is the
run with the least disturbance, the closest to the true cost.
