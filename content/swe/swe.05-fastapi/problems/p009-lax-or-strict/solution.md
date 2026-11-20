## Approach

Ask two questions per value: "is it already the exact type?" (enough for strict) and "can it be converted without losing anything or guessing?" (enough for lax).

```text
1: lax n=5 ok=error | strict n=error ok=error
2: lax n=5 ok=error | strict n=error ok=error
3: lax n=error ok=error | strict n=error ok=error
4: lax n=error ok=True | strict n=error ok=error
5: lax n=error ok=True | strict n=error ok=error
6: lax n=1 ok=True | strict n=1 ok=error
7: lax n=1 ok=True | strict n=error ok=True
```

- **1.** `"5"` is clearly the number 5: lax `int` accepts it. `"5"` is not one of the boolean words, so lax `bool` refuses. Strict refuses a string for both.
- **2.** `5.0` has no fractional part, so lax `int` gives `5` (nothing is lost). A float other than 0 or 1 is no boolean. Strict wants a real `int`: a float is refused.
- **3.** `5.5` would lose `.5`: refused everywhere (section 5.4's "got a number with a fractional part").
- **4, 5.** `"true"` and `"yes"` are boolean words, so lax `bool` gives `True`; they are not numbers. Strict refuses strings.
- **6.** `1` is a real int: accepted by both `int` fields. Lax `bool` reads 1 as `True`; strict `bool` wants a real bool and refuses.
- **7.** `True` is a real bool: both `bool` fields accept it. Lax `int` converts it to `1`, but **strict `int` refuses it**, although Python itself treats `True` as an int.

Real output of the program, run with FastAPI 0.162.0 and Pydantic 2.14.3.

## Complexity

Not applicable; this is a reading exercise.

## Another way

Use strict on one field only: `n: int = Field(strict=True)`, or the type `StrictInt` from `pydantic`. And in a FastAPI app the JSON parser has already turned `5` into an int and `true` into a bool, so strict mode mainly stops strings like `"5"` from being accepted for numbers.
