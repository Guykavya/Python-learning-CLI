# An interaction term

Chapter section 6.4. An **interaction** lets a slope differ between groups. In the synthetic wages data the pay gain per year of experience is about **0.025** (log points) for `school` and `degree`, and about **0.035** for `masters` (0.025 + an extra 0.01).

Write `experience_slope_by_education(df)` that fits

```text
np.log(wage) ~ experience * C(education, Treatment(reference='school')) + C(city)
```

and returns a dict `{level: slope}` with the **experience slope for each education level** (keys `school`, `degree`, `masters`). Careful: in a formula with an interaction the plain `experience` coefficient is the slope of the *baseline* group only. The slope of another level is that coefficient **plus** its interaction coefficient.

The wages data have columns `wage`, `experience`, `education`, `city` (see the previous problem for the generator). As before, `solution.py` must `import numpy as np` because the formula uses `np.log`.

## Example

```text
experience_slope_by_education(make_wages(2000, 11))
-> {"school": 0.025..., "degree": 0.025..., "masters": 0.035...}   # approximately
```
