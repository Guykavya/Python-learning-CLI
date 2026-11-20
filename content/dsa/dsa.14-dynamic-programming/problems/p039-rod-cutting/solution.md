## Approach

Chapter section 11, "Rod cutting". `f[m]` = the most money for a rod of length `m`.

- **Transition:** choose the length `k` of the first piece; the rest is the sub-problem `f[m - k]`. `f[m] = max(price[k - 1] + f[m - k])` over `k = 1..m`.
- **Base:** `f[0] = 0`.
- **Order:** `m` upwards.

```python
def rod_cut(price, n):
    f = [0] * (n + 1)                    # f[m] = best money for a rod of length m
    for m in range(1, n + 1):
        for k in range(1, m + 1):        # length of the first piece
            f[m] = max(f[m], price[k - 1] + f[m - k])
    return f[n]
```

With `prices = [1, 5, 8, 9, 10, 17, 17, 20]`:

| m | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|
| f[m] | 0 | 1 | 5 | 8 | 10 | 13 | 17 | 18 | 22 |

`f[8] = price[1] + f[6] = 5 + 17 = 22`: a piece of length 2, then a rod of 6 that is best sold whole.

It is an unbounded knapsack (p038): the items are the piece lengths `1..n` (weight `k`, value `price[k - 1]`), each usable any number of times, and the capacity is `n`. Unlike p038, the rod is always used completely, but since every length from 1 is available, any leftover can be sold as pieces, so "at most `n`" and "exactly `n`" give the same answer.

## Complexity

`O(n**2)` time, `O(n)` memory. The plain recursion tries every way to cut: a rod of length `n` has `2**(n - 1)` cuttings (every one of the `n - 1` gaps is cut or not).

## Another way

Remember the best first piece `first[m]` whenever `f[m]` improves, then rebuild the cut list: `while m > 0: pieces.append(first[m]); m -= first[m]`. That is chapter section 9's parent pointers. For `n = 8` it gives `[2, 6]`.
