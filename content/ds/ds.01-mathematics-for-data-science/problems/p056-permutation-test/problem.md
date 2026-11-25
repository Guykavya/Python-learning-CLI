# Permutation test

Chapter section 14.5. A **permutation test** asks: if the group labels meant nothing, how often would a random relabelling give a difference at least as large as the one observed? It needs no formula.

Write `permutation_test(a, b, reps, seed)` returning `(observed, p)`:

- `observed = mean(a) - mean(b)`;
- create `rng = np.random.default_rng(seed)`; `reps` times shuffle the **pooled** values, cut off the first `len(a)` as the new group A, the rest as B, and compute the same difference;
- count the shuffles with `|difference| >= |observed| - 1e-12` (a two-sided test);
- return `p = (count + 1) / (reps + 1)`: the observed arrangement counts as one of the possibilities, so `p` is never 0.

## Example

```text
a = [5.1, 4.9, 5.3, 5.0]   b = [4.2, 4.4, 4.0, 4.5]    ->  observed 0.8, p small (< 0.05)
two identical groups                                    ->  observed 0, p = 1
```
