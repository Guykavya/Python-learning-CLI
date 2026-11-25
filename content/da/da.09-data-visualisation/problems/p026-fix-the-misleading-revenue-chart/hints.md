## Hint 1

Go through the four faults one by one. Which row selection hides most of the data? Which line sets the bottom of the axis? What is missing from the y label? What number does the title need?

## Hint 2

```text
first, last = df["revenue"].iloc[0], df["revenue"].iloc[-1]
pct = round(abs(last / first - 1) * 100); word = "grew" if last >= first else "fell"
ax.plot(df["date"], df["revenue"]); ax.set_ylim(bottom=0)
ax.set_ylabel("Revenue (USD)"); ax.set_title(f"Revenue {word} {pct}% from {first_month} to {last_month}")
```
