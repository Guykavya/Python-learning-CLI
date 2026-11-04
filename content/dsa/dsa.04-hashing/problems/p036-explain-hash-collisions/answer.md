**1. Why a modulus.** The exact polynomial `v0 * B^(k-1) + ... + v(k-1)` has about `k * log2(B)` bits: thousands of digits for a long string, so each
operation would cost O(k), not O(1). Working modulo `M` keeps every value below `M`, so all the arithmetic is constant time.

**2. Why collisions exist.** There are infinitely many strings and only `M` hash values, so by the pigeonhole principle different strings must share
hashes. With `B = 31`, `M = 101` the words `abc` and `ga` both hash to 16: `(1*31 + 2)*31 + 3 = 1026 = 16 (mod 101)` and `7*31 + 1 = 218 = 16 (mod 101)`.
A hash match therefore only **suggests** equality.

**3. How many collisions?** `n = 200000` gives about `n^2 / 2 = 2 * 10^10` pairs. If each pair collides with probability about `1 / M = 10^-9`, we expect
about 20 colliding pairs. So one modulus near 10^9 is not safe when comparing that many pairs (the birthday effect).

**4. The fix.** Use a much larger modulus such as `2^61 - 1` (about `4 * 10^-19` per pair, so with `2 * 10^10` pairs the chance of any collision is about
10^-8), or use **double hashing**: two independent `(B, M)` pairs, which needs both to collide, probability about `1 / (M1 * M2)`.

**5. Letter values.** If `v('a') = 0`, then `a`, `aa`, `aaa` all give 0, because the zeros never change the running value: different strings share a hash for
trivial reasons. Letters must map to 1 or more.

**6. Attacks.** If `B` and `M` are public, someone can compute in advance two different strings with equal hash (for example by a birthday search or a lattice
trick) and feed them as input. Defend by picking `B` randomly when the program starts, and, if a wrong answer is not acceptable, compare the actual strings
after a hash match (which costs O(length) only for real matches or rare collisions).
