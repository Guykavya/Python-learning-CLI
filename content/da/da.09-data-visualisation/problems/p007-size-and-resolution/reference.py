from pathlib import Path


def save_png(fig, path, dpi=100):
    path = Path(path)
    if path.suffix.lower() not in {".png", ".svg"}:
        raise ValueError("unsupported format")
    fig.savefig(path, dpi=dpi)
    return path
