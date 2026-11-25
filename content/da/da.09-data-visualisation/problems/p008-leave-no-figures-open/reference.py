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
