# The golden rule

Chapter section 2.3. **The golden rule: anything that learns from data may only learn from the training rows.** Splitting, and applying something already fitted, are fine on any rows; fitting a scaler, an imputer, a feature selector, an encoder or a model on rows that include the test set is a leak.

```python
LEARNS = {"fit scaler", "fit imputer", "select features", "target encode", "fit model", "oversample"}


def check(step, rows):
    if step not in LEARNS:
        return "ok"
    return "ok" if rows == "train" else "leak"


pipeline_steps = [
    ("split rows into train and test", "all"),
    ("fit scaler", "all"),
    ("fit imputer", "train"),
    ("select features", "all"),
    ("transform test with the fitted scaler", "test"),
    ("oversample", "all"),
]
for i, (step, rows) in enumerate(pipeline_steps, start=1):
    print(f"{i}. {step} on {rows} rows: {check(step, rows)}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For the step `("fit model", "train")` the line would be `1. fit model on train rows: ok`.

## After you answer

- Step 5 uses the **test** rows and is still `ok`. Why does the golden rule allow it?
