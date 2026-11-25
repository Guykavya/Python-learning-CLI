# Regression line drawn by seaborn

Chapter section 5.4. `sns.regplot` draws a scatter **and** fits and draws a regression line. What does that line equal? Check it against the numbers.

Write `trend(df)` for a DataFrame with columns `x` and `y`:

- draw a scatter with the fitted line using `sns.regplot` and **no** confidence band (`ci=None`);
- label the axes with the column names;
- return the Figure.

The test reads the **slope of the line that seaborn drew** (from its first and last points) and compares it with the least-squares slope
`np.polyfit(df["x"], df["y"], 1)[0]`.

## Example

For points on `y = 2x + 1` with a little noise, the drawn line has a slope very close to 2.
