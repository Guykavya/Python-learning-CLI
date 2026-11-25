# TimeSeriesSplit by hand

Chapter section 7.3. `TimeSeriesSplit` makes **expanding-window** folds: each fold trains on everything up to a point and tests on the next block. Its documented algorithm for `n` rows and `n_splits` folds: the test block size is `n // (n_splits + 1)`; the test blocks are the **last** `n_splits` blocks of that size; fold `i` trains on everything before its test block, minus `gap` rows at the end.

```python
import numpy as np
from sklearn.model_selection import TimeSeriesSplit

X = np.arange(12)
for gap in (0, 1):
    print(f"gap = {gap}")
    for i, (train, test) in enumerate(TimeSeriesSplit(n_splits=3, gap=gap).split(X)):
        print(f"  fold {i}: train {train[0]}-{train[-1]}, test {test[0]}-{test[-1]}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

With 8 rows and `n_splits=3` the test size would be `8 // 4 = 2`, so the first fold would test rows 2-3 after training on rows 0-1.

## After you answer

- Why would you leave a `gap` between training and testing in a real project (think of how long it takes to know a label)?
