See the model answer shown when you check. The ideas that must appear:

1. Outputs: f1 `[1, 2, 3]`, f2 `[3, 1, 2]`, f3 `[3, 1, 2]`, f4 `[3, 1, 2, 4]`, f5 `[3, 1, 2]`.
2. The parameter refers to the same object as `data`; nothing is copied on the call.
3. Mutating methods, item/slice assignment and `+=` on a list change the caller's object.
4. `lst = ...` rebinds only the local name; later operations act on the new object.
5. Ints seem 'by value' only because they are immutable; every object is passed the same way.
