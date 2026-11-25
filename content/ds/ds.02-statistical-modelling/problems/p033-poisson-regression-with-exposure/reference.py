import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf


def rate_model(df):
    model = smf.glm("count ~ treated", data=df, family=sm.families.Poisson(),
                    offset=np.log(df["exposure"]))
    res = model.fit()
    lo, hi = res.conf_int().loc["treated"]
    return {"rate_ratio": float(np.exp(res.params["treated"])),
            "ci_low": float(np.exp(lo)), "ci_high": float(np.exp(hi))}
