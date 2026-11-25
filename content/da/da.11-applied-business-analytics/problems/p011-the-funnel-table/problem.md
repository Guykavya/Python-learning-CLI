# The funnel table

Chapter section 3.3. A **funnel** follows sessions through ordered steps: viewed a product, added to cart, started checkout, purchased. `df` has one row per session and one boolean column per step.

Write `funnel_table(df, steps)` that returns a DataFrame with **exactly** these columns, in this order, and one row for each of `"sessions"` followed by the steps in the given order:

| column | meaning |
|---|---|
| `step` | `"sessions"` for the first row, then the step names |
| `sessions` | number of sessions: all rows for the first row; the number of `True` in the column for a step |
| `% of previous step` | `sessions / sessions of the row above * 100`; `NaN` in the first row |
| `% of all sessions` | `sessions / number of all sessions * 100` (100.0 in the first row) |
| `dropped` | sessions of the row above minus this row's sessions; `NaN` in the first row |

Index `0, 1, 2, ...`. An empty `df` is not expected.

## Example

10 sessions, 6 viewed, 3 added to cart, 1 purchased (`steps = ["viewed", "carted", "bought"]`): the rows are `sessions 10`, `viewed 6` (60.0 of previous, 60.0 of all, 4 dropped), `carted 3` (50.0, 30.0, 3), `bought 1` (33.3, 10.0, 2).
