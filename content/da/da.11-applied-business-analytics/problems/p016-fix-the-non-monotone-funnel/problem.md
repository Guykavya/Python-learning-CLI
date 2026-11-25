# Fix the non-monotone funnel

Chapter sections 3.3 and 3.7. A funnel must narrow: nobody can **buy** without having **added to the cart**. But the tracking has a bug on one app version: some sessions have `purchased = True` and `added_to_cart = False`.
The function in `starter.py` counts each step column on its own, so a step can have **more sessions than the one before it** (a rate above 100%).

Fix `funnel_table(df, steps)`. It now returns a pair `(table, n_inconsistent)`:

- a session counts at a step **only if it passed every earlier step** (all earlier flags are `True` too);
- `table` has the same columns as in problem 11: `step`, `sessions`, `% of previous step`, `% of all sessions`, `dropped`, with the first row `"sessions"` (NaN in the two derived columns);
- `n_inconsistent` is the number of sessions in which some step flag is `True` although an **earlier** flag is `False`.

## Example

Steps `["viewed", "carted", "bought"]`; a session `(False, False, True)` is inconsistent and counts at no step; a session `(True, False, True)` counts at "viewed" only.
