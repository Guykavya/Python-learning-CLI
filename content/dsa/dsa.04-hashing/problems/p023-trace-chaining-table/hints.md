## Hint 1

Buckets: 5 -> 1, 9 -> 1, 12 -> 0, 13 -> 1, 5 again is already in bucket 1, 7 -> 3, 16 -> 0, 1 -> 1, 20 -> 0.

## Hint 2

Chain in bucket 1 grows 5, 9, 13, 1 (the second 5 is a duplicate and does not grow it).

## Hint 3

`find(13)` walks bucket 1: 5 (step 1), 9 (step 2), 13 (step 3). `find(100)` goes to bucket 0 and walks 12, 16, 20 without finding it: 3 steps, missing.
