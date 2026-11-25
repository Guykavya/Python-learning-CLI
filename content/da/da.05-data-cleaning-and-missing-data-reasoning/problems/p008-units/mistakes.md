- **A default factor of 1 for unknown units** (`FACTORS.get(key, 1)`). The data silently mixes units again, which is
  the very problem this step exists to solve.
- **Not normalising the unit text.** `"KG"` and `" kg "` are real spellings; compare `strip().lower()`.
- **Raising `KeyError`.** The task asks for `ValueError`, and a message naming the unit: `KeyError: 'stone'` hides the
  reason.
- **Converting grams with 1000 instead of 0.001.** 500 g is half a kilogram. Say the factor out loud: "kilograms per
  unit".
- **Treating a missing value as 0.** `nan * factor` stays `nan`; never invent a weight.
- **Comparing floats with `==` in your own tests**: `10 * 0.45359237` is `4.535923700000001`. Use `round` or `approx`.
