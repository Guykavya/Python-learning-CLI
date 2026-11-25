# Scale before you penalise

Chapter section 8.2. The ridge penalty adds up **squared coefficients**. A feature measured in thousands has a tiny coefficient and is barely penalised; a feature measured in fractions has a large coefficient and is shrunk hard. The penalty then depends on the **units**, not on how useful the features are.

Write `ridge_pipeline(alpha)` returning an **unfitted** scikit-learn `Pipeline` made with `make_pipeline(StandardScaler(), Ridge(alpha=alpha))`: standardise every feature, then fit ridge.

## Example

```text
data: two features with the SAME effect per standard deviation; one measured in units of 1000, one in units of 1
Ridge(alpha=2000) alone:   standardised coefficients 2.7 and 0.3    (very unequal)
ridge_pipeline(2000):      standardised coefficients 0.25 and 0.27  (equal)
```
