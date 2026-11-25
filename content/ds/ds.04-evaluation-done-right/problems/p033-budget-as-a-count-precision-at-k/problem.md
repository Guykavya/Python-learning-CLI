# Budget as a count: precision at k

Chapter section 10.8. Often the business does not set a threshold but a **capacity**: "the team can phone 200 customers this week". Then take the top `k` by score and report **precision at k** (share of real positives among them) and **recall at k** (share of all positives that they contain).

Write `at_k(y, score, k)` returning `(precision, recall)` as floats:

- the top `k` rows are the `k` highest scores; **ties are broken by original order** (earlier rows first): use `np.argsort(-score, kind="stable")`
- `k` must satisfy `1 <= k <= len(y)`, otherwise `ValueError`
- if there are no positives at all, recall is `0.0`

## Example

```text
y     = [1, 0, 1, 0, 0, 1]
score = [0.9, 0.8, 0.8, 0.3, 0.2, 0.1]
at_k(y, score, 2)  ->  (0.5, 0.333...)    # rows 0 and 1 (row 1 comes before row 2 on the tie)
at_k(y, score, 3)  ->  (0.667, 0.667)
```
