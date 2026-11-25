## Walk-through

1. "split rows into train and test" is not in `LEARNS`: `ok`.
2. "fit scaler" learns, on `all` rows: `leak`.
3. "fit imputer" learns, on `train`: `ok`.
4. "select features" learns, on `all`: `leak`.
5. "transform test with the fitted scaler" is not in `LEARNS` (it applies, it does not learn): `ok`.
6. "oversample" learns, on `all`: `leak` (copies of the same rows land on both sides of a later split).

## Why step 5 is fine

Transforming test rows with a scaler fitted on training rows uses only what was learned from training. The test rows are only **read**, not learned from.
