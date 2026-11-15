## Hint 1

For each situation write down the two numbers that matter: how big is `n` (can you store a table of that size?)
and is the modulus a prime (does an inverse exist for every number you divide by)?

## Hint 2

Pascal's triangle needs `n^2 / 2` memory and time: fine for `n = 2000` (2 million entries), impossible for 10^6.
Method B needs O(N) memory but needs division, so the modulus must be prime and larger than `n`.

## Hint 3

For a single query with small `r`, no table is worth building: compute only `r` factors. For huge `n` with small `r`,
the multiplicative loop works with modular inverses of the numbers `1..r` only.
