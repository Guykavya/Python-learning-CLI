## Hint 1

`input()` gives you text. Which function turns `"36.6"` into a number you can multiply?

## Hint 2

`*` and `/` are done before `+`, and they go left to right, so `c * 9 / 5 + 32` already means
`((c * 9) / 5) + 32`. You do not need extra brackets.

## Hint 3

```
c = float(input())
print(f"F: {c * 9 / 5 + 32:.1f}")
print(f"K: {c + 273.15:.2f}")
```
