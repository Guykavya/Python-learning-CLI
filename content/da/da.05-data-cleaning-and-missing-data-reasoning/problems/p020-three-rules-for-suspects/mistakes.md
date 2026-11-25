- **Using `>=` and `<=` for the fences.** A value exactly on a fence is not a suspect.
- **Dropping the missing values first** and returning a shorter Series. The result must have the index of `x`; missing
  values are just `False`.
- **Dividing by the MAD without checking for 0.** You get `inf` or `NaN`: values different from the median would be
  flagged by accident in a column where most values are equal.
- **Forgetting the 0.6745** in the robust z-score. Without it the limit 3.5 is on a different scale.
- **Using the mean and std inside `flag_mad`**, or `quantile` inside `flag_z`. Each rule has its own centre and spread.
- **Using `x.std(ddof=0)`.** The task uses pandas' default (sample std).
- **Trusting the z-score because "everybody uses it".** On the toy series it flags nothing: masking.
- **Deleting the flagged rows inside the function.** The function only flags; deleting is a separate, logged decision.
