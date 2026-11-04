## Approach

Compute counts, turn counts into start positions (prefix sums), then place each record at the next free slot of its key, in input order.

## Expected output

```text
count [2, 1, 3]
start [0, 2, 3]
ann -> [None, None, None, 'ann', None, None]
bob -> ['bob', None, None, 'ann', None, None]
cy -> ['bob', None, None, 'ann', 'cy', None]
dee -> ['bob', None, 'dee', 'ann', 'cy', None]
eli -> ['bob', 'eli', 'dee', 'ann', 'cy', None]
fay -> ['bob', 'eli', 'dee', 'ann', 'cy', 'fay']
['bob', 'eli', 'dee', 'ann', 'cy', 'fay']
```

## Why

Because the records are placed in input order and each key's slots are filled left to right, equal keys keep their order: this loop is stable. Going backwards would need `end` positions (decrementing from the back); that is the textbook version and is equally stable. This stable placement is what makes radix sort work.
