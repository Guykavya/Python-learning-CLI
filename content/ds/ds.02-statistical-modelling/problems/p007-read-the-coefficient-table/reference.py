import numpy as np
import pandas as pd


def coef_report(result, exponentiate=False, digits=3):
    ci = np.asarray(result.conf_int())
    out = pd.DataFrame({
        "estimate": np.asarray(result.params),
        "ci_low": ci[:, 0],
        "ci_high": ci[:, 1],
        "p": np.asarray(result.pvalues),
    }, index=list(result.model.exog_names))
    if exponentiate:
        out[["estimate", "ci_low", "ci_high"]] = np.exp(out[["estimate", "ci_low", "ci_high"]])
    return out.round(digits)
