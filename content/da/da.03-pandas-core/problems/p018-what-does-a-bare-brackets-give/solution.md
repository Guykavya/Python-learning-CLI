## Approach

A single column name gives a Series, whose shape has one number: `(4,)`. A list of names, even a list of one, gives a DataFrame: `(4, 1)`. A slice inside brackets selects **rows** by position and stops before the end: positions 1 and 2, so `(2, 2)`. A boolean Series keeps the rows where it is True: `a > 1` is true for 2, 3 and 4, so three rows and both columns, `(3, 2)`.

## Code

The expected output is in `expected.txt`, produced by running the program.

## Complexity

Constant for the column and the slice (views); O(n) for the filter.

## Another way

For clearer code, say what you mean: `df.loc[:, "a"]` or `df.iloc[1:3]`. Bare brackets are short, and short is easy to misread.
