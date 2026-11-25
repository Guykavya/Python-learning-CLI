# Four kinds of rank

Chapter section 14.3. `rank()` turns values into positions, 1 for the smallest. When two values are **tied** there is
no single right answer, so `method=` chooses how ties are ranked: `average` (the mean of the positions they share),
`min` (the lowest of them), `max` (the highest), `dense` (no gaps after a tie) and `first` (the first one that appears
in the data gets the lower rank).

```python
import pandas as pd

s = pd.Series([3, 1, 3, 2])
for method in ["average", "min", "dense", "first"]:
    print(method, s.rank(method=method).tolist())

t = pd.Series([30, 10, 30, 20, 10])
print(t.rank(method="max").tolist())
print(t.rank(method="min", ascending=False).tolist())
print(str(s.rank().dtype), str(s.rank(method="first").dtype))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Ranks are printed as floats,
exactly as pandas returns them (`3.0`, not `3`).

Do not run the code before you have written your answer.

## Example

For `pd.Series([5, 5, 9]).rank(method="min").tolist()` the program would print `[1.0, 1.0, 3.0]`: both fives share
position 1 and 2, `min` gives them 1, and the 9 is third.

## After you answer

- In `s`, which methods agree, and which two differ from all the others?
- A sports table gives two athletes the same time and then says the next athlete is third, not second. Which `method` is that?
