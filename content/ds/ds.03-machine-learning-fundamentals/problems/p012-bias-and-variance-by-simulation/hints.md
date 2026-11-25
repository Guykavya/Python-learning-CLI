## Hint 1

For one fixed point, what do you get if you fit many different training sets and look at the predictions? Which spread tells you about variance, and which distance from the truth tells you about bias?

## Hint 2

```text
P = empty((reps, 19))
for r in range(reps): X, y = make_curve(n_train, noise, seed=seed + r); P[r] = poly_model(degree).fit(X, y).predict(points.reshape(-1, 1))
bias2 = mean((P.mean(axis=0) - truth(points)) ** 2)
variance = mean(P.var(axis=0))
```
