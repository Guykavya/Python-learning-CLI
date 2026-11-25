# Features and target from a table

Chapter section 2. A supervised problem has a matrix of **features** `X` (one row per example, one column per input) and a **target** `y` (the answer). Tables usually keep them together.

Write `split_xy(df, target)` returning `(X, y)`:

- `X`: a DataFrame with every column **except** the target, in the original order
- `y`: the target column, as a Series
- if `target` is not a column, raise `KeyError` with a message that contains the missing name **and** the list of existing columns
- the original DataFrame must stay unchanged, and changing `X` afterwards must not change `df`

## Example

```text
df columns: area, rooms, price
split_xy(df, "price")   ->  X with columns [area, rooms], y = the price column
split_xy(df, "cost")    ->  KeyError: "target column 'cost' not found; columns are ['area', 'rooms', 'price']"
```
