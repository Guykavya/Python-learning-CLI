import matplotlib.pyplot as plt


def make_panels(rows, cols, sharey=False, figsize=(6, 4)):
    fig, _axes = plt.subplots(rows, cols, sharey=sharey, figsize=figsize)
    return fig
