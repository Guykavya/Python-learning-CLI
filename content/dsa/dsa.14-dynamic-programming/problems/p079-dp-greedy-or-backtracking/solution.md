## Approach

Decide by what the problem **allows**, not by what it looks like:

| Question | If yes |
|---|---|
| Must every solution be listed? | backtracking (the output alone is exponential) |
| Is one local choice provably safe? | greedy |
| Do many choice sequences reach the same small state? | DP |

Then check the sizes: a DP table must fit (`n * W` cells), and backtracking must have a small search space or strong pruning.

## Model answer

See `answer.md`.

## What to check

- Every greedy choice comes with a **reason** it is safe (canonical coins, earliest end, fractions), and every rejected greedy with a **counterexample** (6 with `[1, 3, 4]`; whole items in the knapsack).
- Every DP choice names the **state** in a few words.
- You saw that the pairs (5/6, 8 and its twin) are about one property: swapping by weight, listing vs counting.
- You did not pick backtracking for a problem that only asks for a number or a best value; it would work for tiny inputs and fail at the sizes given.

## Another way

Settle a doubt with code, as in chapter section 22: write the greedy and the DP, run both on every small input, and look for the first difference. For task 1 that finds nothing; for task 2 it finds 6 at once.
