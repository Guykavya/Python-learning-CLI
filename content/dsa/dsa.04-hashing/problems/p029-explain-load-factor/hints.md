## Hint 1

For 1 and 2: `n` keys in `m` buckets means each bucket holds about `n / m` keys. With 10^6 keys in 16 buckets, how many per bucket?

## Hint 2

For 3: when the table doubles at sizes 1, 2, 4, 8, 16 it copies 1, 2, 4, 8, 16 keys. Add them up and compare with the number of inserts. Growing by one copies 1, 2, 3, ... keys.

## Hint 3

For 4 and 5: in open addressing every key lives in a slot, so a full table has no empty slot to stop a search. A deleted slot cannot just become empty because it may sit in the middle of a probe run.
