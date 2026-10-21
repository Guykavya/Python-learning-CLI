## Hint 1

The list holds references side by side in one block of memory. What must move when an item goes
in at the front?

## Hint 2

When the block is full, a bigger block is allocated and the references are copied. How often
does that happen if each new block has spare room?

## Hint 3

Doubling n doubles the number of inserts **and** doubles the work of each one.
