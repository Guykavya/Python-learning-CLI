## Hint 1

Imagine playing "guess my number between 1 and 100" where the answer is only "higher" or "lower". What is your best first guess? How many guesses will you need at most?

## Hint 2

After each probe the number of candidates is cut in half: `n, n/2, n/4, ...`. The search ends when 1 candidate is left, so the number of probes is the number of times you can halve `n`: about `log2(n)`.

## Hint 3

Sorting costs `O(n log n)`, which is more than one linear scan of `O(n)`. Sorting pays off when you answer many queries: the sort is paid once, each query costs only `O(log n)`.
