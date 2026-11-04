## Hint 1

Call 1: `lo=0, hi=4`, pivot 5. j=0: 6 is not < 5. j=1: 3 < 5, swap with a[0] -> [3, 6, 8, 1, 5], i=1. j=2: 8 no. j=3: 1 < 5, swap with a[1] -> [3, 1, 8, 6, 5], i=2. Final swap a[2] and a[4]: [3, 1, 5, 6, 8].

## Hint 2

Then the left call `lo=0, hi=1` (values 3, 1) has pivot 1 and lands at index 0; the right call `lo=3, hi=4` (values 6, 8) has pivot 8 and lands at index 4 (6 < 8 swaps with itself).

## Hint 3

Every `base` line is printed for a range with `lo >= hi`, including empty ranges like `lo=0, hi=-1`. Just follow the code call by call, left recursion first.
