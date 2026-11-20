## Approach

Treat the heaps as sets and do the three steps for each number. The step that matters most is step 2: moving the largest of `low` up makes every number of `low` at most every number of `high`, whatever the new number was. Step 3 then fixes only the sizes.

## Trace

```text
number  step 1 (into low)   step 2 (largest of low to high)   step 3 (high bigger?)       median
7       low {7}             low {}      high {7}              yes: 7 back -> low {7}      top of low = 7
3       low {3, 7}          low {3}     high {7}              no (1 and 1)                (3 + 7) / 2 = 5.0
9       low {3, 9}          low {3}     high {7, 9}           yes: 7 back -> low {3, 7}   top of low = 7
3       low {3, 3, 7}       low {3, 3}  high {7, 9}           no (2 and 2)                (3 + 7) / 2 = 5.0
5       low {3, 3, 5}       low {3, 3}  high {5, 7, 9}        yes: 5 back -> low {3,3,5}  top of low = 5
8       low {3, 3, 5, 8}    low {3, 3, 5}  high {7, 8, 9}     no (3 and 3)                (5 + 7) / 2 = 6.0
```

Check at the end: the data sorted is `3 3 5 7 8 9`; the median is `(5 + 7) / 2 = 6.0`. The halves printed are `[3, 3, 5]` and `[7, 8, 9]`.

## Answers to the questions

1. Step 3 runs on the 1st, 3rd and 5th add: exactly when the count **before** the add was even (so `len(low) == len(high)`). Step 2 moves one number from `low` to `high`, so `high` is then one bigger. When `low` was already one bigger (odd count before), step 2 only makes them equal. So the pattern "move back on odd counts" is not a coincidence; it follows from the size rule.
2. Yes. In step 2 the number that goes up is the maximum of `low` *after* the new number was added, so nothing left in `low` is bigger than it. Everything in `high` was `>=` everything in the old `low`, and the moved number is bigger than the rest of `low`. Step 3 moves the smallest of `high` back, which is still `>=` all of `low`.
3. The first `3` was the first-added small number and ended in `low`; the second `3` also ended in `low` (it was pushed in step 1 and stayed, because `7` was the largest of `low` and moved up). Equal numbers can fall on either side of the border, and the median does not change, because both halves contain a `3` next to the border.

## Another way

Run the program and compare line by line. If a line differs, find the step where your sets and the program's sets differ; the `(moved one back)` note tells you whether you forgot step 3 or ran it when you should not.
