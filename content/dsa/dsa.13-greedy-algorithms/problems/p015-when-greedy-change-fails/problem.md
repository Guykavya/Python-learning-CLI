# When greedy change fails

A small country uses coins of **1, 3 and 4**. Its vending machines pay change "largest coin first":

```python
def greedy_coins(amount, coins=(4, 3, 1)):
    used = []
    for c in coins:
        while amount >= c:
            amount -= c
            used.append(c)
    return used
```

Chapter section 9 shows that this system is **not canonical**: for 6 the machine pays `[4, 1, 1]`, three coins, while `[3, 3]` uses two. Find **another** amount where the machine pays too many coins.

Write `counterexample()` that returns a tuple `(amount, machine, better)`:

- `amount`: an integer with `1 <= amount <= 1000`, **not** 6;
- `machine`: the list the machine pays, exactly as `greedy_coins(amount)` returns it (largest first);
- `better`: a list of coins from `{1, 3, 4}` that adds up to `amount` and uses the **fewest coins possible**.

The test recomputes the machine's answer, checks that `better` is valid, and checks with a table of fewest-coin counts that `better` really is the fewest and that the machine used more.

## Example

The shape of the answer, using the chapter's amount (not accepted, because it is 6):

```python
>>> counterexample()
(6, [4, 1, 1], [3, 3])
```

## Think about

Greedy fails when taking a 4 leaves a remainder that is "awkward" (needs 1s), while 3s would have divided the amount evenly. Which amounts are sums of only 3s, or of 3s and 4s, but force 1s after greedy's 4s?
