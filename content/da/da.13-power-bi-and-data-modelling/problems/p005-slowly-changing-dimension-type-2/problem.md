# Slowly changing dimension, type 2

Chapter section 3.6. A customer moves from the North region to the South on 1 July 2024. If you **overwrite** the region (type 1), every old order is suddenly attributed to the South and the history of the North is wrong. A **type 2** dimension keeps **both versions**: the old row is closed, a new row with a **new surrogate key** is added, and each fact row points to the version that was valid on its date. Power BI cannot run offline; this problem is about the model and its numbers, which we build and check in pandas.

The dimension `dim` has the columns `SurrogateKey` (int), `CustomerID` (the natural key), `Region`, `ValidFrom`, `ValidTo` (timestamps) and `IsCurrent` (bool); the current row has `ValidTo = 2999-12-31`.

Write two functions.

**`scd2_apply(dim, changes, as_of)`**: `changes` has `CustomerID` and `Region` (the new values valid from `as_of`). Return a **new** DataFrame (never modify `dim`), sorted by `SurrogateKey`:

- for a customer whose **current** region differs from the change: close the current row (`ValidTo = as_of - 1 day`, `IsCurrent = False`) and add a new row with `SurrogateKey = max + 1` (continuing for each added row, in the order of `changes`), `ValidFrom = as_of`, `ValidTo = 2999-12-31`, `IsCurrent = True`;
- a customer whose region is **unchanged**: nothing happens;
- a customer **not in `dim`** at all: a new row with `ValidFrom = as_of` (no old row to close).

**`lookup_key(dim, customer_id, date)`**: the `SurrogateKey` of the version with `ValidFrom <= date <= ValidTo`; if there is none, raise `ValueError("no version valid on that date")`.

## Example

Customer `C1` is in the North since 2020 (key 1). `scd2_apply(dim, [C1 -> South], 2024-07-01)` closes key 1 on 2024-06-30 and adds key 2 (South, valid from 2024-07-01). `lookup_key(dim, "C1", "2024-03-01")` is 1; on 2024-07-01 it is 2.
