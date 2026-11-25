## Hint 1

Write the seasonal-naive forecast as a small helper first. Which rows does the model see for each origin, and which columns of the future?

## Hint 2

```text
for o in origins:
    train, future = df.iloc[:o], df.iloc[o:o + horizon]
    m = model_fn(train, future.drop(columns="sales")); n = last season of train.sales repeated
    model_err.append(mean(abs(future.sales - m))); naive_err.append(mean(abs(future.sales - n)))
return mean(model_err), mean(naive_err), mean(model_err) < mean(naive_err)
```
