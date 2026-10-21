## Approach

Turn each friend list into a set. Every line of output is one or two set operations. Sort only
when printing.

## Code

```python
a, a_rest = input().split(":")
b, b_rest = input().split(":")
a, b = a.strip(), b.strip()
fa = set(a_rest.split())
fb = set(b_rest.split())
mutual = sorted(fa & fb)
to_a = sorted(fb - fa - {a})
to_b = sorted(fa - fb - {b})
print("Mutual:", " ".join(mutual) if mutual else "none")
print(f"Suggest to {a}:", " ".join(to_a) if to_a else "none")
print(f"Suggest to {b}:", " ".join(to_b) if to_b else "none")
print("Network size:", len(fa | fb | {a, b}))
```

## Complexity

O(n + m) for the set operations, plus sorting for output.
