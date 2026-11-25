## Hint 1

Which rows do you drop and how do you sort? `barh` draws the first row at the bottom. The error bar needs the distance from the estimate to each end of the interval.

## Hint 2

```text
s = summary.drop(index=[...]).sort_values("estimate")
ax.barh(s.index, s["estimate"])
ax.errorbar(s["estimate"], range(len(s)), xerr=[s["estimate"] - s["CI low"], s["CI high"] - s["estimate"]], fmt="none")
ax.axvline(0); ax.set_xlabel(...); ax.set_title(f"{s.index[-1]} explains {s['estimate'].iloc[-1]:.1f} of the {total:.1f}-point rise", loc="left")
```
