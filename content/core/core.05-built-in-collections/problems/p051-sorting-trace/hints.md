## Hint 1

Without a key, strings compare by character codes: every uppercase letter comes before every
lowercase letter.

## Hint 2

The sort is stable. With `reverse=True`, equal items still keep their original order, which is
**not** the same as reversing a sorted list.

## Hint 3

`max` and `min` with a key return the **first** item that has the best key.
