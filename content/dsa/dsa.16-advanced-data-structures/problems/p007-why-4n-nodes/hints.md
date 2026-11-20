## Hint 1

Draw the tree for `n = 5`: the root `[0,5)`, its children `[0,2)` and `[2,5)`, then `[2,3)` and `[3,5)`, and finally `[3,4)`, `[4,5)`. Write the heap index next to each node. Which indices between 1 and 15 are never used?

## Hint 2

The root is level 0 and has index 1. Level `h` holds the indices `2**h` to `2**(h + 1) - 1`. How deep is the deepest leaf for `n` elements?

## Hint 3

If the height is `h = ceil(log2 n)`, then `2**(h - 1) < n`. Multiply both sides by 4 and compare with `2**(h + 1)`, the first index **after** the bottom level.
