## Hint 1

`i = 0, 1`: two `a`s match `pattern[0]` and `pattern[1]`, so `k` goes 0 → 1 → 2. At `i = 2`, the text has `a`, but `pattern[2] = b`: fall back to `pi[1] = 1`, then compare `a` with `pattern[1] = a`.

## Hint 2

After `i = 5`, `k = 5`: the last five text letters `aabaa` match the pattern's first five. At `i = 6` the text has `a`, the pattern wants `pattern[5] = b`. Fall back to `pi[4]`. Then compare again.

## Hint 3

From `k = 2`, `a` against `pattern[2] = b` fails again: fall back to `pi[1] = 1`. Then `a` against `pattern[1] = a` matches. Write all three values of `k` on that line.
