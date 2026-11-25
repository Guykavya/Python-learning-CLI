# What does each summary line mean?

Chapter section 5. A student fitted the study-hours model below. The data are synthetic (30 students, seeded random numbers; the code is in the chapter's style):

```python
rng = np.random.default_rng(5)
hours = rng.uniform(1, 10, 30).round(1)
score = (40 + 5 * hours + rng.normal(0, 6, 30)).round(1)
res = sm.OLS(score, sm.add_constant(hours)).fit()
print(res.summary())
```

```text
                            OLS Regression Results
==============================================================================
Dep. Variable:                      y   R-squared:                       0.866
Model:                            OLS   Adj. R-squared:                  0.862
Method:                 Least Squares   F-statistic:                     181.6
Date:                Wed, 25 Nov 2026   Prob (F-statistic):           9.22e-14
Time:                        09:23:34   Log-Likelihood:                -96.429
No. Observations:                  30   AIC:                             196.9
Df Residuals:                      28   BIC:                             199.7
Df Model:                           1
Covariance Type:            nonrobust
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
const         37.1049      2.475     14.990      0.000      32.034      42.175
x1             5.2896      0.393     13.475      0.000       4.486       6.094
==============================================================================
Omnibus:                        0.766   Durbin-Watson:                   2.012
Prob(Omnibus):                  0.682   Jarque-Bera (JB):                0.651
Skew:                           0.336   Prob(JB):                        0.722
Kurtosis:                       2.736   Cond. No.                         14.0
==============================================================================
```

(The date and time lines change every run. The numbers below them do not.)

Write your answer in `answer.md`: for each of these **eight** items, one sentence that says what the number measures **and** what it says in this printout:

1. R-squared
2. Prob (F-statistic)
3. coef of `x1`
4. std err of `x1`
5. t of `x1`
6. P>|t| of `x1`
7. Durbin-Watson
8. Jarque-Bera (or its Prob)

## After you answer

Compare with the model answer. Tick each box of its checklist only if your sentence really made that point.
