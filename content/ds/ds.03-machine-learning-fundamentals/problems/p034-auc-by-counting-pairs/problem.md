# AUC by counting pairs

Chapter section 12. The **AUC** is the probability that a randomly chosen positive row gets a **higher score** than a randomly chosen negative row (a tie counts as half):

```text
AUC = ( #pairs with score_pos > score_neg  +  0.5 * #pairs with score_pos == score_neg ) / (n_pos * n_neg)
```

Comparing every positive with every negative needs `n_pos * n_neg` comparisons and a matrix of that size: for 60,000 rows that is about 900 million cells, more memory than the test machine allows. Use **ranks** instead:

```text
AUC = ( sum of the ranks of the positive rows  -  n_pos * (n_pos + 1) / 2 ) / (n_pos * n_neg)
```

where the rank is the position of the score in the sorted order, 1 for the smallest, with tied scores sharing the **average** of their positions.

Write `auc_by_pairs(y, score)` (the name is the chapter's) returning the AUC as a float, in `O(n log n)`. `y` has values 0 and 1. If `y` contains only one class, raise `ValueError("AUC needs both classes")`. You may use `scipy.stats.rankdata` or write the ranking yourself.

## Example

```text
y = [0, 0, 1, 1]; score = [0.1, 0.4, 0.35, 0.8]   ->  0.75
y = [0, 1];       score = [0.5, 0.5]                ->  0.5    # a tie counts as half
```
