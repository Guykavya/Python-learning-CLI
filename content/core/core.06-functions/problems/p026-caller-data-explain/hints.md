## Hint 1

Draw one list object and two arrows: `data` and `lst`. After each line, which arrow moved and which object changed?

## Hint 2

`lst = anything` only moves the local arrow. After that, nothing done to `lst` can reach the caller's list.

## Hint 3

`+=` on a list is in-place; `lst + [4]` builds a new list.
