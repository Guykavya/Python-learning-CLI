import matplotlib.pyplot as plt


def category_bars(df, cat, val):
    totals = df.groupby(cat)[val].sum().sort_values()
    fig, ax = plt.subplots()
    ax.barh([str(c) for c in totals.index], totals.values)
    ax.set_xlim(left=0)
    ax.set_xlabel(val)
    return fig
