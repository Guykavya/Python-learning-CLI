- **`pd.to_numeric(s, errors="coerce")` straight away.** `"₹45,000"`, `"45k"` and `"45000/-"` all become `NaN`: good
  numbers thrown away. Remove the decoration first.
- **Checking the codes too late.** `"-999"` is a code for "no answer" and must give missing; if you strip signs or
  commas first it turns into `999` and survives as a real income. Test the codes on the stripped, lower-cased text first.
- **Using `float(text)` as the test.** `float("1e5")`, `float("inf")` and `float("-5000")` all succeed. The rules say
  digits with an optional decimal part, so check the shape.
- **Forgetting the `k` factor for decimals.** `"4.5K"` is 4500, not 45000 or 4.5.
- **Case.** `"RS. 31000"`, `"N/a"`, `"45K"` all appear in real files. Lower-case first.
- **Raising an error on `"forty"`.** The function's job is to say "missing" and let the caller count how many.
