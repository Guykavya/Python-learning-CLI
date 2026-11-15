## Hint 1

Block `a[l..i]` has sum `total - earlier` where `earlier` is the prefix sum before `l`. For that sum to be `k`, what must `earlier` equal?

## Hint 2

A block that starts at index 0 uses the empty prefix: the total before any element is 0, at index `-1`. Is it in the dictionary at the start?

## Hint 3

For the longest block you want the **earliest** index for each prefix sum. Check when the program writes to the dictionary: does it overwrite an existing entry, and does it write before or after it looks something up?
