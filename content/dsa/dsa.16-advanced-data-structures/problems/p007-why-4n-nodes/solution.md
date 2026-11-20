## Approach

Separate two counts: the number of **nodes** (`2n - 1`, always) and the largest **index** (depends on the height and the gaps of heap numbering). Bound the index by the height: the bottom level `h` ends at `2**(h + 1) - 1 < 4n`.

## Model answer

See `answer.md`.

## What to check

- You said why indices have gaps (heap numbering reserves `2i` and `2i + 1` even where the tree stops early).
- You derived `2**(h + 1) <= 4n` from `h = ceil(log2 n)`, not just "it is known".
- You named a bad `n` (just above a power of two) and the good case (a power of two).
- You explained what the iterative tree does differently.

## Another way

Measure instead of proving: compute `max_index(1, 0, n)` for every `n` up to a few thousand and plot `max_index / n` (chapter section 4 does this: the ratio stays below 4 and comes close to it just above powers of two).
