## Hint 1

For question 2: an element moves one level deeper only when **its root** is hung under another root. With union by size, that happens only when its own group is the **smaller** one (or equal). If the smaller group had `s` elements and the other at least `s`, how big is the merged group?

## Hint 2

For question 3: unite pairs `(0,1), (2,3), (4,5), (6,7)` (height 1), then pairs of pairs (height 2), then the two groups of four (height 3). For height 4 an element would have to be moved down 4 times; by the doubling argument its group would then have at least `2**4 = 16` elements.

For question 5: think of a bank account. Some operations pay a lot, but they also "save" work for the later ones (compression flattens the path). Amortised cost = total cost divided by the number of operations.
