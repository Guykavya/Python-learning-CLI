## Approach

Separate two costs: the **depth** of the recursion (how many calls wait at the same time, limited by Python) and the **number of calls** (the total work). `power` has depth `n`; `fast_power` has depth about `log2 n` and makes only one call per level.

## Model answer

See `answer.md` and tick the checklist at its end.

## What to check

- `power(2, 10**6)` raises `RecursionError` long before it runs out of time: the depth is the problem, not the speed.
- The chain 1000000, 500000, 250000, ... reaches 0 after about 21 steps.
- Two recursive calls per level double the tree: `1 + 2 + 4 + ... + n` is about `2n` calls.
- Increasing the recursion limit trades a clean error for a possible hard crash.

## Another way

A loop does the same "square and multiply" without any stack (fast exponentiation on the bits of `n`), and Python's built-in `pow(x, n)` and `x ** n` already use it.
