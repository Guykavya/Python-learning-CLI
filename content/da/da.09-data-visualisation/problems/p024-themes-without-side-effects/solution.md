## Approach

Matplotlib reads `rcParams` when it creates the Figure and its text and grid artists. If we create them inside the `with` block, they keep the whitegrid and talk settings, and the block restores the
old `rcParams` when it exits. `sns.set_theme` has no "undo".

## Code

```python
import matplotlib.pyplot as plt
import seaborn as sns


def themed_chart(df):
    with sns.axes_style("whitegrid"), sns.plotting_context("talk"):
        fig, ax = plt.subplots()
        ax.bar(df["label"], df["value"])
        ax.set_title("Value by label")
    return fig
```

## Complexity

O(n).

## Another way

`matplotlib.rc_context({...})` does the same for plain matplotlib settings, with the keys you choose.
