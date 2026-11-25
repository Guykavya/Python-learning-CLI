import matplotlib.pyplot as plt
import seaborn as sns


def trend(df):
    fig, ax = plt.subplots()
    sns.regplot(data=df, x="x", y="y", ci=None, ax=ax)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    return fig
