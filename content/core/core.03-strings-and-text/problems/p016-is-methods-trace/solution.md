## Walkthrough

| Line | Result | Why |
|---|---|---|
| `"2026".isdigit()` | `True` | all digits |
| `"-5".isdigit()` | `False` | `-` is not a digit |
| `"3.14".isdecimal()` | `False` | `.` is not a digit |
| `"".isalpha()` | `False` | empty strings are False |
| `"café".isalpha()` | `True` | `é` is a letter |
| `"hello world".isalpha()` | `False` | the space |
| `"abc123".isalnum()` | `True` | letters and digits |
| `" \t\n".isspace()` | `True` | all whitespace |
| `"HELLO 2".isupper()` | `True` | uncased characters are ignored |
| `"Hello World".istitle()` | `True` | each word starts upper, rest lower |
| `"²"` | `True False` | a digit, but not a decimal digit |
| `"_name".isidentifier()` | `True` | names may start with `_` |
