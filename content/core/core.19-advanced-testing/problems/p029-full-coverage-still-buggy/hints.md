## Hint 1

Look at the three bad results one at a time and ask: which input did the three tests use, and which input shows the bug? Is `10` among
the inputs? Is there any test where `weight_kg` is large **and** `express` is true? Is there any line in the function that mentions a negative weight?

## Hint 2

Coverage answers "which lines and decisions ran?". For each bug, ask whether it can be seen by looking at which lines ran. Three different reasons
explain the three bugs: a value on the border of a condition, two decisions that never met in one call, and code that was never written.

```
bug 1: condition is  > 10  but spec says >= 10      -> border value 10 never tried
bug 2: surcharge added, THEN doubled                  -> no call with heavy AND express
bug 3: no check for negative weight at all            -> no line exists to be "uncovered"
tests: shipping(10, False) == 15 | shipping(12, True) == 20 | pytest.raises(ValueError)
```
