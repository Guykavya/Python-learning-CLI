The model answer is shown when you check. The ideas that must appear:

1. The plain polynomial value grows like `B^k`: huge for long strings. Taking `% M` keeps every number small and hash computations O(1).
2. A hash maps infinitely many strings into `M` values, so different strings with the same hash (collisions) must exist. Example: with `B = 31`,
   `M = 101`, both `abc` and `ga` hash to 16.
3. About `n^2 / 2 / M = 2 * 10^10 / 10^9 = 20` colliding pairs are expected. A single modulus around 10^9 is **not** safe when you compare
   very many pairs.
4. Use a huge modulus (`2^61 - 1`: about `1 / 2 * 10^18` per pair, so with `2 * 10^10` pairs a collision is very unlikely) or double hashing
   (two independent hashes: a collision needs both: about `1 / (M1 * M2)`).
5. With `v('a') = 0` the strings `a`, `aa`, `aaa` all hash to 0.
6. With a fixed public `B` and `M` an attacker can search for colliding strings in advance. Defend with a random base picked at program start.
   If the answer must be exactly right, verify candidate matches by comparing the strings.
