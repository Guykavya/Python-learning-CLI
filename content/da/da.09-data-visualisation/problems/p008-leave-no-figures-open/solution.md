## Approach

Create each figure, use it inside `try`, and close it in `finally`. `finally` runs on success and on error, so a failure in the middle of the loop cannot leave
its figure behind. Figures finished earlier were already closed in their own iteration.

## Code

```python
from pathlib import Path

import matplotlib.pyplot as plt


def render_all(frames, folder):
    folder = Path(folder)
    saved = []
    for name, df in frames.items():
        fig, ax = plt.subplots()
        try:
            ax.bar(df["label"], df["value"])
            ax.set_title(name)
            path = folder / f"{name}.png"
            fig.savefig(path)
            saved.append(path)
        finally:
            plt.close(fig)
    return saved
```

## Complexity

O(total bars); memory stays at one figure at a time.

## Another way

`matplotlib.figure.Figure()` (not created through pyplot) is never registered in the global list, so it needs no `close`; you then attach a canvas
with `FigureCanvasAgg(fig)` to save it. That is the cleanest choice inside a web server.
