See the model answer shown when you check. The ideas that must appear:

1. Mutable: changes in place, same identity. Immutable: never changes; operations make new objects.
2. At least four immutable types (int, float, str, bool, complex, None, Decimal, Fraction).
3. `n += 1` on an int creates a new object and rebinds `n`; `m` is unaffected.
4. `append` mutates the one shared list, so both names see it.
5. Immutable objects are safe to share.
6. Rule: distinguish rebinding from mutation; copy explicitly when you need independence.
