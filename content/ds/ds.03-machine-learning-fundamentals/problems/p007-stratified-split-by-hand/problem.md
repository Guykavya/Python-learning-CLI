# Stratified split by hand

Chapter section 4. With imbalanced classes a random split can put almost no rare cases in the test set. A **stratified** split keeps each class's share the same in both sets.

Write `stratified_split(y, test_frac, seed)` returning `(train_idx, test_idx)`, two **sorted** integer index arrays:

- for every class `c` with `m` rows, the number of its rows in the test set is `round(test_frac * m)`, then adjusted to be **at least 1 and at most m - 1** when the class has 2 or more rows (a class never disappears from either set); a class with exactly 1 row goes to the training set
- inside each class, which rows go to the test set is chosen at random with `np.random.default_rng(seed)`; use **one** generator for the whole function, visiting classes in sorted order
- every index appears exactly once in `train_idx` or `test_idx`
- the same seed gives the same result

## Example

```text
y = [0]*90 + [1]*7 + [2]*3, test_frac = 0.2, seed = 0
test counts per class: class 0 -> 18, class 1 -> 1 (round(1.4)), class 2 -> 1 (round(0.6))
```
