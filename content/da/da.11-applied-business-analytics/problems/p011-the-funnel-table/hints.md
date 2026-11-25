## Hint 1

Keep a running "previous" count. In each step, the number is `df[step].sum()`. What are the first row's values for the two derived columns that need a previous row?

## Hint 2

```text
n = len(df); rows = [("sessions", n, nan, 100.0)]; prev = n
for s in steps: k = int(df[s].sum()); rows.append((s, k, k/prev*100, k/n*100)); prev = k
t = DataFrame(rows, columns=[...]); t["dropped"] = t["sessions"].shift(1) - t["sessions"]
```
