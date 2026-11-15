## Approach

Do not walk the tree; **count** its sub-trees. Under each choice of the first digit hang `(n-1)!` leaves, so the first digit is the one whose block contains `k`. Remove it, reduce `k` to its position inside the block, and repeat. This is the factorial number system: `k - 1` written with digits weighted `(n-1)!, (n-2)!, ..., 0!`.

## Code

```python
def kth_permutation(n, k):
    digits = list(range(1, n + 1))
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i
    k -= 1                            # 0-based
    out = []
    for size in range(n - 1, -1, -1):
        i, k = divmod(k, fact[size])  # which block, position inside it
        out.append(str(digits.pop(i)))
    return "".join(out)
```

Example `n = 4`, `k = 9`: `k - 1 = 8`. `8 // 3! = 1` picks `2` (digits left 1, 3, 4), `8 % 6 = 2`. `2 // 2! = 1` picks `3`, `k = 0`. Then `1`, then `4`: `"2314"`.

## Complexity

`O(n^2)` because of `list.pop(i)`, which is tiny for `n <= 9`. No permutations are generated.

## Another way

The same counting can be written recursively: `kth(digits, k)` picks the first digit and calls `kth(rest, k % block)`. You can also test your answer against `itertools.islice(itertools.permutations(...), k - 1, None)` for small `n`.
