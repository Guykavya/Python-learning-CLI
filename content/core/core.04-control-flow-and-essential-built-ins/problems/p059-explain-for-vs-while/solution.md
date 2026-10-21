See the model answer shown when you check. The ideas that must appear:

1. `for` gets items from an iterator; the `while` version must start the counter right, compare correctly, and increase it (or it loops for ever).
2. `for ch in word:` and `for i, ch in enumerate(word):`.
3. `while` for unknown counts: sentinel or validation input loops; processes like halving until small, or two-index merges.
4. Half-open ranges have `b - a` items, match string positions, and join without overlap.
5. "If you can say what you loop over, use `for`; if you loop until something happens, use `while`."
