**Why:** floats are stored in binary (IEEE 754 double precision, 64 bits). Just as 1/3
cannot be written exactly in decimal (0.333...), 0.1 and 0.2 cannot be written exactly
in binary. Each is stored as the closest possible binary value, slightly off. Adding
two slightly-off values gives `0.30000000000000004`, which is not the stored value
closest to 0.3.

**Not a bug:** every language using hardware floats (C, Java, JavaScript) behaves the same.
It is a property of the binary format, chosen because it is fast and covers a huge range.

**Comparing:** never use `==` on computed floats. Use `math.isclose(a, b)`, which checks
the values are within a small relative tolerance.

**Money:** use `decimal.Decimal`, created from strings (`Decimal("0.10")`), or store whole
cents as `int`. Decimal does base-10 arithmetic, so 0.1 is exact and rounding rules
(like ROUND_HALF_UP) are under your control.

Key ideas to check: binary representation, closest approximation, isclose, Decimal from strings or integer cents.
