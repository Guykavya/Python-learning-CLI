## Approach

`bool` is a subclass of `int`. `True == 1` and `False == 0`, so adding comparison results counts how many were true.

## Code

```python
a = int(input())
b = int(input())
c = int(input())
print((a > 0) + (b > 0) + (c > 0))
print((a == 0) + (b == 0) + (c == 0))
```

## Why the brackets matter

`+` has higher precedence than `>`. Without brackets, `a > 0 + b > 0` becomes the chained
comparison `a > (0 + b) > 0`, which is a single bool, not a count.

## Another way

`int(a > 0) + int(b > 0) + int(c > 0)` makes the conversion explicit. It gives the same result.
