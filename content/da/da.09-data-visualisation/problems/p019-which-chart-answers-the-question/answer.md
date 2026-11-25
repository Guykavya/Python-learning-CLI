## Model answer

1. **Sorted horizontal bars**, largest on top, from zero: bars compare categories by length, which the eye reads best. Avoid a pie chart (six slices that are hard to rank).
2. **Line chart** of monthly revenue: time is ordered and the line shows the direction and the season. Avoid bars for a dense time series.
3. **Histogram or ECDF** (a box plot as a summary): they show the spread, the skew and the outliers; a bare average would hide all three.
4. **Scatter plot** (small, see-through dots if there are thousands): two numbers per customer, so the relationship is the shape of the cloud. Avoid a dual-axis line chart.
5. **100% stacked bars** (one per store): every bar has the same total, so only the shares differ. Avoid a pie per store with many slices.
6. **Diverging stacked bars**: negative answers to the left of zero, positive to the right, neutral split in the middle, so the balance is visible at once.
7. **Heatmap** with the value written in each cell and a colour bar: a number for every weekday-hour pair is a matrix. Avoid a rainbow colour map.
8. **A dot with an interval** (error bar, labelled "95% CI"): the dot shows the difference, the whisker shows how sure we are. Avoid bare bars with no uncertainty.

**Checklist: your answer should mention**
- [ ] sorted bars (not a pie) to compare categories
- [ ] a line for change over time
- [ ] histogram or ECDF for a distribution
- [ ] a scatter plot for a relationship of two numbers
- [ ] 100% stacked bars for shares of a whole
- [ ] diverging bars for a Likert scale
- [ ] a heatmap for a matrix
- [ ] error bars or a dot with an interval for uncertainty
- [ ] at least three charts to avoid, with the reason
