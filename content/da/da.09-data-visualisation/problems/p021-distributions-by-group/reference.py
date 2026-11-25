import matplotlib.pyplot as plt
import seaborn as sns


def hist_by_group(df):
    fig, ax = plt.subplots()
    sns.histplot(data=df, x="value", hue="group", stat="density", common_norm=False, ax=ax)
    return fig
