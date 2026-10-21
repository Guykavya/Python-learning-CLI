# Validate a username

Write `validate_username(name)` that returns `name` unchanged if it is a valid username, and
otherwise **raises** an exception with a message that tells the user what to do. Check the rules
in this order and raise for the **first** one that fails:

| Rule | Exception and message |
|---|---|
| `name` must be a `str` | `TypeError("username must be text (str), got <type name>")` |
| length 3 to 15 characters | `ValueError("username must be 3 to 15 characters long, got <length>")` |
| only letters, digits and `_` (use `ch.isalnum() or ch == "_"`) | `ValueError("username may only use letters, digits and _, found <char!r>")` with the **first** bad character |
| must not start with a digit | `ValueError("username must not start with a digit")` |

Do not print anything. The caller decides what to do with the exception.

**Examples**

```python
validate_username("asha_99")      # 'asha_99'
validate_username("ab")           # ValueError: username must be 3 to 15 characters long, got 2
validate_username("ravi kumar")   # ValueError: username may only use letters, digits and _, found ' '
validate_username("7up")          # ValueError: username must not start with a digit
validate_username(42)             # TypeError: username must be text (str), got int
```
