## Approach

Count the choices. The engine has to decide how to group the run of `a`s, and there are
`2^(n-1)` groupings. On a failing input every grouping is tried before the engine gives up, which
is exactly the 4x-per-two-letters growth in the table. On a matching input the first grouping
succeeds, so the problem hides until someone sends a near-miss.

The cure is to remove the ambiguity: `a+b` accepts the same language with a single choice per
character. Atomic groups `(?>...)` and possessive quantifiers `*+ ++ ?+` (Python 3.11+) are the
other tool: they forbid going back into a finished group.

See `answer.md` for the full model answer.

## Complexity

`(a+)+b` on a failing input: O(2^n) per start position. `a+b`: O(n) per start position (O(n^2)
for `search` over all starts in the worst case, still tiny).

## Another way

Measure it yourself:

```python
import re, timeit
for n in range(14, 24, 2):
    s = "a" * n + "c"
    print(n, timeit.timeit(lambda: re.search(r"(a+)+b", s), number=1))
```

Stop at about 24: every extra letter doubles the time.
