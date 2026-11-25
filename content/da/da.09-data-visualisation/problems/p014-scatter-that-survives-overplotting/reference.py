import matplotlib.pyplot as plt


def overplot_scatter(df, xlabel, ylabel):
    n = len(df)
    alpha, size = (0.2, 6) if n > 2000 else (0.8, 30)
    fig, ax = plt.subplots()
    ax.scatter(df["x"], df["y"], s=size, alpha=alpha)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    return fig
