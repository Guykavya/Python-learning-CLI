import pandas as pd


def category_counts(s):
    """Frequency table with missing values shown as '(missing)'."""
    counts = s.value_counts()
    return pd.DataFrame({"label": counts.index, "count": counts.values})
