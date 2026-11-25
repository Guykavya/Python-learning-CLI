# Patch one table with another

Chapter section 7.4. The customer table `old` has some wrong or missing cities and segments. The support team sends a
small table `fixes` with corrections. Both have a `customer_id` column plus some of the columns `city` and `segment`.

Write `patch_customers(old, fixes)` that returns the corrected customer table:

- where `fixes` has a value for a customer and column, **the fix wins**;
- where a fix cell is missing (`None`/`NaN`), the old value stays: a missing fix never erases a value;
- the result has exactly the rows of `old`, in the same order, and exactly the columns of `old`, in the same order,
  with a fresh index `0, 1, 2, ...`. A fix for a `customer_id` that is not in `old` is ignored, and so is a column that
  `old` does not have;
- neither input is changed.

## Example

```python
import pandas as pd

old = pd.DataFrame({"customer_id": ["C1", "C2", "C3"],
                    "city": ["Pune", None, "Agra"],
                    "segment": ["retail", "retail", "premium"]})
fixes = pd.DataFrame({"customer_id": ["C2", "C3", "C9"],
                      "city": ["Delhi", None, "Surat"],
                      "segment": [None, "business", "retail"]})
out = patch_customers(old, fixes)
print(out.values.tolist())
```
```text
[['C1', 'Pune', 'retail'], ['C2', 'Delhi', 'retail'], ['C3', 'Agra', 'business']]
```

`C2` gets its missing city from the fix but keeps its segment (the fix has none); `C3` keeps Agra but gets the new
segment; `C9` is not a customer, so it is ignored.
