## Hint 1

For each idea, write the number of basic steps as a formula in `n` (`n^2 / 2` for pairs, `2^n` for subsets, `n!` for
orders), put in the largest `n`, and divide by 10^7 to get seconds.

## Hint 2

Useful values: `2^20 ~ 10^6`, `10! = 3628800`, `sqrt(10^12) = 10^6`, `log2(10^5) ~ 17`.

## Hint 3

The chapter's table: `n <= 10`: O(n!); `n <= 20`: O(2^n); `n <= 2000` to `5000`: O(n^2);
`n <= 2 * 10^5` to `10^6`: O(n log n) or O(n); larger: O(log n) or O(1).
