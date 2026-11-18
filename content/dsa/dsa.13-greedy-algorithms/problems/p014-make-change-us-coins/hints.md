## Hint 1

Start with the largest coin, 25. How many quarters fit into the amount? Take all of them; what is left is smaller than 25. Then do the same with 10, then 5, then 1. Why can you never need to "go back" and take one quarter fewer with these coins?

## Hint 2

"How many of coin `c` fit into `amount`" is `amount // c`, and what is left is `amount % c` (or `amount - count * c`). `[c] * count` is a list with `count` copies of `c`, and `list.extend` adds them all.

## Hint 3

```
used = []
for c in (25, 10, 5, 1):
    count = amount // c
    used.extend([c] * count)
    amount -= count * c
return used
```
