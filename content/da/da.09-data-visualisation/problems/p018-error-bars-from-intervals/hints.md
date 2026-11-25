## Hint 1

You need one `(mean, half_width)` pair per group. Which `groupby` loop gives each group's values? Which argument of `ax.errorbar` takes the whisker half-lengths?

## Hint 2

```text
for name, g in df.groupby(group): m, h = mean_ci(g[value]); collect
ax.errorbar(names, means, yerr=halves, fmt="o", capsize=5)
ax.set_ylim(bottom=0)
ax.set_title("... (95% CI)")
```
