# Parallel sum of squares with processes

Summing `i * i` for `i` in `range(n)` is pure CPU work, so threads cannot speed it up (the
GIL). Processes can: split the range into chunks, sum each chunk in a separate process, and
add the partial sums.

Write three functions in `solution.py`:

1. `sum_squares(r)`: takes a `range` and returns the sum of `i * i` over it. This is the
   **worker**. It must be a normal **top-level** function, because it is sent to the worker
   processes by pickling its name.
2. `chunk_ranges(n, k)`: split `range(n)` into **at most `k`** consecutive, non-empty ranges
   whose sizes differ by at most 1, **bigger chunks first**. Together they cover `0 .. n-1`
   exactly once. If `n < k` you get `n` chunks of size 1; if `n == 0`, an empty list.
3. `parallel_sum_squares(n, workers)`: use `chunk_ranges(n, workers)` and a
   `ProcessPoolExecutor` to compute the same number as `sum(i * i for i in range(n))`.
   Use at most `workers` processes, and **no more processes than there are chunks**. For
   `n == 0` return `0`.

Use `from concurrent.futures import ProcessPoolExecutor` at the top of the file (the starter
already does), and call it by that name. The tests check that you really use it.

**Example**

```python
print(chunk_ranges(10, 3))
print(chunk_ranges(2, 4))
print(sum_squares(range(4)))

if __name__ == "__main__":
    print(parallel_sum_squares(1_000_000, 4))
```

```text
[range(0, 4), range(4, 7), range(7, 10)]
[range(0, 1), range(1, 2)]
14
333332833333500000
```

The `if __name__ == "__main__":` guard matters when you run this as a script: on Windows and
macOS (and with Linux's default "forkserver" in Python 3.14) each worker process **imports**
your file. Without the guard, every worker would start its own pool again.
