See the model answer shown when you check. The ideas that must appear:

1. Each pending call keeps a frame; 5000 items need about 5000 frames, above the default limit of 1000.
2. The limit protects the interpreter's C stack; raising it risks a hard crash.
3. CPython has no tail-call optimisation, and this function is not tail-recursive anyway.
4. `items[1:]` copies the rest of the list every call: O(n²) total.
5. Use a loop or `sum` for linear recursion; recursion suits nested or branching problems.
