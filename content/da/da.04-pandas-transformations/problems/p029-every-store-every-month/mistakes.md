- **Starting from the sales table.** Months without sales cannot appear: no row, no zero.
- **Taking the stores from the sales.** A store that sold nothing at all would be missing from the grid.
- **`how="outer"` with the sales.** Sales of unknown stores or other months sneak in, and the count is no longer
  stores × months.
- **Leaving `NaN` instead of 0.** A chart then has gaps and a `sum` ignores them silently; the task says 0.0.
