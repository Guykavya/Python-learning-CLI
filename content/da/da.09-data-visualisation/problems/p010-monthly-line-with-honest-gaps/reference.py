import matplotlib.pyplot as plt
import pandas as pd


def monthly_line(df):
    months = df["date"].dt.to_period("M").dt.to_timestamp()
    m = df.groupby(months)["revenue"].sum()
    m = m.reindex(pd.date_range(m.index.min(), m.index.max(), freq="MS"))
    fig, ax = plt.subplots()
    ax.plot(m.index, m.values)
    ax.set_ylim(bottom=0)
    ax.set_ylabel("Revenue")
    return fig
