# The formula interface

Chapter section 6. The monthly-wages table has the columns `wage`, `experience`, `education` (`school`, `degree`, `masters`) and `city` (`Pune`, `Delhi`, `Mumbai`). The data are synthetic; the true log-wage model has education effects **0.18** (degree) and **0.40** (masters, at zero experience) relative to `school`, and about 0.025 per year of experience. The masters gap really grows by 0.01 per year of experience; this formula has no interaction, so its masters coefficient is an **average** of that growing gap (about 0.55 with these data, as the chapter's 0.53 shows).

Write `fit_wages(df)` that fits, with `statsmodels.formula.api.ols`:

```text
np.log(wage) ~ experience + C(education, Treatment(reference='school')) + C(city)
```

and returns the fitted results object. The baseline for education must be `school` (not the alphabetical default `degree`).

> **Trap:** a formula such as `np.log(wage)` is evaluated by `patsy` in the namespace of **your file**. Your `solution.py` must `import numpy as np`, or the fit fails with `NameError: name 'np' is not defined`.

<details><summary>The generator (so you can try your function in <code>my-work</code>)</summary>

```python
import numpy as np
import pandas as pd

def make_wages(n=400, seed=11):
    rng = np.random.default_rng(seed)
    experience = rng.integers(0, 31, size=n)
    education = rng.choice(["school", "degree", "masters"], size=n, p=[0.4, 0.4, 0.2])
    city = rng.choice(["Pune", "Delhi", "Mumbai"], size=n, p=[0.4, 0.35, 0.25])
    log_wage = (10.2 + 0.025 * experience
                + 0.18 * (education == "degree") + 0.40 * (education == "masters")
                + 0.10 * (city == "Delhi") + 0.22 * (city == "Mumbai")
                + 0.01 * experience * (education == "masters")
                + rng.normal(0, 0.25, size=n))
    return pd.DataFrame({"wage": np.exp(log_wage).round(0), "experience": experience,
                         "education": education, "city": city})
```
</details>

## Example

```text
res = fit_wages(make_wages(1500))
[name for name in res.params.index if "education" in name]
-> ["C(education, Treatment(reference='school'))[T.degree]",
    "C(education, Treatment(reference='school'))[T.masters]"]
```
