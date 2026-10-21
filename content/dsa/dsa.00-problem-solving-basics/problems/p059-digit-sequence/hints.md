## Hint 1

Count the blocks. 1..9 are 9 numbers of 1 digit: 9 digits. 10..99 are 90 numbers of 2 digits: 180
digits. 100..999 are 900 numbers of 3 digits: 2700 digits. If `k = 190`, is it in the first block?
The first two together (189 digits)? So which block, and at which position inside it?

## Hint 2

Keep `length` (1, 2, 3, ...), `count` (9, 90, 900, ...) and `start` (1, 10, 100, ...). While `k` is
bigger than the whole block (`length * count` digits), subtract the block from `k` and move to the next
one. After that, with `k` counted from 1 inside the block, the number is `start + (k - 1) // length`
and the digit's position inside it (0 = leftmost) is `(k - 1) % length`.

## Hint 3

```
length = 1; count = 9; start = 1
while k > length * count:
    k -= length * count
    length += 1; count *= 10; start *= 10
number = start + (k - 1) // length
index = (k - 1) % length
drop = length - 1 - index            # digits to the right of the one we want
repeat drop times: number //= 10
print number % 10
```
Check: `k = 190` -> after skipping, `k = 1`, `length = 3`, number 100, index 0, drop 2, 100 -> 1 -> digit 1.
