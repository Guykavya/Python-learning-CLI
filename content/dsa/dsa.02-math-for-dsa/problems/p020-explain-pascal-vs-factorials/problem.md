# Which nCr method, and when?

You now know three ways to compute `C(n, r)`:

- **A. Pascal's triangle:** build rows with `C(n, r) = C(n-1, r-1) + C(n-1, r)`.
- **B. Factorial tables with modular inverses:** `fact[n] * inv_fact[r] * inv_fact[n-r]` modulo a prime.
- **C. The multiplicative loop:** `c = c * (n - r + i) // i` for `i = 1..r`, exact integers.

For each situation, say which method you would pick and why. Then write the cost (time and memory) of each method.
Write your answer in `answer.md`.

1. `n, r <= 60`, a few thousand queries, exact answer (no modulus).
2. `n <= 10^6`, 10^5 queries, answer modulo `10^9 + 7`.
3. `n <= 2000`, many queries, answer modulo **10^9** (not a prime!). Why does method B break here?
4. One single query with `n = 10^5`, `r = 3`, exact answer.
5. `n <= 10^18`, `r <= 10^5`, modulo `10^9 + 7`. Which method? What does it cost? (Careful: what can you not tabulate?)
6. In which situation can you NOT use method B at all, and what does it need in order to work (hint: inverses)?
