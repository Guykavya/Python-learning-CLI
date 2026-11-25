# Scores and segments

Chapter sections 5.2 and 5.3. R, F and M become **scores from 1 to 5** (5 is best), and the R and F scores become a named **segment**.

Write two functions.

**`score_quantile(s, higher_is_better=True, n=5)`**: `s` is a Series. Return an int Series (same index) with scores `1..n` so that each score holds about the same number of customers. Heavy ties (most customers have exactly one order) make
`pd.qcut` fail, so **rank first**: `s.rank(method="first", ascending=higher_is_better)` and then `pd.qcut(rank, n, labels=range(1, n + 1))`. A **small** recency is good, so for recency call it with `higher_is_better=False` and the most recent customers get 5.

**`segment(r, f)`**: the first rule that applies, in this order:

| rule | label |
|---|---|
| `r >= 4 and f >= 4` | `Champions` |
| `r >= 3 and f >= 3` | `Loyal` |
| `r >= 4 and f <= 2` | `New / promising` |
| `r <= 2 and f >= 3` | `At risk` |
| `r <= 2 and f <= 2` | `Hibernating` |
| anything else | `Needs attention` |

## Example

`segment(5, 5)` is `Champions`; `segment(4, 3)` is `Loyal` (it fails the first rule and meets the second).
