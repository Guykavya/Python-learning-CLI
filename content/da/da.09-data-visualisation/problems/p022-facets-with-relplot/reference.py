import seaborn as sns


def store_lines(df):
    g = sns.relplot(data=df, x="week", y="revenue", col="store", col_wrap=3, kind="line",
                    errorbar=None, facet_kws={"sharey": True})
    g.set_titles("{col_name}")
    return g
