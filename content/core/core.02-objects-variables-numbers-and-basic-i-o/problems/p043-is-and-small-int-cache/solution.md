See the model answer shown when you check. The ideas that must appear:

1. `==` compares values; `is` compares identity (`id`).
2. CPython caches small ints (-5 to 256), so equal small ints share one object.
3. The cache is an implementation detail and results depend on context, so `is` on numbers is unreliable.
4. `x is 5` triggers a SyntaxWarning because it is almost always a bug.
5. Use `is` for `None` and genuine identity questions; use `==` for values.
