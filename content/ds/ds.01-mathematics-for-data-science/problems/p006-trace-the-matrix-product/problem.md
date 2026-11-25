# Trace the matrix product

Chapter section 2.2. Each entry of a product is a row-by-column dot product.

```python
A = [[1, 2], [3, 4]]
B = [[5, 6, 7], [8, 9, 10]]

for i in range(2):
    for j in range(3):
        parts = [A[i][k] * B[k][j] for k in range(2)]
        print(f"C[{i}][{j}] = {parts[0]} + {parts[1]} = {sum(parts)}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

If `A = [[1, 0]]` and `B = [[2], [9]]`, the program would print `C[0][0] = 2 + 0 = 2`.

## After you answer

- What is the shape of `C`?
- Compute `B x A` for the same two matrices: why does it fail?
