# Add two months that do not match

Chapter sections 2.4 and 4.3. Arithmetic between two Series **aligns on labels**. A label found in only one of
them gives `NaN`, and the integers turn into floats.

`january` and `february` are Series of units sold, indexed by product name. Some products were sold in only one month.

Write `combine_months(a, b)` that returns the total units per product over both months:

- a product missing from one month counts as 0 for that month;
- the result is sorted by label (product name);
- the result has an **integer** dtype (`int64`), not float, and no missing values;
- the inputs are not changed.

## Example

```python
import pandas as pd

jan = pd.Series([5, 3], index=["tea", "milk"])
feb = pd.Series([4, 2], index=["milk", "rice"])
combine_months(jan, feb).to_dict()   # {"milk": 7, "rice": 2, "tea": 5}
```

`jan + feb` would give `milk 7.0, rice NaN, tea NaN`.
