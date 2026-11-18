## Hint 1

Split the job in two. (a) For one amount, how many coins does greedy use? (b) For one amount, what is the true fewest? Compare them for every amount from 1 to the bound `c(k-1) + ck - 1`. The answer is `False` as soon as one amount disagrees.

## Hint 2

Greedy's count is the loop of chapter section 9: largest coin first, `count += amount // c`, `amount %= c`.

The true fewest for **all** amounts at once: `best[0] = 0`, and for `a = 1, 2, ...`, `best[a] = 1 + min(best[a - c] for c in coins if c <= a)`. It works because the best way to pay `a` ends with some coin `c`, and the rest `a - c` must itself be paid in the best way; `best[a - c]` is already known because `a - c < a`. Since 1 is a coin, the `min` is never empty.

## Hint 3

```
coins = sorted(coins)
if only one coin: return True
limit = coins[-1] + coins[-2] - 1
best = [0] * (limit + 1)
for a in 1 .. limit:
    best[a] = 1 + min(best[a - c] for c in coins if c <= a)
    if greedy_count(a) != best[a]: return False
return True
```
