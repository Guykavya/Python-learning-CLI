import warnings

import numpy as np
import statsmodels.api as sm


def _mentions_separation(obj):
    text = (type(obj).__name__ + " " + str(obj)).lower()
    return "separation" in text


def safe_logit(X, y):
    if np.linalg.matrix_rank(np.asarray(X, dtype=float)) < np.asarray(X).shape[1]:
        return None, "singular design matrix: a column is a copy or combination of others"
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            res = sm.Logit(y, X).fit(disp=0)
        except np.linalg.LinAlgError:
            return None, "singular design matrix: a column is a copy or combination of others"
        except Exception as exc:
            if _mentions_separation(exc):
                return None, "perfect separation: no finite maximum-likelihood estimate"
            raise
    if any(_mentions_separation(w.message) or _mentions_separation(w.category()) for w in caught):
        return None, "perfect separation: statsmodels warned about it"
    if not np.all(np.isfinite(res.params)) or np.max(np.abs(res.params)) > 15:
        return None, "separation suspected: absurdly large coefficient"
    return res, "ok"
