## Hint 1

Pivot = 5. j=0: 7 is not < 5, no swap, i stays 0. j=1: 2 < 5, swap a[0] and a[1] -> [2, 7, 9, 4, 3, 8, 5], i = 1.

## Hint 2

j=3: 4 < 5, swap a[1] and a[3] -> [2, 4, 9, 7, 3, 8, 5], i = 2. j=4: 3 < 5, swap a[2] and a[4] -> [2, 4, 3, 7, 9, 8, 5], i = 3.

## Hint 3

j=5: 8 is not smaller. Finally swap a[3] and the pivot: [2, 4, 3, 5, 9, 8, 7], pivot index 3. For `b`, no value is `< 4`, `i` stays 0, the pivot swaps with itself positions 0 and 3: the returned index is 0.
