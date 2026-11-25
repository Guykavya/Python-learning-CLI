# Revenue per visitor with a bootstrap

Chapter section 2.6. **Revenue per visitor** includes all the visitors who bought nothing (revenue 0), so its distribution is very skewed: a spike at 0 and a long tail. A formula for the interval of a mean
that assumes a bell shape is shaky there. A **bootstrap** resamples the data many times and reads the interval off the results.

Write `mean_diff_ci(a, b, n_boot=2000, seed=1)`:

- `a` and `b` are the revenues of the visitors in A and in B (lists or arrays);
- draw `n_boot` bootstrap samples **with replacement** of each group (same size as the original), compute `mean(b*) - mean(a*)` for each pair, and use `numpy.random.default_rng(seed)` as the only source of randomness;
- return `(observed, (low, high))`: the observed difference `mean(b) - mean(a)` and the 2.5% and 97.5% quantiles of the bootstrap differences, all plain floats.

The same `seed` must give exactly the same answer.

## Example

If 9 of 10 visitors in A spend 0 and one spends 100, and B is the same but the buyer spends 150, the observed difference is `+5.0`, and the bootstrap interval contains it.
