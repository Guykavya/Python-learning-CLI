import numpy as np
import matplotlib.pyplot as plt


def share_bars(df, group, part, value):
    groups = list(df[group].unique())
    parts = list(df[part].unique())
    tbl = (df.groupby([group, part])[value].sum().unstack(fill_value=0)
             .reindex(index=groups, columns=parts, fill_value=0))
    pct = tbl.div(tbl.sum(axis=1), axis=0) * 100
    fig, ax = plt.subplots()
    bottom = np.zeros(len(groups))
    for p in parts:
        ax.bar([str(g) for g in groups], pct[p].to_numpy(), bottom=bottom, label=str(p))
        bottom = bottom + pct[p].to_numpy()
    ax.set_ylabel("Share (%)")
    ax.legend()
    return fig
