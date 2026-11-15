**Costs.**
- A (Pascal): O(n^2) time and memory to build rows up to `n`. Each query is O(1) afterwards. No division, so any modulus works (or none, with exact big ints).
- B (factorial + inverse factorial tables): O(N) time and memory to build, O(1) per query. Needs a **prime** modulus `p` larger than `N`, so that every `i <= N` is invertible.
- C (multiplicative loop): O(r) time per query, O(1) memory, exact integers. No table, no modulus needed.

**1. `n, r <= 60`, exact.** Pascal's triangle (A): only 1800 entries, no division, exact big integers. The loop (C) would work too.

**2. `n <= 10^6`, 10^5 queries, mod `10^9 + 7`.** Method B. A table of 10^6 factorials is cheap, and each query is three multiplications. Pascal would
need 10^12 entries; the loop C would need up to 10^6 steps per query, so about 10^11 in all. `10^9 + 7` is prime and bigger than `n`, so all inverses exist.

**3. `n <= 2000`, modulus 10^9.** Pascal's triangle (A). The modulus is not prime, so numbers like 2 and 5 have no inverse mod 10^9 (they share factors
with it). Fermat's `x^(p-2)` does not apply, and `fact[i]` may even be 0 mod 10^9 for larger `i`. Pascal needs only additions, and 2000^2 / 2 = 2 million entries is fine.

**4. One query, `n = 10^5`, `r = 3`.** The loop (C): 3 multiplications and divisions. Building tables of 10^5 entries would be far more work than the query itself. Even `math.comb(n, r)` is a good answer.

**5. `n <= 10^18`, `r <= 10^5`, mod `10^9 + 7`.** Method C, done modulo p: numerator `n * (n-1) * ... * (n-r+1)` in O(r), divided by `r!` using an inverse of `r!`. Only `r!` is needed, so only O(r) work
and nothing proportional to `n` is stored. (This requires `r < p`, so that `r!` is invertible. If `n >= p`, the numerator can contain a multiple of `p`: in that case more theory (Lucas' theorem) is needed.)

**6. When B fails.** When the modulus is not prime (inverses of numbers sharing a factor with the modulus do not exist), or when `n >= p` so that some `fact[i]` is 0 mod `p` and has no inverse.
B needs a prime modulus bigger than every `n` used, so that `i!` is never a multiple of `p` and therefore always has an inverse (Fermat or extended Euclid).
