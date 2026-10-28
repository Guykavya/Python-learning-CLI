- Forgetting `strip().upper()` in one of the methods. `leave("ka01")` then cannot find `KA01`.
- Letting a large car take a small spot when the large ones are full.
- Taking the most recently freed spot instead of the one with the lowest number.
- Sorting the report as text: `sorted(["S10", "S2"])` gives `["S10", "S2"]`.
- Updating `_spots` but forgetting `_where` (or the other way round) in `leave`. The two dicts then
  disagree, and a car can be "parked" in a free spot.
- `class LotFullError(Exception)` with no shared base. Callers then need three `except` clauses to
  catch "any parking problem".
- Raising `KeyError` from `leave` for an unknown plate. A `NotParkedError` tells the caller what
  really went wrong.
