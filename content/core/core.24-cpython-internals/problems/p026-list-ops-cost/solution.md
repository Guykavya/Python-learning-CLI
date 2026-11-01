## Approach

To see how a cost **grows**, keep everything the same except n. Each operation leaves the
container unchanged, the container is built once outside the timed code, and the same op is timed
at n = 1,000 and n = 100,000. The ratio of the two times answers the question without any
absolute number: about 1x for O(1), about 100x for O(n). A threshold of 5x sits far from both, so
noise cannot flip the verdict.

Why the results come out as they do (CPython):

- `append`/`pop()` write or clear one slot at the end. When the array is full, `append`
  reallocates with extra room (over-allocation), so the occasional copy is spread over many cheap
  appends: **amortised O(1)**. Our op pops right after appending, so no resize happens at all.
- `insert(0, x)`/`pop(0)` call `memmove` on all n pointers: **O(n)**, even though `memmove` is
  fast C code.
- `deque` keeps a doubly linked list of 64-item blocks; both ends are **O(1)**.
- `-1 in list` compares `-1` with every item: **O(n)**. `-1 in set` hashes `-1` and probes a slot
  or two: **O(1)** on average.

## Code

```python
"""Measure how the cost of a container operation grows with the container's size."""

import timeit
from collections import deque


# ---------------------------------------------------------------- one operation each,
# every function leaves the container the same size it found it


def push_pop_end(container):
    container.append(0)
    container.pop()


def push_pop_front(container):
    container.insert(0, 0)
    container.pop(0)


def push_pop_left(container):
    container.appendleft(0)
    container.popleft()


def search_missing(container):
    return -1 in container


# ---------------------------------------------------------------- measuring


def time_per_call(op, n, factory=list, number=200, repeat=5):
    """Seconds for ONE call of op on a container of n items: the best of `repeat` timings."""
    container = factory(range(n))
    best = min(timeit.repeat(lambda: op(container), number=number, repeat=repeat))
    return best / number


def measure(op, sizes, factory=list, number=200, repeat=5):
    """{n: seconds per call} for every n in sizes."""
    return {n: time_per_call(op, n, factory, number, repeat) for n in sizes}


def growth_kind(t_small, t_large, threshold=5.0):
    """'linear' if the large size is at least `threshold` times slower, else 'constant'."""
    return "linear" if t_large / t_small >= threshold else "constant"


def classify(op, factory=list, small=1_000, large=100_000, number=200, repeat=5):
    """Time op at two sizes and say whether its cost is constant or grows with n."""
    times = measure(op, [small, large], factory, number, repeat)
    return growth_kind(times[small], times[large])
```

## Complexity

`time_per_call` costs `repeat * number` calls of the operation plus O(n) to build the container
once. For the linear operations at n = 100,000 a single call already takes about 0.1 ms
(`insert`/`pop(0)`) or 1 ms (`in` on a list), which is why the tests pass a smaller `number` for them.

## Another way

Without `timeit`, use `time.perf_counter()` around a loop of `number` calls and keep the
minimum over `repeat` rounds:

```python
def time_per_call(op, n, factory=list, number=200, repeat=5):
    container = factory(range(n))
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        for _ in range(number):
            op(container)
        best = min(best, (time.perf_counter() - start) / number)
    return best
```

`timeit` does the same, but also turns off the garbage collector during the timing and keeps the
loop overhead as small as possible. For a fuller picture, measure at many sizes
(`measure(op, [1_000, 2_000, 4_000, ...])`) and plot time against n: a flat line is O(1), a
straight rising line is O(n).
