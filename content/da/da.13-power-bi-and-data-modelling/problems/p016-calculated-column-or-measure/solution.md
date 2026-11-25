## Approach

Columns describe things (rows), measures describe totals (contexts). Anything used to slice, group or filter must be a column; anything that must respond to the slicers is a measure.

## Code

See `answer.md`.

## Complexity

Not applicable (an explain problem).

## Another way

Make the columns in **Power Query or pandas** before loading (a price band, an age group): they are then part of the data, tested in Python, and they cost no refresh time inside the model.
