# Stress test harness

Write the reusable function of chapter section 13:

```python
stress(fast, brute, gen, trials=1000, seed=1)
```

- `gen(rng)` receives a `random.Random` object and returns the **arguments** of one test case as a **tuple**.
- For every trial, call `fast(*case)` and `brute(*case)` and compare.
- Return `(case, fast_result, brute_result)` for the **first** trial where the results differ. Return `None` if all `trials` agree.
- The `rng` is `random.Random(seed)`, created **once**: the same seed always produces the same sequence of cases.

Details the tests check:

1. `fast` and `brute` may **change** their arguments (for example sort a list in place). Each must get its own **deep copy**, and the `case` you return must be the original, unchanged one.
2. If a function **raises** an exception, that counts as a result: use the exception object as the result for that function. Two exceptions of the same type are considered equal. A trial where exactly one function raises is a difference.
3. Stop at the first difference: do not call `gen` again after it.

## Example

```python
def fast(a):        # buggy Kadane: best starts at 0
    best = cur = 0
    for x in a:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best

def brute(a):
    n = len(a)
    return max(sum(a[i:j]) for i in range(n) for j in range(i + 1, n + 1))

def gen(rng):
    return ([rng.randint(-5, 5) for _ in range(rng.randint(1, 5))],)

case, a, b = stress(fast, brute, gen)
print(case, a, b)     # a tiny list of negative numbers: fast says 0, brute says a negative number
```
