# The learning rate decides

Chapter section 8.2. For `f(w) = w^2` the gradient is `2 w`, so each step multiplies `w` by `1 - 2 lr`. The program runs four steps from `w = 1` for four learning rates.

```python
for lr in [0.1, 0.5, 1.0, 1.1]:
    w = 1.0
    path = []
    for _ in range(4):
        w = w - lr * 2 * w
        path.append(f"{w:.4f}")
    print(f"lr={lr}: " + " ".join(path))
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

For `lr = 0.25` the factor is `0.5`, so the line would be `lr=0.25: 0.5000 0.2500 0.1250 0.0625`.

## After you answer

- Which learning rates converge, which oscillate, which diverge? How does the factor `1 - 2 lr` tell you?
