## Hint 1

Which Axes method draws vertical bars from names and heights? Where do the title and the y label live: on the Figure or on the Axes?

## Hint 2

```text
fig, ax = plt.subplots()
ax.bar(categories, values)
ax.set_title(title)
ax.set_ylabel(ylabel)
return fig
```
