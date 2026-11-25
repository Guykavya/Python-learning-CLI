import plotly.express as px


def px_bars(df):
    d = df.groupby("store", as_index=False)["revenue"].sum().sort_values("revenue")
    return px.bar(d, x="revenue", y="store", orientation="h", title="Revenue by store",
                  labels={"revenue": "Revenue (USD)", "store": "Store"})
