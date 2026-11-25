- **`str.split("-")` instead of a pattern.** It accepts `EL-24-0042` and `X-Y-Z-W` without a word of warning.
- **`astype(int)` with missing values.** Raises an error (`NaN` is not an integer). Use `"Int64"`.
- **Unnamed groups.** `extract(r"([A-Z]{2})-...")` gives columns `0`, `1`, `2`. Named groups give the names the task
  asks for.
- **Forgetting the anchors.** `extract` searches *inside* the text; `AAEL-2024-0042` would give `EL`.
- **Converting before stripping or before the extract.** `to_numeric` on the whole code fails; extract first.
- **A half-filled row** when only one group fails. A pattern with all three groups either matches or gives all `NaN`.
- **Leaving `number` as text** (`"0042"`). The task wants the integer 42.
