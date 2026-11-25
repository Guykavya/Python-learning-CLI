# Regex or plain text?

Chapter sections 4.1 and 4.5. Many characters mean something special in a pattern: `.` is "any character", `+` is "one
or more of the previous". Whether pandas treats your text as a pattern or as plain text depends on the `regex=`
argument. Both calls below run without an error, and they give different answers.

```python
import pandas as pd

s = pd.Series(["a.b", "1+1", "x2y3", "211"])
print(s.str.replace(".", "", regex=False).tolist())
print(s.str.replace(".", "", regex=True).tolist())
print(s.str.contains("1+1", regex=False).tolist())
print(s.str.contains("1+1", regex=True).tolist())
print(s.str.count(r"\d").tolist())
print(s.str.replace(r"\d", "#", regex=True).tolist())
print(int(s.str.contains(".", regex=True).sum()), int(s.str.contains(".", regex=False).sum()))
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`.

Do not run the code before you have written your answer.

## Example

For `t = pd.Series(["3.5", "35"])`, `t.str.replace(".", "", regex=False).tolist()` is `['35', '35']` (only the real dot
goes), while `t.str.replace(".", "", regex=True).tolist()` is `['', '']` (every character matches `.`).

## After you answer

- In which of the calls above does `+` mean "plus sign", and in which does it mean "one or more"?
- How would you write the pattern so that the regex version of line 2 removes only real dots?
- Which setting would you choose when the text to find comes from a user, and why?
