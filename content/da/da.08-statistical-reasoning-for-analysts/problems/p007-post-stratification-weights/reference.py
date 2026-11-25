import pandas as pd


def weighted_mean(sample_df, value, by, pop_shares):
    if abs(sum(pop_shares.values()) - 1) > 1e-9:
        raise ValueError(f"shares must add up to 1, got {sum(pop_shares.values())}")
    means = sample_df.groupby(by)[value].mean()
    for s in means.index:
        if s not in pop_shares:
            raise ValueError(f"stratum {s!r} is in the sample but not in pop_shares")
    for s in pop_shares:
        if s not in means.index:
            raise ValueError(f"stratum {s!r} has no rows in the sample")
    return float(sum(share * means[s] for s, share in pop_shares.items()))
