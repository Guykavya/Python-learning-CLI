import pandas as pd
import statsmodels.api as sm


def vif_table(df, predictors):
    vifs = {}
    for name in predictors:
        others = [p for p in predictors if p != name]
        if not others:
            vifs[name] = 1.0
            continue
        r2 = sm.OLS(df[name], sm.add_constant(df[others])).fit().rsquared
        vifs[name] = 1.0 / (1.0 - r2)
    return pd.Series(vifs).sort_values(ascending=False)
