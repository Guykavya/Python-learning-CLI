## Hint 1

What are the shapes of the arrays that `learning_curve` returns, and over which axis do you average? Which two positions of the gap do you compare?

## Hint 2

```text
sizes, tr, va = learning_curve(model, X, y, train_sizes=[...], cv=KFold(5, shuffle=True, random_state=seed), scoring=...)
train = -tr.mean(axis=1); val = -va.mean(axis=1); gap = val - train
gap_last = gap[-1]; rel = gap_last / val[-1]; high = rel > 0.15; helps = high and gap[-1] < gap[2]
```
