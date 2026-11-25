import numpy as np  # patsy looks up `np` here, in the file that calls ols()
import statsmodels.formula.api as smf


def experience_slope_by_education(df):
    formula = ("np.log(wage) ~ experience * C(education, Treatment(reference='school'))"
               " + C(city)")
    res = smf.ols(formula, data=df).fit()
    base = float(res.params["experience"])
    slopes = {"school": base}
    for name, value in res.params.items():
        if name.startswith("experience:") and "[T." in name:
            level = name.split("[T.")[1].rstrip("]")
            slopes[level] = base + float(value)
    return slopes
