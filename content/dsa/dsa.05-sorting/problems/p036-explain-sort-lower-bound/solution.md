## Approach

Count the outcomes: a correct sort distinguishes all `n!` permutations, and each yes/no comparison at most doubles what it can distinguish.

## Model answer

See `answer.md`. Compare it with yours point by point.

## What to check

- States `n!` possible inputs and `2^k` outcomes after `k` comparisons.
- Concludes `k >= log2(n!)`; for `n = 4`, `4! = 24` and `2^4 = 16 < 24 <= 2^5`, so at least 5 comparisons.
- Mentions Stirling or the fact `log2(n!)` is about `n log2 n`.
- Counting and radix sort avoid comparisons and need bounded integer keys.
