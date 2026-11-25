## Hint 1

In the leaky version, where do the 19 copies of a fraud row go when the folds are cut? In the honest version, which rows are copied?

## Hint 2

```text
oversample: pos = where(y == 1); extra = tile(pos, factor - 1); return vstack([X, X[extra]]), concatenate([y, y[extra]])
first:  Xo, yo = oversample(X, y); for tr, va in skf.split(Xo, yo): fit on (Xo[tr], yo[tr]), score Xo[va]
inside: for tr, va in skf.split(X, y): Xa, ya = oversample(X[tr], y[tr]); fit; score X[va]
```
