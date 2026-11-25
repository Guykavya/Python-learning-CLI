import pandas as pd


def region_month_table(items):
    """Revenue by region (rows) and month (columns), 0 for empty cells, with a Total row and column."""
    return items.pivot_table(index="region", columns="month", values="revenue",
                             aggfunc="sum", fill_value=0, margins=True, margins_name="Total")
