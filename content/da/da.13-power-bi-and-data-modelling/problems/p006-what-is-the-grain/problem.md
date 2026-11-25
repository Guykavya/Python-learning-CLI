# What is the grain?

Chapter sections 2.2 and 3.1. The **grain** of a table says what one row means. Merging tables of different grain repeats the values of the coarser table.

```python
import pandas as pd

orders = pd.DataFrame({"OrderID": ["A", "B", "C"], "Freight": [10.0, 20.0, 30.0]})
lines = pd.DataFrame({"OrderID": ["A", "A", "A", "B", "B", "C"], "Qty": [1, 2, 3, 1, 1, 5]})
flat = lines.merge(orders, on="OrderID")
print(len(orders), len(lines), len(flat))
print(orders["Freight"].sum())
print(flat["Freight"].sum())
print(round(flat["Freight"].sum() / orders["Freight"].sum(), 2))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For a single order `D` with 4 lines and freight 8.0, the freight in the flat table would be summed as `32.0`.

## After you answer

- Which of the two freight totals is right, and why?
- Where should the freight column live in a star schema?
