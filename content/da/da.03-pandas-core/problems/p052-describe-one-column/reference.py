import pandas as pd


def _py(x):
    return None if pd.isna(x) else float(x)


def describe_column(s):
    x = s.dropna()
    n = int(x.count())
    if n == 0:
        return {"n": 0, "missing": int(len(s)), "mean": None, "median": None, "sd": None,
                "q1": None, "q3": None, "skew": None}
    return {
        "n": n,
        "missing": int(len(s) - n),
        "mean": _py(x.mean()),
        "median": _py(x.median()),
        "sd": _py(x.std()),
        "q1": _py(x.quantile(0.25)),
        "q3": _py(x.quantile(0.75)),
        "skew": _py(x.skew()),
    }
