import pandas as pd


def channel_by_region(orders):
    """(counts, shares): orders per region x channel, and each region's row as shares that sum to 1."""
    counts = pd.crosstab(orders["region"], orders["channel"])
    shares = pd.crosstab(orders["region"], orders["channel"], normalize="index")
    return counts, shares
