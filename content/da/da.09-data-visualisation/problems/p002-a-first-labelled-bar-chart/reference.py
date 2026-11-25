import matplotlib.pyplot as plt


def bar_chart(categories, values, title, ylabel):
    fig, ax = plt.subplots()
    ax.bar(categories, values)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    return fig
