# Which comparison is fair?

Chapter section 8. Eight patients, two hospitals ("big" and "small"), a treatment given to some (`t = 1`), and a recovery score `y`.
Compare the naive difference with the differences **inside** each hospital.

```python
import pandas as pd

df = pd.DataFrame({
    "hospital": ["big", "big", "big", "big", "small", "small", "small", "small"],
    "t": [1, 0, 0, 0, 1, 1, 1, 0],
    "y": [88, 78, 80, 82, 58, 60, 62, 50],
})

naive = df[df.t == 1].y.mean() - df[df.t == 0].y.mean()
print(f"naive: {naive:.1f}")
inside = {}
for name, g in df.groupby("hospital"):
    inside[name] = g[g.t == 1].y.mean() - g[g.t == 0].y.mean()
    print(f"{name}: {inside[name]:.1f}")
weighted = sum(inside[name] * len(g) for name, g in df.groupby("hospital")) / len(df)
print(f"weighted: {weighted:.1f}")
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. (`groupby` visits the groups in alphabetical
order.)

Do not run the code before you have written your answer.

## Example

For two groups with differences 4.0 and 6.0 and sizes 2 and 6, the weighted line would be `weighted: 5.5`.

## After you answer

- Why is the naive difference negative while the treatment helps inside both hospitals?
- Which hospital gives the treatment more often, and what does that say about its patients?
