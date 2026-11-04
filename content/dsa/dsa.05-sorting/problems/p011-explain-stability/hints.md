## Hint 1

What do `ann` and `cy` have in common? In the input, which one comes first?

## Hint 2

A stable sort keeps `ann` before `cy` and `bob` before `dee`, because their keys are equal. Output: `[('bob', 25), ('dee', 25), ('ann', 30), ('cy', 30)]`.

## Hint 3

Two-pass recipe: sort by the **less important** key first, then by the **more important** key. The second pass keeps the first pass's order among ties.
