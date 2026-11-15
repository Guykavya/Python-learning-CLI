## Hint 1

Pass 1 (ones digit): 170->0, 45->5, 75->5, 90->0, 802->2, 24->4, 2->2, 66->6. Bucket 0: 170, 90; bucket 2: 802, 2; bucket 4: 24; bucket 5: 45, 75; bucket 6: 66.

## Hint 2

Result of pass 1: `[170, 90, 802, 2, 24, 45, 75, 66]`. Pass 2 uses this order as its input (tens digits: 7, 9, 0, 0, 2, 4, 7, 6).

## Hint 3

There are 3 passes because `max(a) = 802` has 3 digits: after exp = 1000, `802 // 1000` is 0 and the loop stops. Then the `done` line repeats the final list.
