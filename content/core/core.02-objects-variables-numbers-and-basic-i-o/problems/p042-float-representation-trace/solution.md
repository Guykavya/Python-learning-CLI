## Walkthrough

| Expression | Output | Why |
|---|---|---|
| `0.1 + 0.2` | `0.30000000000000004` | both inputs are approximations; the sum lands on the float just above the one nearest 0.3 |
| `0.1 + 0.2 == 0.3` | `False` | different floats |
| `0.5 + 0.25 == 0.75` | `True` | 1/2 and 1/4 are exact in binary |
| `0.1 * 3` | `0.30000000000000004` | same error as above |
| `0.1 + 0.7` | `0.7999999999999999` | here the error goes downward |
| `1e16 + 1` | `1e+16` | at 1e16 neighbouring floats are 2 apart; `+ 1` is lost. Large floats print in e-notation |
| `2 ** 53 + 1.0` | `9007199254740992.0` | 2**53 + 1 needs 54 bits, so it rounds to 2**53 |
| `int(2.9999)` | `2` | truncation |
| `1 / 3` | `0.3333333333333333` | 16 threes is the shortest text that reads back to the same float |
| `10 / 2` | `5.0` | true division always returns a float |
| `1e308 * 10` | `inf` | overflow beyond the largest float (about 1.8e308) |
| `nan == nan` | `False` | IEEE 754 rule |
| `round(0.1 + 0.2, 10) == 0.3` | `True` | rounding to 10 places lands on the float nearest 0.3; works here, but is not a general comparison method (use `math.isclose`) |
