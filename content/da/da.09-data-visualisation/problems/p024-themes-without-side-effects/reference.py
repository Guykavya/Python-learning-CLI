import matplotlib.pyplot as plt
import seaborn as sns


def themed_chart(df):
    with sns.axes_style("whitegrid"), sns.plotting_context("talk"):
        fig, ax = plt.subplots()
        ax.bar(df["label"], df["value"])
        ax.set_title("Value by label")
    return fig
