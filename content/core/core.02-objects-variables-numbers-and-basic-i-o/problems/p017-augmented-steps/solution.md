## Approach

An augmented assignment like `n *= 3` computes `n * 3` and rebinds `n` to the result.
Because ints are immutable, each step creates a new int object.

## Code

```python
n = int(input())
n += 5
print(n)
n *= 3
print(n)
n //= 2
print(n)
n -= 1
print(n)
n **= 2
print(n)
n %= 7
print(n)
```

## Check with a negative start

For `-10`: `-5`, `-15`, `-8` (because `-15 // 2` is `-8`), `-9`, `81`, `4`.

## Another way

Write the long form `n = n + 5` and so on. It is the same for ints. The short form differs
only for mutable objects such as lists, which you will meet in core.05.
