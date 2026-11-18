## Hint 1

Process the coins **one at a time** in the outer loop. While coin `c` is being processed, `f[a]` counts the combinations of `a` that use only the coins seen so far. Adding coin `c` means: a combination of `a` that uses `c` at least once is a combination of `a - c` (with the coins so far, `c` included) plus one more `c`.

## Hint 2

Every combination is then built in one fixed order (all copies of the first coin, then all of the second, ...), so it is counted once. If the amount loop is outside instead, every order is counted separately: that is p020.

## Hint 3

```
f = [0] * (amount + 1); f[0] = 1
for c in coins:                       # outer: coins
    for a in c..amount:               # inner: amounts, upward
        f[a] += f[a - c]
return f[amount]
```
