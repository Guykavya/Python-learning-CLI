# DIVIDE, blanks and COALESCE

Chapter section 5.6. In DAX, "no data" is **BLANK**, which is not the same as 0. `DIVIDE(a, b)` returns BLANK when `b` is 0 or BLANK; a measure over a context with no rows returns BLANK; `COALESCE(x, 0)` replaces a BLANK by 0; `ISBLANK(x)` tests for it.

The model has two tables.

| Product: ProductKey | Category |
|---|---|
| 1 | A |
| 2 | A |
| 3 | B |

| Sales row | ProductKey | Amount | Qty |
|---|---|---|---|
| 1 | 1 | 100 | 2 |
| 2 | 2 | 50 | 1 |
| 3 | 3 | 30 | 3 |

(`Sales[ProductKey]` is related to `Product[ProductKey]`, many-to-one.) With **no filters**, evaluate these five expressions and write the results, **one per line, in order**, in `answer.txt`. Write `BLANK` for a blank result and whole numbers or plain numbers otherwise.

1. `DIVIDE(SUM(Sales[Amount]), SUM(Sales[Qty]) - SUM(Sales[Qty]))`
2. `CALCULATE(SUM(Sales[Amount]), Product[Category] = "Z")`
3. `COALESCE(CALCULATE(SUM(Sales[Amount]), Product[Category] = "Z"), 0)`
4. `IF(ISBLANK(CALCULATE(SUM(Sales[Amount]), Product[Category] = "Z")), -1, 1)`
5. `VAR t = SUM(Sales[Amount]) VAR q = SUM(Sales[Qty]) RETURN DIVIDE(t, q)`

## Example

`DIVIDE(10, 4)` is `2.5` and `DIVIDE(10, 0)` is `BLANK`.

## After you answer

- In a visual, what happens to a row whose measure is BLANK, and what happens to a row whose value is 0?
- When is it right to turn a BLANK into 0 with `COALESCE`?
