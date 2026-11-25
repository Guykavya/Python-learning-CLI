import pandas as pd


def validate_table(df, rules):
    result = []
    for name, rule in rules.items():
        ok = rule(df).fillna(True).astype(bool)
        bad = ~ok
        if bad.any():
            result.append((name, int(bad.sum()), df.index[bad.to_numpy()][:3].tolist()))
    return result
