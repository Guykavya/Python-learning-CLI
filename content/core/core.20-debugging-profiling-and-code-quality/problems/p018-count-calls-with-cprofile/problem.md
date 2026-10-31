# Count calls with cProfile

Timings from a profiler change from run to run, but **call counts do not**. "This function was
called 177 times to compute `fib(10)`" is a fact you can test, and very often the reason code is
slow is that something runs far more often than you thought.

Write `call_counts(fn, *args, **kwargs) -> dict[str, int]` in `solution.py`. It runs
`fn(*args, **kwargs)` under `cProfile` and returns a dictionary that maps the **name** of every
Python function that ran (including `fn` itself) to how many times it was called in total.

Rules:

- Use `cProfile.Profile` and read the numbers with `pstats.Stats(profiler).stats`. That
  dictionary maps a key `(filename, line_number, function_name)` to a tuple whose first two items
  are `primitive_calls` and `total_calls`. Recursive calls are counted in `total_calls` only, so
  use that one.
- Leave out built-in functions (`len`, `list.append`, the profiler's own `disable`, ...). In the
  stats their filename is `"~"`.
- If two different functions have the same name (for example two `helper`s in two files), add
  their counts together.
- The profiler must always be switched off before `call_counts` returns, **even if `fn` raises**.
  The exception must reach the caller unchanged. (Only one profiler can be active at a time
  since Python 3.12, so a profiler left running breaks the next `call_counts`.)

**Example**

```python
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

def main():
    return [fib(i) for i in range(3)]

call_counts(fib, 10)
# {'fib': 177}

call_counts(main)
# {'main': 1, 'fib': 5}     (fib(0): 1 call, fib(1): 1 call, fib(2): 3 calls)
#  in Python 3.11, a comprehension also shows up as its own function '<listcomp>'
```
