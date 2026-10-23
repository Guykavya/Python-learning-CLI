## Hint 1

For each test decide first what `parse_age(...)` really does with that argument: returns, raises `ValueError` with which message, or raises something else.

## Hint 2

`test_g`: `None.isdigit()` raises `AttributeError`. Is that an `Exception`? `test_i`: in a regular expression, what does `a+b` mean? Does it match the text `a+b`?

## Hint 3

The `+` means "one or more a", so the pattern `a+b` looks for `ab`, `aab`, ... The message contains `a+b` with a literal plus sign in between, so it does not contain `ab`.
