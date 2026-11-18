## Hint 1

First get the number right: the fewest-coins table of section 7, `f[a] = 1 + min(f[a - c])`, with `f[0] = 0` and `INF` for "impossible". Then add a second list `last`, where `last[a]` is the coin that gave the best `f[a]`. When exactly may you write into `last[a]`?

## Hint 2

Write `last[a] = c` **inside** the `if` that improves `f[a]`, never after the loop over coins (that would store the last coin *tried*). After the table is full: if `f[amount]` is `INF`, return `None`. Otherwise start at `a = amount`, append `last[a]`, subtract it, and repeat until `a` is 0.

## Hint 3

```
f = [INF] * (amount+1);  f[0] = 0;  last = [None] * (amount+1)
for a in 1..amount:
    for c in coins:
        if c <= a and f[a-c] + 1 < f[a]:
            f[a] = f[a-c] + 1
            last[a] = c
if f[amount] is INF: return None
used = [];  a = amount
while a > 0: used.append(last[a]); a -= last[a]
return used
```
