## Approach

Build the counterexample from the failure pattern of chapter section 8: one dense but **awkward** item whose weight leaves a gap that nothing else fills, next to two slightly less dense items that fill the bag exactly. Then point at the exact step of the fractional proof that needs divisibility.

## Model answer

See `answer.md`.

## What to check

- Your instance really fails: compute greedy's total and the best total, and check every subset if you are unsure (with three items there are only 8).
- You named the **illegal step** ("remove a little"), not just "0/1 is harder".
- You explained the loss through the **empty space**.
- You did not claim that some other sort key fixes it.

## Another way

Let the computer find instances: generate random lists of 3 or 4 items with `random.Random(seed)`, compare `knapsack_greedy_01` with `knapsack_brute_01` from chapter section 8, and print the first instance where they differ. Then explain **that** instance in words; random search finds the failures, you supply the reason.
