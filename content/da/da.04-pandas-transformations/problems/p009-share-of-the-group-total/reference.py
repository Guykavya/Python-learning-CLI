import pandas as pd


def share_of_store(lines):
    """Copy of lines with a column share = revenue / revenue of the line's store."""
    total = lines.groupby("store_id")["revenue"].transform("sum")
    return lines.assign(share=lines["revenue"] / total)
