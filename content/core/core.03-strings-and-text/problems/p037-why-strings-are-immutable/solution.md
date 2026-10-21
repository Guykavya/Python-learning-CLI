See the model answer shown when you check. The ideas that must appear:

1. A `str` object never changes. You build a new string and rebind the name: `name = "A" + name[1:]` or `name = name.capitalize()`.
2. Methods return new strings; the result must be stored.
3. Benefits: safe sharing between names and functions, usable as dictionary keys (stable hash), simpler reasoning, and Python can reuse identical strings.
4. Repeated `+=` copies the growing string every time, so the total work grows roughly with the square of the number of pieces. `join` measures all pieces first, allocates once and copies each piece once.
5. CPython can sometimes grow a string in place when no other name refers to it, but that optimisation is fragile and not part of the language.
