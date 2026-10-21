## Approach

Each check is one `any` or `all` call over the characters. The verdict combines the four
booleans.

## Code

```python
password = input()
long_enough = len(password) >= 8
has_digit = any(ch.isdigit() for ch in password)
has_capital = any(ch.isupper() for ch in password)
only_alnum = all(ch.isalnum() for ch in password)
for label, ok in zip(["Length 8+", "Has digit", "Has capital", "Only letters and digits"],
                     [long_enough, has_digit, has_capital, only_alnum]):
    print(f"{label}: {'yes' if ok else 'no'}")
print("Strong" if all([long_enough, has_digit, has_capital, only_alnum]) else "Weak")
```

## Why the empty password says yes for "only"

`all` of nothing is `True`. The string method `"".isalnum()` is `False`, because the string
methods add their own "not empty" rule. Here the task follows `all`. The verdict is still
`Weak`, because the length check fails.

## Another way

Four separate `print` lines are just as good as the `zip` loop.
