## Hint 1

The list grows only when `size == capacity` at the start of an append. Write the capacity after each growth:
1, 2, 4, 8, ... and find at which item the list is full each time.

## Hint 2

When the capacity is 1, item 1 fits. Item 2 finds the list full (size 1), so it grows to 2, copying 1 item.
Item 3 finds size 2 == capacity 2: grow to 4, copying 2 items.

## Hint 3

Growth happens before items 2, 3, 5, 9 and 17. The copies are 1 + 2 + 4 + 8 + 16.
