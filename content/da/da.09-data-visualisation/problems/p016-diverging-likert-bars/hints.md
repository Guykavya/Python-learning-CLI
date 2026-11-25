## Hint 1

If the neutral bar is centred on 0, where does it start? Then where does "Disagree" end, and where does "Strongly disagree" end? Work out the five left edges for one row before you write any plotting code.

## Hint 2

```text
pct = counts divided by row sums * 100
half = neutral / 2
lefts = [-(sd+d+half), -(d+half), -half, half, half+a]
for each category: ax.barh(questions, widths, left=lefts, label=category)
ax.axvline(0)
```
