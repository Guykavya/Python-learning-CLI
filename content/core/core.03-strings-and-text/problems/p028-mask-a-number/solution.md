## Code

```python
digits = input().replace(" ", "").replace("-", "")
print(f"Digits: {len(digits)}")
print(f"Masked: {digits[-4:].rjust(len(digits), '*')}")
```

## Why it needs no `if`

- `digits[-4:]` never fails. For `"123"` it is `"123"`.
- `rjust` never cuts, and pads only up to the full length. With 4 or fewer characters there is nothing to pad.

## Another way

`"*" * (len(digits) - 4) + digits[-4:]`. When the length is under 4 the count is negative, and a string times a negative number is `""`. So this also works without `if`.
