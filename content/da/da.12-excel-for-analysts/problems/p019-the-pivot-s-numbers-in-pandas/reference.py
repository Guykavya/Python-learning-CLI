import pandas as pd


def pivot_expected(orders):
    pt = orders.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum",
                            margins=True, margins_name="Grand Total", fill_value=0)
    rows = sorted([r for r in pt.index if r != "Grand Total"], key=str.lower) + ["Grand Total"]
    cols = sorted([c for c in pt.columns if c != "Grand Total"], key=str.lower) + ["Grand Total"]
    return pt.loc[rows, cols].round(2)
