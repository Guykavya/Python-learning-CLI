import pandas as pd
import pandera.pandas as pa


def split_valid(df, schema):
    try:
        schema.validate(df, lazy=True)
    except pa.errors.SchemaErrors as e:
        fc = e.failure_cases
        if fc["index"].isna().any():
            raise
        why = fc.groupby("index")["column"].agg(lambda c: ", ".join(sorted(set(c.dropna()))))
        bad = df.index.isin(why.index)
        quarantine = df[bad].assign(reasons=why.reindex(df.index[bad]).to_numpy())
        return df[~bad].copy(), quarantine
    return df.copy(), df.iloc[0:0].assign(reasons=pd.Series(dtype="str"))
