## Hint 1

Trace the bug report. Round 1: `slow` = 2, `fast` = 3. Round 2: `slow` = 3, `fast` = 3 (from 3, two steps: 2, then 3). Round 3: `slow` = 2, `fast` = 3 ... Can `fast` ever be node `1` again? What **is** true in round 2?

## Hint 2

Floyd's method compares the two pointers with each other, not with the head. Change one name in the `if` line. Then make sure the `if` still comes **after** the two moves, or every list looks cyclic.
