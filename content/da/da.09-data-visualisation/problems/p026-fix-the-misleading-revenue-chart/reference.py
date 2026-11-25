import matplotlib.pyplot as plt


def revenue_chart(df):
    first, last = df["revenue"].iloc[0], df["revenue"].iloc[-1]
    pct = round(abs(last / first - 1) * 100)
    word = "grew" if last >= first else "fell"
    start, end = df["date"].iloc[0].strftime("%b %Y"), df["date"].iloc[-1].strftime("%b %Y")
    fig, ax = plt.subplots()
    ax.plot(df["date"], df["revenue"])
    ax.set_ylim(bottom=0)
    ax.set_ylabel("Revenue (USD)")
    ax.set_title(f"Revenue {word} {pct}% from {start} to {end}")
    return fig
