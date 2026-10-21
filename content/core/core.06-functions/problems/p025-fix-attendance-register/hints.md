## Hint 1

Call each function **twice**, and print the caller's lists after each call. Which ones change when they should not?

## Hint 2

Bug 1 is in a `def` line. When is `register=[]` evaluated? Bug 2 and bug 3 change an argument the caller still needs.

## Hint 3

- `mark_present`: default `register=None`, then `if register is None: register = []`.
- `absent_students`: build a new list: `[s for s in all_students if s not in register]`.
- `sorted_register`: `return sorted(register, key=str.lower)` instead of `.sort()` on the argument.
