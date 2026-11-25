# Cosine similarity

Chapter section 1.4. The **cosine similarity** of two vectors is their dot product divided by the product of their lengths. It is `1` for vectors pointing the same way, `-1` for opposite ones and `0` for perpendicular ones. It ignores length and compares **direction** only.

Write `cosine_similarity(x, y)` returning a float. If either vector is the zero vector, raise `ValueError("cosine is undefined for a zero vector")`.

## Example

```text
cosine_similarity([1, 0], [2, 0])   ->  1.0
cosine_similarity([1, 0], [0, 5])   ->  0.0
cosine_similarity([1, 1], [-1, -1]) -> -1.0
```
