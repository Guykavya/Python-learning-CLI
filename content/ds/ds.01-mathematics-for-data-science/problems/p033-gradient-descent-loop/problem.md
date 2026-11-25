# Gradient descent loop

Chapter section 8.1. **Gradient descent** repeats one move: step against the gradient, `w <- w - lr * grad(w)`.

Write `gradient_descent(grad, w0, lr, steps)` returning `(w, history)`:

- `w` is the final point as a NumPy array;
- `history` is a list with the point **before the first step and after every step** (`steps + 1` arrays, each a copy).

`grad` takes a NumPy vector and returns a NumPy vector. Do not modify `w0`.

## Example

```text
grad = lambda w: 2 * (w - 3)       w0 = [0]       lr = 0.1       steps = 2
history -> [[0], [0.6], [1.08]]    w -> [1.08]
```
