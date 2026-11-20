## Hint 1

Adding `x`: `count[x] += 1`, and if it became 1, one more distinct genre. Removing `x`: `count[x] -= 1`, and if it became 0, one fewer. Each step is `O(1)`.

## Hint 2

Sort the question indices by `(l // B, r)` with `B` about `sqrt(n)`. Within one block of `l`, the right edge only moves forward (at most `n` steps per block), and the left edge moves less than `B` per question.

## Hint 3

For each question in that order: grow left (`cur_l > l`), grow right (`cur_r < r`), then shrink left (`cur_l < l`), shrink right (`cur_r > r`). Growing first means the window is never "negative" (`cur_l > cur_r`), so counts never go below zero. Store the answer at the question's original index.
