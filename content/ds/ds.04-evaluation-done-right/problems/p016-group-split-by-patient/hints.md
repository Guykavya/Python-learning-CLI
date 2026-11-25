## Hint 1

`GroupShuffleSplit.split(X, y, groups)` is a generator. How do you take its first (and only) item?

## Hint 2

`train, test = next(GroupShuffleSplit(1, test_size=test_frac, random_state=seed).split(df, groups=df[group_col]))`, then sort both.
