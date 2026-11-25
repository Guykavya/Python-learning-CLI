## Hint 1

Ask two questions of each need: does the value belong to **one row** of a table and never change with the slicers (column), or does it have to be recomputed for whatever the reader selected (measure)? And: will it be used as a slicer or an axis (needs a column) or as a number to show (measure)?

## Hint 2

Ratios and distinct counts must never be stored per row (they do not add up). A running total depends on the dates visible, so it is a measure.
