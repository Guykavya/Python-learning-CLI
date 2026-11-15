1. `x * x >= 50`: `F...FT...T`. `7*7 = 49 < 50`, `8*8 = 64`. Search for the first True, which is 8.
2. `x * x <= 50`: `T...TF...F`. It is the opposite. Search the last True, which is 7.
3. `x is prime`: not monotonic. `2` True, `4` False, `5` True. A probe at a composite number tells nothing about the primes on either side.
4. Capacity `x` ships everything in `D` days: `F...FT...T`. With more capacity each day can carry at least as much, so the number of days never grows. Search the first True.
5. Digit sum at least 10: not monotonic. `19` True (1 + 9 = 10), `20` False (2), `99` True (18).
6. `ceil(1000 / x) <= 25`: `F...FT...T`. A larger `x` gives a smaller or equal ceiling. At `x = 40` it is `ceil(25) = 25`, True; at 39 it is `ceil(25.64) = 26`, False. First True is 40.
7. `x is even`: not monotonic, it alternates `F T F T ...`.

**Why monotonicity matters.** If `ok(mid)` is True in a `F...FT...T` predicate, then everything to the right of `mid` is True too, so the first True is at `mid` or to its left and the right half can be discarded.
If it is False, everything to the left is False as well and that half can be discarded. One probe thus settles half of all candidates. In a non-monotonic predicate a single answer says nothing about the other values, so no half can be thrown away and binary search can miss the answer.
