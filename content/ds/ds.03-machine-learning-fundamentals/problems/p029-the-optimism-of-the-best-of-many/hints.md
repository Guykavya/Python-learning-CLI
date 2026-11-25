## Hint 1

What is the accuracy of a random guesser on coin-flip labels? Where does a validation accuracy of 64% come from if nobody can predict anything?

## Hint 2

```text
rng = default_rng(seed); draw X_val, y_val, X_test, y_test; best_acc = -1
repeat n_models: w = rng.normal(size=10); acc = mean(((X_val @ w) > 0) == y_val)
    if acc > best_acc: best_acc, best_w = acc, w
test_acc = mean(((X_test @ best_w) > 0) == y_test)
```
