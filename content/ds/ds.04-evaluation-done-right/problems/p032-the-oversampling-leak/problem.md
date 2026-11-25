# The oversampling leak

Chapter section 9.4. **Random oversampling** copies rare-class rows to balance the classes. Done **before** cross-validation, copies of the same row land in training and validation folds, and a flexible model recognises them: the score is far too good. Done **inside** each training fold, the validation folds stay untouched.

Write three functions:

- `oversample(X, y, factor)`: return `(X_new, y_new)` with every positive row (`y == 1`) appearing `factor` times in total: the original rows first, then `factor - 1` extra copies of all positives (`np.tile` of their positions), as in the chapter
- `cv_oversample_first(make_model, X, y, factor, seed=0)`: oversample the **whole** data, then cross-validate (the leak)
- `cv_oversample_inside(make_model, X, y, factor, seed=0)`: cross-validate the original data and oversample **only the training part** of each fold

Both CV functions use `StratifiedKFold(5, shuffle=True, random_state=seed)` on the data they split, build a fresh model with `make_model()` per fold, and return the mean ROC-AUC on the validation folds (from `predict_proba(...)[:, 1]`). `X` is a NumPy array, `y` 0/1.

## Example

```text
make_fraud(20000) (about 0.9% fraud), a full-depth decision tree, factor 20:
cv_oversample_first  ->  0.995      # it recognises the copies
cv_oversample_inside ->  0.54       # the honest number for this model
```
