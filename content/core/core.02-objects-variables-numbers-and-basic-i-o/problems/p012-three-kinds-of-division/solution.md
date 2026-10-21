## Approach

Use the operators that Python defines for this. They always satisfy
`(a // b) * b + (a % b) == a`, with `a // b` rounded toward negative infinity.

## Code

```python
a = int(input())
b = int(input())
print(a / b)
print(a // b)
print(a % b)
print(divmod(a, b))
```

## Why the starter is wrong

`int(-3.5)` is `-3` because `int()` cuts toward zero. Floor division goes down to `-4`.
The starter also goes through a float, so for huge ints like `10**20 + 1` it loses digits.

## Another way

`q, r = divmod(a, b)` gives both parts in one call, which is handy when you need both.
