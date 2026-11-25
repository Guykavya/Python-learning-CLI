import plotly.express as px


def px_lines(df):
    return px.line(df, x="month", y="revenue", facet_col="store", hover_data=["units"],
                   labels={"revenue": "Revenue (USD)"}, title="Revenue by month")
