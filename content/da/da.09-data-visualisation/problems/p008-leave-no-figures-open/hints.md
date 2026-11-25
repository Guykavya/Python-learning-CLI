## Hint 1

Which function removes a figure from matplotlib's global list? Where must the call be so that it also runs when an error is raised inside the loop?

## Hint 2

```text
for name, df in frames.items():
    fig, ax = plt.subplots()
    try:
        ax.bar(df["label"], df["value"])
        fig.savefig(path)
    finally:
        plt.close(fig)
```
