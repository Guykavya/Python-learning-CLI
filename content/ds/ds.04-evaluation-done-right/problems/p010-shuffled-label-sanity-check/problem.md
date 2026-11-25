# Shuffled-label sanity check

Chapter section 4.4. Shuffle the target and run the **whole** evaluation again. With random labels no honest procedure can score better than chance (AUC 0.5). If it still scores clearly above 0.5, the procedure itself creates signal: it leaks.

Write `shuffled_label_check(evaluate, y, repeats=5, seed=0)`. `evaluate` is a function that takes a label array and returns a score (it runs the whole procedure: preprocessing, selection, cross-validation). Using **one** `rng = np.random.default_rng(seed)`, call `evaluate(rng.permutation(y))` `repeats` times and return `(mean, std)` of the scores (population std, `ddof=0`) as floats.

## Example

```text
shuffled_label_check(honest_eval, y)   ->  (0.50, 0.01)    # fine
shuffled_label_check(leaky_eval, y)    ->  (0.83, 0.02)    # the procedure leaks
```
