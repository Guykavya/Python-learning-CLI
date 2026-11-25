## Hint 1

Which seaborn function combines the scatter and the fitted line? Which argument removes the shaded band? After you draw, where does the line live: in `ax.lines` or in `ax.collections`?

## Hint 2

```text
fig, ax = plt.subplots()
sns.regplot(data=df, x="x", y="y", ci=None, ax=ax)
ax.set_xlabel("x"); ax.set_ylabel("y")
return fig
```
