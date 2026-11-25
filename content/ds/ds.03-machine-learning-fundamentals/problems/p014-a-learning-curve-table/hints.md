## Hint 1

Which loop is inside which? For one size you need several fits on different random subsets before you average.

## Hint 2

```text
rng = default_rng(seed); rows = []
for n in sizes:
    tr, va = [], []
    repeat `repeats` times:
        idx = rng.choice(len(X), n, replace=False); m = make_model().fit(X[idx], y[idx])
        tr.append(rmse(y[idx], m.predict(X[idx]))); va.append(rmse(val_y, m.predict(val_X)))
    rows.append((n, mean(tr), mean(va)))
```
