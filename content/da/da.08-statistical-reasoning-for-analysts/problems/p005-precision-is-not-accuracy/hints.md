## Hint 1

Which three numbers do you compute from the same list: the average error, the spread around the average, the typical size of the error? Which `ddof` makes the identity `rmse^2 = bias^2 + sd^2` exact?

## Hint 2

```text
e = np.asarray(estimates, float)
bias = e.mean() - truth ; sd = e.std() (ddof=0) ; rmse = sqrt(mean((e - truth) ** 2))
```
