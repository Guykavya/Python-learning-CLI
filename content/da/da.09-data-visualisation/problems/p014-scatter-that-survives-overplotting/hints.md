## Hint 1

Which two arguments of `ax.scatter` control how opaque and how big the dots are? What number of rows decides which setting to use?

## Hint 2

```text
n = len(df)
if n > 2000: alpha, size = 0.2, 6
else:        alpha, size = 0.8, 30
ax.scatter(df["x"], df["y"], s=size, alpha=alpha)
ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
```
