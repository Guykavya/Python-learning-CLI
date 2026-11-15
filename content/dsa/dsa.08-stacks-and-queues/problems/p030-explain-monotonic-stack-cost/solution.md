## Approach

Replace "worst case per loop times number of loops" by "total work over the whole run". The quantity that makes this easy is the number of pushes and pops: each index contributes one push and at most one pop.

## Model answer

See `answer.md`.

## What to check

- You agreed that a single `while` can be long, with an example, instead of denying it.
- Your proof counts **pops**, links each `while` iteration to one pop, and concludes "at most `n` in total".
- You named amortised analysis and gave a second example from the module.
- You separated time (`O(n)`) from memory (stack up to `n`).

## Another way

A **potential** argument: let the potential be the size of the stack. A `for` step pushes once (+1) and pops `k` times (-k) at a real cost of `k + 1`. Real cost plus change in potential is `(k + 1) + (1 - k) = 2`, a constant per step. The potential starts at 0 and is never negative, so the total real cost is at most `2n`. This is the same counting in a more formal dress, and it is how textbooks (CLRS, chapter 17) present amortised analysis.

You can also measure it: put a counter in the `while` loop and run the function on 1,000 random lists of length 10,000. The counter never goes above 10,000.
