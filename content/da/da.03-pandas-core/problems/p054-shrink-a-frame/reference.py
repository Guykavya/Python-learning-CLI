import pandas as pd


def shrink(df, max_unique=50):
    out = df.copy()
    for col in out.columns:
        s = out[col]
        if isinstance(s.dtype, pd.CategoricalDtype) or pd.api.types.is_bool_dtype(s):
            continue
        if pd.api.types.is_integer_dtype(s):
            out[col] = pd.to_numeric(s, downcast="integer")
        elif pd.api.types.is_float_dtype(s):
            small = s.astype("float32")
            if small.astype("float64").equals(s):
                out[col] = small
        elif pd.api.types.is_string_dtype(s) and s.nunique() <= max_unique:
            out[col] = s.astype("category")
    return out
