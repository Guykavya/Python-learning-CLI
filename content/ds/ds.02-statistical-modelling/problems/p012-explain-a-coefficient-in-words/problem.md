# Explain a coefficient in words

Chapter section 7. Every coefficient is a sentence in disguise: *"Holding the other variables in the model fixed, a one-unit increase in x is associated with a b-unit change in y."* Four models were fitted on synthetic data. Write one careful sentence for each coefficient, using the right units.

| # | Model | Coefficient |
|---|---|---|
| 1 | `score ~ hours` (score in marks, hours per week) | `hours = 4.7` |
| 2 | `np.log(wage) ~ experience + ...` | `experience = 0.025` |
| 3 | `np.log(sales) ~ np.log(area) + ...` | `np.log(area) = 0.80` |
| 4 | `np.log(wage) ~ C(education, Treatment('school')) + ...` | `degree = 0.18` |

Write your answer in `answer.md`. For the log-level cases (2 and 4) also give the **exact** percent change `100 * (exp(b) - 1)`, rounded to one decimal, and say why it differs from `100 * b`.

(Useful values: `exp(0.025) = 1.0253`, `exp(0.18) = 1.1972`.)

## After you answer

Compare with the model answer and tick the checklist only for points you really made.
