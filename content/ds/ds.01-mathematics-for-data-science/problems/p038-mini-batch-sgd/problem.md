# Mini-batch SGD

Chapter section 8.6. **Stochastic gradient descent** uses the gradient of a small random batch instead of the whole data set, so each step is cheap. One pass through all the data is an **epoch**: shuffle the rows, cut them into batches, and take one step per batch.

Write `sgd(X, y, lr, epochs, batch, seed)` for the mean squared error. `X` already includes an intercept column. Start from zero weights, create `rng = np.random.default_rng(seed)`, and in each epoch draw `order = rng.permutation(n)`, then go through `order` in chunks of `batch` rows (the last chunk may be smaller) with the gradient `(2/m) X_b^T (X_b w - y_b)` where `m` is the chunk size. Return the final weights.

The same `seed` must give the same result.

## Example

```text
n = 200 rows, batch = 20, epochs = 30  ->  200 / 20 * 30 = 300 weight updates
```
