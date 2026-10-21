- Computing `n!` and counting zeros. It works for small `n` but `10**18 !` can never be computed;
  the program runs forever.
- Counting only `n // 5`. Multiples of 25 contain two 5s, so `25` gives 5 instead of 6, and the
  error grows for larger `n`.
- Counting the 2s instead of the 5s, or taking the minimum of both after a slow loop. The 5s are
  always the limiting factor, so counting 2s gives far too many zeros.
- Starting the loop with `power = 1`: `n // 1` is `n`, which adds `n` extra zeros.
