# Simpson's paradox detector

Chapter section 15.1. A treatment can win in **every** group and still lose **overall**, when the groups have very different sizes for the two treatments. Write `rates_by_group(rows)`. Each row is `(group, treatment, success)` with `treatment` equal to `"A"` or `"B"` and `success` a boolean.

Return a dict with three keys:

- `"groups"`: `{group: {"A": rate, "B": rate}}`, the success rate (successes / rows) of each treatment inside each group;
- `"overall"`: `{"A": rate, "B": rate}` over all rows, ignoring groups;
- `"paradox"`: `True` when **every group prefers the same treatment** (strictly higher rate) and the **overall** rates prefer the **other** treatment (strictly). Otherwise `False`.

Errors: a treatment other than `"A"` or `"B"` raises `ValueError`; a group that lacks one of the two treatments raises `ValueError` (its rate would be undefined); no rows raises `ValueError`.

## Example

The kidney-stone counts of the chapter: small stones A 81 of 87, B 234 of 270; large stones A 192 of 263, B 55 of 80.
Group rates: small A 0.931 vs B 0.867, large A 0.730 vs B 0.688, so A wins both; overall A 273/350 = 0.780 vs B 289/350 = 0.826, so B wins. `paradox` is `True`.
