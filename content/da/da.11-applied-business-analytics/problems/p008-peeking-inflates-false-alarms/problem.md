# Peeking inflates false alarms

Chapter section 2.8. A test is planned for 14 days, but every morning someone looks at the dashboard and stops "as soon as it is significant". Each look is another chance to see a false alarm.
Simulate it. **Both groups have the same true conversion rate `p`**, so every "significant" result is a false positive.

Write `peeking_simulation(n_sims=400, n_per_group=3000, looks=14, p=0.06, seed=3)` that returns `(fixed_rate, peeking_rate)`:

- in each simulation draw `n_per_group` Bernoulli(`p`) visitors for A and for B (use `numpy.random.default_rng(seed)` as the only source of randomness);
- `per_look = n_per_group // looks`; the `k`-th look uses the first `per_look * k` visitors of each group (`k = 1 .. looks`);
- at each look compute `z = (kB - kA) / n / sqrt(pp (1 - pp) * 2 / n)` with `n = per_look * k` and `pp = (kA + kB) / (2 n)` (use 0 when `pp` is 0 or 1) and call the look significant when `|z| > 1.96`;
- `fixed_rate`: the share of simulations in which the **last** look is significant (one look at the planned end);
- `peeking_rate`: the share in which **any** look is significant.

## Example

`peeking_simulation(looks=1)` gives two equal numbers near 0.05. With `looks=14` the second number is several times larger.
