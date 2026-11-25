from itertools import combinations


def candidate_keys(df, max_cols=2):
    found = []
    for size in range(1, max_cols + 1):
        for combo in combinations(df.columns, size):
            if any(set(k) <= set(combo) for k in found):
                continue
            cols = list(combo)
            if df[cols].isna().any(axis=None):
                continue
            if not df.duplicated(subset=cols).any():
                found.append(combo)
    return found
