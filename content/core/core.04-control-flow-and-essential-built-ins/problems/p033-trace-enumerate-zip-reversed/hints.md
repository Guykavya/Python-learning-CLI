## Hint 1

`start=10` changes only the numbers. `zip` stops at the shortest input. A tuple prints with
brackets and quotes, like `('a', 1)`.

## Hint 2

After a `for` loop has used up the `zip` iterator, what is left in it? After one `next()`
call on an `enumerate` iterator, where does the `for` loop start?

## Hint 3

`zip()` with no inputs has nothing to give. The last `enumerate` passes `1` as its second
argument: that is the start.
