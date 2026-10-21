## Hint 1

In a format spec, which symbols mean left, right and centre?

## Hint 2

`<` is left, `>` is right, `^` is centre. A fill character goes just before the alignment symbol. The width can be another `{}` field inside the spec.

## Hint 3

```
word = input()
width = int(input())
print(f"[{word:<{width}}]")
print(f"[{word:>{width}}]")
print(f"[{word:^{width}}]")
print(f"[{word:*^{width}}]")
```
