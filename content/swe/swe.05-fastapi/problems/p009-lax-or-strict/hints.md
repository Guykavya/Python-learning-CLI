## Hint 1

Section 5.4: lax mode converts a value when the conversion is **unambiguous and loses nothing**. For `int`: is the text `"5"` clearly 5? Is the float `5.0`? Is `5.5`? For `bool`: which words and numbers did section 3.1 list as true or false?

## Hint 2

Strict mode accepts **only the exact type**: an `int` field wants a real `int`, a `bool` field a real `bool`. Careful: in Python `True` is also an int (`isinstance(True, int)` is `True`), but Pydantic's strict `int` refuses bools, while lax `int` turns `True` into `1`.

## Hint 3

```text
lax int:    "5" -> 5, 5.0 -> 5, 1 -> 1, True -> 1; 5.5, "true", "yes" -> error
lax bool:   "true", "yes", 1, True -> True; "5", 5.0, 5.5 -> error
strict int: only a real int (1); everything else, even True, -> error
strict bool: only a real bool (True); everything else, even 1, -> error
```
