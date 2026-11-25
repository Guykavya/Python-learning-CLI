# Same features in training and serving

Chapter section 14. **Training-serving skew** happens when the features computed for training differ from those computed when the model serves one customer at a time: a different clipping, a different column order, a one-hot column that only exists when a category happens to be present in the batch. The fix is **one function** used by both.

Write `build_features(raw)` that turns a DataFrame of raw columns (`tenure_months`, `monthly_charge`, `support_calls`, `contract`, `autopay`) into model features. Return a DataFrame with **the same index** as `raw` and exactly these columns, in this order:

| column | value |
|---|---|
| `tenure_months` | `tenure_months` clipped to `[1, 72]` |
| `charge_per_call` | `monthly_charge / (1 + support_calls)` |
| `contract_month` | 1 if `contract == "month"` else 0 |
| `contract_year` | 1 if `contract == "year"` else 0 |
| `contract_two_year` | 1 if `contract == "two_year"` else 0 |
| `autopay` | `autopay` as an integer |

An unknown contract value (say `"weekly"`) gives 0 in all three contract columns. Do not modify `raw`. Do **not** use `pd.get_dummies` on the batch: its columns depend on which categories happen to appear.

## Example

```text
build_features(one_row_with_contract_year)   ->  contract_month 0, contract_year 1, contract_two_year 0
build_features(batch).iloc[[i]]  equals  build_features(batch.iloc[[i]])   for every row i
```
