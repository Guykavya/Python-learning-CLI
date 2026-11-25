# Redo a flawed analysis

Chapter section 10, the module project. An analyst compared app users and non-users in a customer table and wrote: "App users spend
far more, so the app boosts spending by that amount; push it to everyone." You redo the analysis on the data they had.

The table `study_df` has one row per customer: `city` (Metro, Large, Small), `age`, `engagement` (a measured score), `app` (bool: uses the
app) and `spend`. Keen, older/younger and Metro customers install the app more, so the naive comparison is confounded by measured variables.

Write `redo(study_df, mei)` returning a dict with these keys:

| key | value |
|---|---|
| `"naive_diff"` | mean spend of app users minus mean spend of the others |
| `"adjusted_diff"` | the coefficient of `app` in `spend ~ app_i + engagement + age + C(city)` (OLS, `app_i` = 0/1) fitted with **robust standard errors** `cov_type="HC3"` |
| `"ci"` | the 95% confidence interval of that coefficient from the same fit, a tuple `(low, high)` of floats |
| `"verdict"` | the chapter's label for the interval against `mei`: `"worth it: the whole interval is above the minimum effect"` (`low > mei`), `"not worth it: the whole interval is below the minimum effect"` (`high < mei`), else `"inconclusive: the interval contains the minimum effect"` |
| `"report"` | a short text that **contains** the three numbers (estimate, low, high) rounded with `sig_round(value, SE)` (SE of the coefficient; the rule of problem 33, copy it), the word **observational** and the word **confounder** |

Example of a good report: `Adjusted for engagement, age and city, app users spend 118 rupees more (95% CI 92 to 144). This is an
observational comparison: an unmeasured confounder could still bias it.`

## Example

On a study with a true effect of 120 rupees, the naive difference is several hundred rupees, the adjusted estimate is near 120 with an
interval of about 25 rupees on each side, and with `mei = 50` the verdict is `worth it`.
