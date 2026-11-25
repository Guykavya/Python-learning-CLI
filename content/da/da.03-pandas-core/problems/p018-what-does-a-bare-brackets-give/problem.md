# What does a bare `[]` give?

Chapter section 7.5. Square brackets on a DataFrame do four different jobs, depending on what is inside. The result may be
a Series (one-dimensional) or a DataFrame (two-dimensional).

```python
import pandas as pd

df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [5, 6, 7, 8]})

for x in [df["a"], df[["a"]], df[1:3], df[df["a"] > 1]]:
    print(type(x).__name__, x.shape)
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `t = pd.DataFrame({"p": [1, 2], "q": [3, 4]})`, `type(t["p"]).__name__` is `Series` with shape `(2,)` and
`type(t[["p"]]).__name__` is `DataFrame` with shape `(2, 1)`.

## After you answer

- What is the difference between `df["a"]` and `df[["a"]]`, and when does it matter?
- Is `df[1:3]` a selection of columns or of rows? Which positions does it keep?
