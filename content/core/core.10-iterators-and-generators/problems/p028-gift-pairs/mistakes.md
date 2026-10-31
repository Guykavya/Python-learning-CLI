- Two nested loops over all positions (`for a in items: for b in items:`): you get `(a, a)` and
  both `(a, b)` and `(b, a)`.
- `permutations(items, 2)`: order matters there, so every pair appears twice.
- `combinations_with_replacement`: it pairs an item with itself, giving `('book', 'book')`.
- Returning the price tuples instead of the names.
