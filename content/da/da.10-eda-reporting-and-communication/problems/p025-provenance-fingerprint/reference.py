import hashlib

import pandas as pd


def fingerprint(df):
    return hashlib.sha256(pd.util.hash_pandas_object(df, index=False).to_numpy().tobytes()).hexdigest()[:10]


def provenance(frames, analysis_date, date_col="week"):
    dates = [f[date_col] for f in frames.values() if date_col in f.columns]
    return {"rows": {k: int(len(v)) for k, v in frames.items()},
            "fingerprints": {k: fingerprint(v) for k, v in frames.items()},
            "date_from": str(min(d.min() for d in dates).date()) if dates else None,
            "date_to": str(max(d.max() for d in dates).date()) if dates else None,
            "analysis_date": analysis_date}
