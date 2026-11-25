## Approach

Table of the Series: label 2 holds 10, label 0 holds 20, label 1 holds 30.

- `s[0]` is a label lookup: 20.
- `s.iloc[0]` is the first row: 10.
- `s.loc[1]` is the row named 1: 30.
- `s.iloc[-1]` is the last row: 30.
- `s.loc[[0, 1]]` takes labels 0 and 1 in the order given: `[20, 30]`.
- `s.loc[5]` has no such label: `KeyError`, and the `except` prints only the class name.

## Code

The expected output is in `expected.txt`, produced by running the program.

## Complexity

Every lookup here is O(1) (the list lookup is O(k) for k labels).

## Another way

Print `s.index.tolist()` first: seeing `[2, 0, 1]` makes the trap obvious.
