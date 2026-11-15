## Hint 1

There are `n!` orderings of `n` distinct values. A correct algorithm must distinguish them all.

## Hint 2

Each comparison is a yes/no question, so `k` comparisons give at most `2^k` outcomes. You need `2^k >= n!`, so `k >= log2(n!)`, which is about `n log2 n`.

## Hint 3

Counting sort never compares two elements: it uses the values as array indices. That needs the values to be small integers (or numbers split into digits).
