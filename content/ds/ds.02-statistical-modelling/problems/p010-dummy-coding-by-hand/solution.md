## Walk-through

`set(education) - {"school"}` leaves `{"masters", "degree"}`; `sorted` gives `["degree", "masters"]`, so the dictionary keys come in the order `is_degree`, `is_masters`.

`education` is school, masters, degree, degree, school. `is_degree` is 0, 0, 1, 1, 0. `is_masters` is 0, 1, 0, 0, 0.

A row is in the baseline group when every dummy is 0: positions 0 and 4, so the count is 2.

## Another way

`pd.get_dummies(series, drop_first=True)` does this, but it drops the first level alphabetically (`degree` here), not your chosen baseline. That is why the chapter's formulas name the baseline with `Treatment(reference='school')`.
