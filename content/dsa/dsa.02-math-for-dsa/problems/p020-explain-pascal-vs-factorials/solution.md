The model answer is shown when you check. The ideas that must appear:

1. Costs: A is O(n^2) time and memory, no division. B is O(N) tables, O(1) per query, needs a prime modulus bigger than `n`. C is O(r) per query with no table.
2. Situation 1: Pascal (or C), exact. Situation 2: B. Situation 3: Pascal, since 10^9 is not prime and inverses do not exist. Situation 4: C.
3. Situation 5: C, using `r!`'s inverse; you cannot tabulate up to 10^18, but only `r` factors are needed.
4. B fails when the modulus is composite, or when `n` reaches the prime (then `n!` is 0 mod `p`).
