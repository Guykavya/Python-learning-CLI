## Hint 1

Which argument of `relplot` splits the data into columns of panels? What does the default title of a panel look like, and which method of the grid changes it? Which `facet_kws` entry shares the y axis?

## Hint 2

```text
g = sns.relplot(data=df, x="week", y="revenue", col="store", col_wrap=3, kind="line", errorbar=None, facet_kws={"sharey": True})
g.set_titles("{col_name}")
return g
```
