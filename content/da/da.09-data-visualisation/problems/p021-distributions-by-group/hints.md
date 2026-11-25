## Hint 1

Which `histplot` arguments choose the colour split, the normalisation (counts, density, share) and whether the groups are normalised together or separately? seaborn's defaults normalise all groups **together**.

## Hint 2

```text
fig, ax = plt.subplots()
sns.histplot(data=df, x="value", hue="group", stat="density", common_norm=False, ax=ax)
return fig
```
