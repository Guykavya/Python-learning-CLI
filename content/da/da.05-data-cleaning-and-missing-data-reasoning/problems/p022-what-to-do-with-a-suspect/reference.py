import pandas as pd


def outlier_strategies(s, flags):
    q1, q3 = s.quantile([0.25, 0.75])
    lo, hi = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    flags = flags.fillna(False).astype(bool)

    def stat(x):
        return {"mean": float(x.mean()), "median": float(x.median())}

    out = {
        "keep": stat(s),
        "remove": stat(s[~flags]),
        "cap": stat(s.where(~flags, s.clip(lo, hi))),
        "flag_only": stat(s),
    }
    out["flag_only"]["n_flagged"] = int(flags.sum())
    return out
