See the model answer shown when you check. The four ideas that must appear:

1. Floats are binary approximations; 0.1 has no exact binary form.
2. This is the IEEE 754 standard, shared by almost every language.
3. Compare with `math.isclose`, not `==`.
4. Use `Decimal("...")` or integer cents for money.
