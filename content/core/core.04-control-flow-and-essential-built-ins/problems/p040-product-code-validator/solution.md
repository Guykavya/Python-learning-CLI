## Approach

An `if`/`elif` chain in the order of the rules. The first failing rule wins, which is exactly
what an `elif` chain does. `all` checks every character of a slice.

## Code

```python
UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"
n = int(input())
valid = 0
for _ in range(n):
    code = input().strip()
    if len(code) != 7:
        reason = "length"
    elif not all(ch in UPPER for ch in code[:2]):
        reason = "letters"
    elif code[2] != "-":
        reason = "dash"
    elif not all(ch in DIGITS for ch in code[3:]):
        reason = "digits"
    else:
        reason = ""
    if reason:
        print(f"{code}: invalid ({reason})")
    else:
        print(f"{code}: valid")
        valid += 1
print(f"Valid: {valid} of {n}")
```

## Why the length check is first

Every later check indexes or slices assuming 7 characters. `code[2]` on `"AB"` crashes. The
`elif` chain guarantees the later checks only run when the length is right.

## Why not `isupper()` and `isdigit()`

`"É".isupper()` is `True` and `"²".isdigit()` is `True`. The rules say A to Z and 0 to 9, so
membership in an explicit string is the exact test.

## About `_`

`for _ in range(n)` is the usual name for a loop variable you do not use.
