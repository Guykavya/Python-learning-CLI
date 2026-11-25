# What does barplot draw?

Chapter section 5.3. `sns.barplot` does not draw your rows: it **aggregates** them. By default each bar is the **mean** of `y` for one category, and
the categories appear in the order of **first appearance** in the data. (We switch the interval off with `errorbar=None`.)

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

df = pd.DataFrame({
    "g": ["tea", "espresso", "tea", "pastry", "tea", "pastry"],
    "v": [2, 12, 4, 6, 6, 10],
})
fig, ax = plt.subplots()
sns.barplot(data=df, x="g", y="v", errorbar=None, ax=ax)
fig.canvas.draw()
print([round(float(p.get_height()), 2) for p in ax.patches])
print([t.get_text() for t in ax.get_xticklabels()])
print(len(ax.lines))
print(f"{df['v'].mean():.2f}")
print(f"{sum(p.get_height() for p in ax.patches) / len(ax.patches):.2f}")
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For two rows `a: 1, 3` only, the first print would show `[2.0]` (one bar, the mean of 1 and 3).

## After you answer

- The mean of the bars and the mean of the rows are different numbers. Why?
- What would be drawn on top of each bar if we had left `errorbar` at its default?
