## Approach

Two nested loops. The outer loop runs `repeat` batches. Each batch reads the clock, calls `fn`
`number` times, and reads the clock again. The batch time divided by `number` is the per-call
time. The answer is the smallest per-call time.

Why the minimum: every disturbance (another program, the garbage collector, a page fault) adds
time, nothing subtracts it. The fastest batch is the least disturbed one, so it is the best
estimate of what the code itself costs. That is what `timeit.repeat` users are told to do:
`min(timeit.repeat(...)) / number`.

Why read the clock only around the batch: `perf_counter()` itself takes tens of nanoseconds. If
the function takes 50 ns and you read the clock around every call, half of what you measure is
the clock.

## Code

```python
import time


def best_time(fn, number, repeat, timer=time.perf_counter):
    if number < 1 or repeat < 1:
        raise ValueError("number and repeat must be at least 1")
    per_call = []
    for _ in range(repeat):
        start = timer()
        for _ in range(number):
            fn()
        end = timer()
        per_call.append((end - start) / number)
    return min(per_call)
```

## Complexity

`number * repeat` calls of `fn`, `2 * repeat` clock reads, O(repeat) extra memory for the list
(O(1) if you keep a running minimum instead).

## Another way

Let `timeit` do the batching:

```python
import timeit

def best_time(fn, number, repeat, timer=time.perf_counter):
    if number < 1 or repeat < 1:
        raise ValueError("number and repeat must be at least 1")
    return min(timeit.repeat(fn, number=number, repeat=repeat, timer=timer)) / number
```

`timeit` also turns off the garbage collector during each batch, which makes runs more
similar to each other (and can hide GC cost that real code would pay).
