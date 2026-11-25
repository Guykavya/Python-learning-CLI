# Predict label versus position

Chapter sections 2.3 and 7.1. The Series below has integer labels that are **not** in the order `0, 1, 2`.

```python
import pandas as pd

s = pd.Series([10, 20, 30], index=[2, 0, 1])

print(int(s[0]))
print(int(s.iloc[0]))
print(int(s.loc[1]))
print(int(s.iloc[-1]))
print(s.loc[[0, 1]].tolist())
try:
    print(int(s.loc[5]))
except KeyError as exc:
    print(type(exc).__name__)
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `t = pd.Series([7, 8], index=[1, 0])`, the line `print(int(t.loc[0]))` prints `8` (the row *labelled* 0) and
`print(int(t.iloc[0]))` prints `7` (the *first* row).

## After you answer

- Which of the lines would have printed something different in an old pandas tutorial for `s[0]`?
- Which line shows that `.loc` with a list follows the order you ask for, not the order of the Series?
