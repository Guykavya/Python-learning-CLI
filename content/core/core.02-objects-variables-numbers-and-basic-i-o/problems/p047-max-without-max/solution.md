## Approach

Turn the comparison into arithmetic. The sum of the two numbers and the distance between them
together determine which is larger.

## Code

```python
a = int(input())
b = int(input())
c = int(input())
big = (a + b + abs(a - b)) // 2
small = (a + b - abs(a - b)) // 2
print(big)
print(small)
print((big + c + abs(big - c)) // 2)
```

## Why `//` is exact here

`a + b + abs(a - b)` is always `2 * L`, an even number, so `// 2` loses nothing. Using `/` would
produce a float, which prints `8.0` and loses digits for huge ints like `10**30 + 1`.

## Another way

With bools as ints: `a * (a >= b) + b * (a < b)`. Exactly one comparison is `True` (1), so this
picks one number. Both tricks are good exercises; in real code use `max()`.
