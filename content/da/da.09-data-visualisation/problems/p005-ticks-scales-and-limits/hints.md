## Hint 1

Which Axes methods set the lower limit and the scale? And which object turns a tick value into text: a `Formatter`. Which one wraps a function of `(value, position)`?

## Hint 2

```text
fig, ax = plt.subplots()
ax.plot(df["month"], df["revenue"])
if log: ax.set_yscale("log")
else:   ax.set_ylim(bottom=0)
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, pos: f"{v:,.0f}"))
ax.set_ylabel("Revenue (USD)")
return fig
```
