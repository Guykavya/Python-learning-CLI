from pathlib import Path

import pandas as pd


def combine_folder(folder):
    frames, cols = [], None
    for f in sorted(Path(folder).glob("*.csv")):
        if f.stat().st_size == 0:
            continue
        d = pd.read_csv(f, dtype=str, keep_default_na=False)
        d = d[~(d == d.columns).all(axis=1)]
        if cols is None:
            cols = list(d.columns)
        elif set(d.columns) != set(cols):
            raise ValueError(f"columns differ in {f.name}")
        d = d[cols].assign(source=f.name)
        frames.append(d)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
