## Hint 1

With `n` digits, each choice of the first digit is followed by `(n-1)!` permutations. So the first digit is determined by which block of size `(n-1)!` contains `k`.

## Hint 2

Work with `k - 1` (0-based). The index of the first digit among the remaining sorted digits is `(k - 1) // (n-1)!`, and the new `k - 1` is `(k - 1) % (n-1)!`. Repeat with one digit fewer.

## Hint 3

```
digits = [1..n]; k -= 1; out = []
for size in n-1 down to 0:
    block = size!
    i = k // block; k = k % block
    out.append(digits.pop(i))
return joined out
```
