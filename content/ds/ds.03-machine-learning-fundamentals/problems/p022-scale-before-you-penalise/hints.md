## Hint 1

What does `make_pipeline` return, and in which order do the steps run when you call `fit`? What does the scaler learn from the data, and from which rows?

## Hint 2

`make_pipeline(StandardScaler(), Ridge(alpha=alpha))`: the two steps in that order.
