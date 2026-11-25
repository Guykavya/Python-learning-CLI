## Hint 1

Each step does two things to the vector: multiply it by `A`, then divide it by its own length. Why do you need to divide?

## Hint 2

```text
v = rng.normal(size=n); v = v / |v|
repeat: w = A @ v; v = w / |w|
value = v @ A @ v
```
