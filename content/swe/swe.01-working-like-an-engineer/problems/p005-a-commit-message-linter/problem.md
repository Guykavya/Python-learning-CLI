# A commit message linter

Chapter section 4.2 gives the rules of a good commit message. Write `lint_message(msg)` that returns the list of **problems** found, as short codes, in this fixed order (each code at most once):

| Code | When |
|---|---|
| `"empty"` | the message is empty or only whitespace (then return only this code) |
| `"subject-too-long"` | the first line has more than 50 characters |
| `"subject-ends-with-period"` | the first line ends with `.` |
| `"no-blank-line"` | there is a second line and it is not empty |
| `"body-line-too-long"` | any line after the subject has more than 72 characters |

Trailing whitespace and newlines at the very end of the message are ignored. A perfect message returns `[]`.

## Examples

```python
lint_message("Fix crash when cart is empty")                       # []
lint_message("Fix crash.")                                          # ["subject-ends-with-period"]
lint_message("Add discount helper\nIt applies a percent.")          # ["no-blank-line"]
lint_message("")                                                    # ["empty"]
```

A subject of exactly 50 characters is fine; 51 is too long. A body line of exactly 72 characters is fine; 73 is too long.
