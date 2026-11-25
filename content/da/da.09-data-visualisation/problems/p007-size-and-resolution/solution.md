## Approach

Check the suffix first (so nothing is written for a wrong format), then call `savefig`. The default is to keep the figure's own size; `dpi` multiplies it.

## Code

```python
from pathlib import Path


def save_png(fig, path, dpi=100):
    path = Path(path)
    if path.suffix.lower() not in {".png", ".svg"}:
        raise ValueError("unsupported format")
    fig.savefig(path, dpi=dpi)
    return path
```

## Complexity

O(pixels) to render a PNG.

## Another way

`fig.savefig(path, format="png")` forces the format whatever the suffix; here the suffix is the single source of truth.
