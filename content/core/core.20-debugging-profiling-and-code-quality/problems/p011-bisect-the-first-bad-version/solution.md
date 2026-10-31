## Approach

This is binary search for a **boundary**: the list looks like
`good good good bad bad bad`, and we want the first `bad`.

Keep a half-open search range of **indexes** `[lo, hi]` that always contains the answer, where
`hi == n` stands for "no bad version". At the start that is `[0, n]`.

- Test the middle `mid`. If it is bad, the first bad version is `mid` or earlier: `hi = mid`.
- If it is good, the first bad version is after it: `lo = mid + 1`.
- Each test halves the range. When `lo == hi` one candidate is left and we are done; no extra
  call is needed to "confirm" it, because the invariant already proves it.

Counting: the range starts with `n + 1` candidates, so we need `ceil(log2(n + 1))` calls at
most, which is never more than `ceil(log2(n)) + 1`. For 1,000 versions that is 10.

## Code

```python
def first_bad(versions: list, is_bad):
    lo, hi = 0, len(versions)
    while lo < hi:
        mid = (lo + hi) // 2
        if is_bad(versions[mid]):
            hi = mid
        else:
            lo = mid + 1
    return versions[lo] if lo < len(versions) else None
```

## Complexity

O(log n) calls of `is_bad`, O(1) extra space. Since `is_bad` is the expensive part (a build and
a test run), the number of calls is what matters.

## Another way

`bisect.bisect_left` can do the search when you give it a `key`:

```python
import bisect

def first_bad(versions, is_bad):
    i = bisect.bisect_left(range(len(versions)), True, key=lambda j: is_bad(versions[j]))
    return versions[i] if i < len(versions) else None
```

`key=` exists from Python 3.10. In real projects `git bisect start`, `git bisect bad`,
`git bisect good <old>` and then `git bisect run pytest tests/test_x.py` runs exactly this
loop over your commits, with your test as `is_bad`.
