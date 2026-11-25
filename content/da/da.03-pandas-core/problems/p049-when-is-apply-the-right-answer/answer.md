## Model answer

1. **What `apply` does.** `apply(f)` calls the Python function `f` **once per element** (and `apply(axis=1)` builds a whole `Series` object for every row first, which is even slower). The loop is still a Python loop, only hidden. A vectorised expression such as `prices * 1.18` runs one compiled loop over the NumPy array: no Python call, no per-row object. In the chapter, on 200,000 rows, the vectorised line took about a millisecond while `Series.apply` took tens of milliseconds and `iterrows` over a tenth of the rows took hundreds (machine-specific). The gap grows with the table.

2. **`map`.** `Series.map(dict)` is a **look-up**: replace each code by its name (city to zone). It is fast enough and clear. A key that is not in the dictionary becomes `NaN`, so count those (`isna().sum()`) or use `.fillna("Other")` so unknown codes do not vanish unnoticed.

3. **When `apply` is right.** When the logic really cannot be written column-wise: for example a **parser for a messy code** such as `"PUN-2025-0042"` with several rules and branches, or a function from a library that only accepts one value (a custom text parser, a geocoding or date library call). Then a per-row call is the honest tool. Keep it safe: first look for the `.str`, `.dt`, `where` or `np.select` version; test the function on a small slice; keep it off the hot path (run once, store the result); and check the output for missing values.

4. **Order of things to try.** (1) A vectorised expression, a `.str` or `.dt` method, `where` / `np.select` / `cut`. (2) `map` with a dictionary for look-ups. (3) `apply` for the rest. (4) A plain loop only when nothing else fits. And **measure** with a real size before and after changing anything.

**Checklist: your answer should mention**
- [ ] `apply` is a row-wise Python call; the loop is hidden, not removed
- [ ] slow on big data (per-row cost, especially `axis=1`)
- [ ] vectorised first
- [ ] `map` for look-ups; missing keys give NaN
- [ ] `apply` for complex per-row logic that cannot be vectorised
- [ ] measure, do not guess
