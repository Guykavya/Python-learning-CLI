# A business-rule baseline

Chapter section 8.3. Before a model, ask what the team would do **without** it. Often there is a rule of thumb. A rule can be scored like a model if it produces a **risk score**.

The churn team's rule gives **2 points** for a month-to-month contract and **1 point** for 3 or more support calls in the last month. Write `rule_score(X)`: `X` is a DataFrame with (at least) the columns `contract_month` (0/1) and `support_calls` (a count). Return a float NumPy array with the rule's points for each row (0, 1, 2 or 3).

## Example

```text
contract_month  support_calls   ->  score
      1              0                2
      0              4                1
      1              3                3
      0              2                0
```
With these points as scores, the rule reaches a ROC-AUC of about 0.68 on the churn data: the number a model must beat.
