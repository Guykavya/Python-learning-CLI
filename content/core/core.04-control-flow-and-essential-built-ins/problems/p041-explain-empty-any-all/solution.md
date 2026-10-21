See the model answer shown when you check. The ideas that must appear:

1. `any`: start `False`, return `True` at the first truthy item. `all`: start `True`, return `False` at the first falsy item.
2. With no items, the loop never runs, so each returns its starting value. `all` means "no counter-example", which holds vacuously.
3. Both stop early; the rest of the items (and any expensive or crashing work in a generator) are never evaluated.
4. Validating input with `all(...)` accepts an empty string; add `text and all(...)`.
5. `sum([])` returns the neutral start 0; `max([])` has no sensible answer, so it raises unless given `default=`.
