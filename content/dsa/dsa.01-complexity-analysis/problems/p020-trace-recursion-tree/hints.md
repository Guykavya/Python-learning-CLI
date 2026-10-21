## Hint 1

Draw the tree for `n = 4`: a root `4` with two children `2` and `2`, each with two children `1` and `1`.
Count the boxes (calls), and add the numbers in all the boxes (work).

## Hint 2

Look at the tree level by level. For `n = 8` the levels are `8`; `4 4`; `2 2 2 2`; `1 1 1 1 1 1 1 1`.
How much work is on each level, and how many levels are there?

## Hint 3

For `n = 10`, the halves are `10 // 2 = 5` and `10 - 5 = 5`. For `5`, the halves are `2` and `3`. For `3`, they are
`1` and `2`. Build the tree and add up carefully. `calls(n) = 1 + calls(left) + calls(right)`, and the same for
work, with `n` instead of 1.
