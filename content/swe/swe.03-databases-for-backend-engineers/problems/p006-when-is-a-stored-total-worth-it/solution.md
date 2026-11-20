## Approach

The model answer is in `answer.md`. Remember the rule: **normalise first, denormalise on purpose**, with a way to check the copy.

## Complexity

Reading the total: `O(lines)` computed, `O(1)` stored. Writing a line: `O(1)` plus one extra `UPDATE` when stored.

## Another way

A **materialised view** or a summary table refreshed in batches. The data is slightly old but never wrong in structure.

## Why it matters

Denormalised values are a bet on speed against correctness. You win the bet only if you can **prove** the copy is right whenever you want.
