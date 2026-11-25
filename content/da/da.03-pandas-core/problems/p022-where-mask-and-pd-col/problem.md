# `where`, `mask` and `pd.col`

Chapter section 8.5. `df[mask]` **drops** rows. `where(cond, other)` keeps the shape and replaces the cells where the
condition is **False**; `mask(cond, other)` replaces the cells where it is **True**.

Write `cap_discounts(df, cap)`: the frame keeps **all rows and columns**, but every `discount` above `cap` becomes `cap`.
Discounts at or below the cap, and missing discounts, stay as they are. Return a new frame; the input is not changed.

## Example

```python
df = pd.DataFrame({"item": ["a", "b", "c", "d"], "discount": [5.0, 30.0, None, 20.0]})
cap_discounts(df, 20)["discount"].tolist()    # [5.0, 20.0, nan, 20.0]
```
