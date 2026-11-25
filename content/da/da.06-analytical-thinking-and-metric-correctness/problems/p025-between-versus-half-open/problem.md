# between versus half-open

Chapter section 8.2. `Series.between(a, b)` is a **closed** interval: both ends are included. A date text such as
`"2025-02-28"` means **midnight at the start** of that day. Read the program, hand-trace it, and write **every line it
prints**, in order, in `answer.txt`.

```python
import pandas as pd

t = pd.Series(pd.to_datetime([
    "2025-02-01 00:00:00",
    "2025-02-14 10:00:00",
    "2025-02-28 00:00:00",
    "2025-02-28 15:30:00",
    "2025-02-28 23:59:59.500",
    "2025-03-01 00:00:00",
], format="ISO8601"))

closed = t.between("2025-02-01", "2025-02-28")
half_open = (t >= "2025-02-01") & (t < "2025-03-01")
print(closed.tolist())
print(half_open.tolist())
print(int(closed.sum()), int(half_open.sum()))
print(t[half_open & ~closed].dt.strftime("%d %H:%M:%S").tolist())
last_day = (t >= "2025-02-28") & (t < "2025-03-01")
print(int(last_day.sum()), int((last_day & closed).sum()))
print(int(t.between("2025-02-01", "2025-03-01").sum()))
```

Write the lines exactly as Python prints them (`True`, lists with brackets, quotes around texts).
`%S` of `strftime` prints whole seconds only (it drops the `.5`).

Do not run the code before you have written your answer.

## Example

For `u = pd.Series(pd.to_datetime(["2025-02-28 00:00:00", "2025-02-28 12:00:00"]))`, the line
`print(u.between("2025-02-01", "2025-02-28").tolist())` prints `[True, False]`: midnight equals the end, so it is in;
noon is later than the end, so it is out.

## After you answer

- Which two timestamps does the closed interval lose, and what do they have in common?
- Why is the timestamp `2025-02-28 00:00:00` counted by **both** methods, and `2025-03-01 00:00:00` by neither of the first two?
- What does the last line show about the closed interval `between("2025-02-01", "2025-03-01")`?
