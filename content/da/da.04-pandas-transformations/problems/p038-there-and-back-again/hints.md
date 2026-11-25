## Hint 1

Why did `to_wide` turn the whole numbers into floats (`10.0`)? What does `melt` give for the cell (S2, 2025-01), and
which two steps undo both changes on the way back?

## Hint 2

```text
to_wide:  pivot(index="store_id", columns="month", values="sales") -> reset_index -> columns.name = None
to_long:  melt(id_vars="store_id", var_name="month", value_name="sales")
          -> dropna(subset=["sales"])            (absent pairs were NaN cells)
          -> sales.astype("int64")               (NaN forced float; now none are left)
          -> sort by store_id, month -> reset_index(drop=True)
```
