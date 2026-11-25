import matplotlib.pyplot as plt


def revenue_chart(df):
    # Misleading on purpose: fix the window, the baseline, the unit and the title.
    last = df.tail(3)
    fig, ax = plt.subplots()
    ax.bar(last["date"].dt.strftime("%b"), last["revenue"])
    ax.set_ylim(bottom=last["revenue"].min() * 0.95)
    ax.set_title("Revenue is soaring!")
    return fig
