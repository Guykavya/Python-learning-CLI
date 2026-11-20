# Build a greedy checker

Chapter section 15 ends with a small harness, `find_counterexample`, that runs a greedy and a brute force on random inputs until they disagree. In this problem you build your own version as two reusable functions. You will use them for every greedy idea you meet from now on.

## 1. `first_counterexample(greedy, brute, instances)`

- `greedy` and `brute` are functions that take one instance and return an answer.
- `instances` is any sequence of instances (a list, or any other iterable).
- Go through the instances **in order**. Return the **first** instance where `greedy(instance) != brute(instance)`. Stop there: do not call the functions on any later instance.
- If they agree on every instance (or there are none), return `None`.

## 2. `stress_test(greedy, brute, make_input, trials=1000, seed=0)`

- Create **one** random generator `rng = random.Random(seed)`.
- For each of at most `trials` trials, make a new instance with `make_input(rng)` (call it exactly once per trial, and nothing else uses `rng`).
- At the first instance where the two functions disagree, return the tuple `(instance, greedy_answer, brute_answer)` and stop.
- If all `trials` instances agree, return `None`.

Because the generator is created from `seed`, the same call always finds the same counterexample: a failure can be reproduced.

## The copy rule

A greedy often **sorts its input in place** (chapter section 16, trap 5). Then the brute force, and your report, would see a changed instance. So: **if an instance is a list, give each function its own copy** (`list(instance)`), and return or report the **original**, unchanged instance.

## Example

```python
def greedy_coins(amount):               # largest coin first, coins 1, 3, 4
    count = 0
    for c in (4, 3, 1):
        count += amount // c
        amount %= c
    return count

def dp_coins(amount):                   # fewest coins, by dynamic programming
    best = [0] + [None] * amount
    for a in range(1, amount + 1):
        best[a] = 1 + min(best[a - c] for c in (1, 3, 4) if c <= a)
    return best[amount]

>>> first_counterexample(greedy_coins, dp_coins, range(20))
6
>>> stress_test(greedy_coins, dp_coins, lambda rng: rng.randint(0, 30), trials=500, seed=1) is None
False
>>> first_counterexample(greedy_coins, dp_coins, [0, 1, 2, 3, 4, 5]) is None
True
```

At 6 the greedy pays `4 + 1 + 1` (3 coins), the best is `3 + 3` (2 coins).

The tests also use your checker on two more problems from this module: activity selection by earliest finish (greedy is correct, so the checker must find nothing) and 0/1 knapsack by highest value first (greedy is wrong, and it sorts its input in place).

## Constraints

- Only `random.Random(seed)` for randomness, so results are reproducible. Do not use the global `random.seed`.
- Answers may be any values that can be compared with `!=` (numbers, lists, `None`, ...). `0` and `None` are answers too, not "nothing found".
