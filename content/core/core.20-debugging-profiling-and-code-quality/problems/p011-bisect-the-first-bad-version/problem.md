# Bisect the first bad version

"It worked last month, and now it is broken. Which change broke it?" With 1,000 commits in
between, testing them one by one is hopeless if each test takes a minute. `git bisect` answers
the question with about **10** tests: it checks the middle commit, keeps the half that contains
the change from good to bad, and repeats.

That only works because the history is **monotone**: every version before the first bad one is
good, and every version from it on is bad.

Write `first_bad(versions: list, is_bad) -> object | None` in `solution.py`:

- `versions` is ordered oldest to newest. `is_bad(v)` returns `True` or `False` and is
  **expensive**: imagine it builds the project and runs the test suite.
- Return the **first** bad version, or `None` if every version is good (or the list is empty).
- Call `is_bad` at most **`ceil(log2(n)) + 1`** times for `n` versions (11 calls for 1,000
  versions). Only call it with items of `versions`.

`starter.py` already has a correct but slow version that tests every version in order. Keep
its answers, make it fast.

**Example**

```python
versions = [f"v{i}" for i in range(1, 9)]       # v1 .. v8
first_bad(versions, lambda v: int(v[1:]) >= 6)  # 'v6', with at most 4 calls of is_bad
first_bad(versions, lambda v: False)            # None
first_bad([], lambda v: True)                   # None, without calling is_bad
```
