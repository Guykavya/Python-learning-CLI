# Make the data go missing

Chapter section 8.2. To understand missing data, build it. You start from a **population** where you know everything
(`edu_years`, `age`, `income`, the `make_population` of the chapter) and delete incomes by a rule. Then you can see what
each mechanism does to the average of the people who remain.

Write `simulate_missing(pop, mechanism, rate, rng)`:

- `pop`: a DataFrame with columns `edu_years`, `age` and `income` (no missing values). `rate`: the target share of
  incomes to delete (for example `0.25`). `rng`: a `numpy.random.Generator` (use only it for randomness).
- Return a **copy** of `pop` in which some values of `income` are set to `NaN`. The other columns and the index do not
  change. Each row is hidden **independently** with its own probability `p_i`:

| `mechanism` | weight `w_i` of the row | meaning |
|---|---|---|
| `"MCAR"` | 1 for everybody | a coin flip |
| `"MAR"` | 2 if `age < 40`, else 1 | people under 40 hide twice as often (a **visible** column) |
| `"MNAR"` | 5 if `income` is above the **median income of `pop`**, else 1 | high earners hide five times as often (the hidden value itself) |

- The probability of a row is `p_i = rate * w_i / mean(w)` (so the average probability is `rate`; clip it to 1).
- Draw with `rng.random(len(pop)) < p`. Any other mechanism name raises `ValueError`.
- The same seed must give the same result. Do not change `pop`.

## Example

```python
import numpy as np

pop = make_population(6000, seed=1)
out = simulate_missing(pop, "MNAR", 0.25, np.random.default_rng(7))
print(round(out["income"].isna().mean(), 2))               # close to 0.25 (here 0.26)
print(out["income"].mean() < pop["income"].mean())         # True: the high earners are the ones who vanished
```

```text
0.26
True
```

(The exact missing share varies a little with the seed; it stays within two percentage points of the target.)
