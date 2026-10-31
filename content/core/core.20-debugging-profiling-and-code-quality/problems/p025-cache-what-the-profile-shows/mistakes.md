- **Putting `@cache` on `ways`.** `ways(10, [1, 5])` then raises `TypeError: unhashable type:
  'list'`, and even with a tuple it would only cache the top-level answer, not the thousands of
  repeated inner calls.
- **Keeping the coins in a global and caching `count(amount, i)`.** The cache key no longer says
  which coins were used, so the second coin list gets the first list's answers.
- **Writing your own `memo = {}` at module level keyed by `(amount, i)`.** Same problem, plus the
  dictionary is never cleared. If you write your own memo, key it by all inputs.
- **Caching a function that is not pure.** A cache returns the old answer without running the
  body, so any printing, counting or randomness inside is skipped on hits.
- **`lru_cache(maxsize=10)`.** A tiny cache keeps throwing answers away and the recursion
  recomputes them; use `maxsize=None` (or `cache`) when the set of questions is bounded.
- **Guessing instead of profiling.** The profile line `74809/1` is the proof that the same calls
  repeat; after the fix, profile again to see the count drop.
