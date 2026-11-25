# Sampling distribution of the mean

Chapter section 12.2. The **sampling distribution** of the mean is what you get by drawing many samples of size `n` and recording each sample's mean.

Write `sample_means(draw, n, reps, seed)`. `draw(rng, shape)` is a function that returns random numbers of the given `shape` using the generator `rng` (for example `lambda rng, shape: rng.exponential(2.0, shape)`). Create `rng = np.random.default_rng(seed)`, draw an array of shape `(reps, n)` and return the `reps` row means as a 1-D array.

## Example

```text
draw = lambda rng, shape: rng.exponential(2.0, shape)      # mean 2, std 2
sample_means(draw, n=16, reps=5000, seed=0).std()  ->  about 0.5 = 2 / sqrt(16)
```
