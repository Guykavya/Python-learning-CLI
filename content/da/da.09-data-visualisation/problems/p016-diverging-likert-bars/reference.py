import matplotlib.pyplot as plt


def likert_bars(counts):
    pct = counts.div(counts.sum(axis=1), axis=0) * 100
    cols = list(pct.columns)
    sd, d, n, a, sa = (pct[c].to_numpy() for c in cols)
    half = n / 2
    lefts = [-(sd + d + half), -(d + half), -half, half, half + a]
    widths = [sd, d, n, a, sa]
    questions = [str(q) for q in pct.index]
    fig, ax = plt.subplots()
    for c, left, w in zip(cols, lefts, widths):
        ax.barh(questions, w, left=left, label=str(c))
    ax.axvline(0, color="black", linewidth=1)
    ax.set_xlabel("Share of answers (%)")
    ax.legend()
    return fig
