## Hint 1

Label the copies: `[1a, 1b, 2]`. Write the 6 orderings and group those that look the same when you erase the labels.

## Hint 2

In each group, exactly one ordering has 1a before 1b. Now read `not used[i - 1]` as: "1b may be chosen only if 1a is already in the path".

## Hint 3

What does `nums[i - 1]` mean if the list is `[1, 2, 1]` (not sorted)? Is the other 1 its neighbour?
