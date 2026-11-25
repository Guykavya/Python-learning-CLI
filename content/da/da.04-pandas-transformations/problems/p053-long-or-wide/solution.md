## Approach

Think about who reads the table. Code reads columns, so it wants each variable in a column (long). People read grids,
so a report wants one variable spread across columns (wide). Keep the long table as the source of truth and make wide
tables at the edge, for display. Compare with `answer.md` and tick the checklist.

## Code

```python
import pandas as pd

long = pd.DataFrame({"store_id": ["S1", "S1", "S2", "S2"], "quarter": ["2024Q1", "2024Q2"] * 2,
                     "revenue": [299858, 280256, 303269, 346731]})
wide = long.pivot(index="store_id", columns="quarter", values="revenue").reset_index()
back = wide.melt(id_vars="store_id", var_name="quarter", value_name="revenue")
print(long.groupby("quarter")["revenue"].sum().to_dict())        # {'2024Q1': 603127, '2024Q2': 626987}
print(wide.drop(columns="store_id").sum().to_dict())             # the same totals, from the wide shape
print(len(back) == len(long))                                    # True: no row gained or lost
```

## Complexity

Reshaping is O(cells) plus sorting the labels. The real cost of the wrong shape is in the code: loops over column
names, and code that breaks when a new period arrives.

## Another way

Some teams keep a wide table in a spreadsheet as the "source". Then the first step of every analysis is a `melt`, and
the first check is that the melted row count equals stores × periods minus the empty cells.
