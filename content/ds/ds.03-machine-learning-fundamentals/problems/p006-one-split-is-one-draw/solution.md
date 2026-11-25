## Walk-through

Seed 0: no rotation, test rows are `(4, 0), (5, 1), (6, 1)`. The rule says 1, 1, 1. Hits: only the last two. Accuracy 2/3 = 0.667.

Seed 1: rotated by 2 gives `(3,1), (4,0), (5,1), (6,1), (1,0), (2,0)`; test rows are `(6, 1), (1, 0), (2, 0)`. The rule says 1, 0, 0, all correct. Accuracy 1.000.

Seed 2: rotated by 4 gives `(5,1), (6,1), (1,0), (2,0), (3,1), (4,0)`; test rows are `(2, 0), (3, 1), (4, 0)`. The rule says 0, 1, 1: the last one is wrong. Accuracy 0.667.

The accuracy ranges from 0.667 to 1.000 for the same rule.

## What it means

With only three test rows a single split is a very noisy estimate. Even with many rows the score varies with the split. The remedy is to average over several splits (cross-validation, section 9) and to report the spread, not one number.
