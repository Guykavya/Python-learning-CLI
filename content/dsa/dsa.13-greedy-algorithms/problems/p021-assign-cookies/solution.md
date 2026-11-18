## Approach

Sort both lists and give each cookie, from the smallest, to the **least greedy child who is still unhappy**, if it is big enough. A cookie that is too small for that child is too small for every child left (they are all greedier), so it is thrown away.

**Why it is safe (exchange).** Let `x` be the least greedy child and `c` the smallest cookie with `c >= greed(x)`. Take any optimal assignment and change it so that `x` gets `c`:

- If `x` has another cookie `c'` and `c` belongs to a child `y`, swap them. `x` is happy with `c`. `y` is happy with `c'`, because `c' >= c` (`c` is the smallest cookie that fits `x`, and `c'` fits `x`) and `c >= greed(y)`.
- If `x` has no cookie and `c` belongs to `y`, move `c` from `y` to `x`: one happy child is replaced by another.
- If `c` is unused, give it to `x` (and free the cookie `x` had, if any).

In every case the number of happy children does not drop, so some optimal answer makes the greedy choice; the rest is the same problem on fewer children and cookies.

```python
def assign_cookies(greed, sizes):
    greed = sorted(greed)
    sizes = sorted(sizes)
    child = 0
    for cookie in sizes:
        if child < len(greed) and cookie >= greed[child]:
            child += 1                  # this child is happy; move to the next one
    return child
```

## Complexity

`O(n log n + m log m)` for the two sorts, then one `O(m)` pass. Extra space `O(n + m)` for the sorted copies.

## Another way

Go from the other end: the **greediest** child first, with the **biggest** cookie. If the biggest cookie left satisfies the greediest child left, give it; otherwise that child can never be satisfied, so skip the child.

```python
def assign_cookies(greed, sizes):
    greed = sorted(greed, reverse=True)
    sizes = sorted(sizes, reverse=True)
    happy = 0
    for g in greed:
        if happy < len(sizes) and sizes[happy] >= g:
            happy += 1
    return happy
```
