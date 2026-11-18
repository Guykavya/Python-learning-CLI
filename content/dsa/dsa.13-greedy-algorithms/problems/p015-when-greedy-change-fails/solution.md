## Approach

Greedy loses when its 4s leave a remainder of 2: that remainder costs two 1s. Trading the last `4 + 1 + 1` (three coins) for `3 + 3` (two coins) pays the same amount with one coin fewer. 10 is the next amount after 6 with that remainder.

- Machine: `10 = 4 + 4 + 1 + 1`, four coins.
- Better: `10 = 4 + 3 + 3`, three coins. Two coins can pay at most `4 + 4 = 8`, so three is the fewest.

```python
def counterexample():
    return (10, [4, 4, 1, 1], [4, 3, 3])
```

Other valid answers: `14` (machine `4, 4, 4, 1, 1`; better `4, 4, 3, 3`), `18`, `22`, ... In this system greedy is never off by more than one coin: an amount `4q + 2` needs at least `q + 1` coins (each coin is at most 4), the trade above reaches `q + 1`, and greedy uses `q + 2`. For remainders 0, 1 and 3 greedy is already optimal.

## Complexity

Constant: the function returns fixed values. The test's table is `O(amount * 3)`.

## Another way

Search: `for a in range(1, 100): if len(greedy_coins(a)) != fewest[a]: print(a)`, with a fewest-coin table or the BFS of chapter section 9. It prints 6, 10, 14, 18, ... (every amount that leaves remainder 2 after the 4s, from 6 on). This is how section 9's `first_failure` works, and p016 turns it into a full check.
