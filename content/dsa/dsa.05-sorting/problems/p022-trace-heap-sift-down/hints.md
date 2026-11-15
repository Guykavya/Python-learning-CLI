## Hint 1

Start at index 2 (value 2): its only child is index 5 (value 5). 5 > 2 so swap: `[3, 9, 5, 1, 4, 2]`. Index 5 has no children, the loop ends.

## Hint 2

Start at index 1 (value 9): children 1 and 4 (indices 3 and 4) are both smaller. No swap at all, only the `start 1` line.

## Hint 3

Start at index 0 (value 3): children 9 and 5, the larger is 9 (index 1): swap, then at index 1 children 1 and 4: 4 is larger than 3, swap again.
