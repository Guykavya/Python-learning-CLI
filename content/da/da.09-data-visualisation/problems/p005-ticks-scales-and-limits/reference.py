import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def revenue_chart(df, log=False):
    fig, ax = plt.subplots()
    ax.plot(df["month"], df["revenue"])
    if log:
        ax.set_yscale("log")
    else:
        ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, pos: f"{v:,.0f}"))
    ax.set_ylabel("Revenue (USD)")
    return fig
