import matplotlib.pyplot as plt


def fig_contributions(summary):
    s = summary.drop(index=["observed rise (model)", "left unexplained"]).sort_values("estimate")
    total = summary.loc["observed rise (model)", "estimate"]
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.barh(list(s.index), s["estimate"])
    ax.errorbar(s["estimate"], range(len(s)), xerr=[s["estimate"] - s["CI low"], s["CI high"] - s["estimate"]],
                fmt="none", ecolor="black", capsize=4)
    ax.axvline(0, color="black", linewidth=1)
    ax.set_xlabel("Contribution to the rise in monthly churn (percentage points, 95% interval)")
    ax.set_title(f"{s.index[-1]} explains {s['estimate'].iloc[-1]:.1f} of the {total:.1f}-point rise", loc="left")
    return fig
