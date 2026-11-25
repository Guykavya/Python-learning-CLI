# Trace a gradient step

Chapter section 8.1. Gradient descent moves against the gradient: `w <- w - lr * f'(w)`. Here `f(w) = (w - 3)^2`, so `f'(w) = 2 (w - 3)`.

```python
def f(w):
    return (w - 3) ** 2


def grad(w):
    return 2 * (w - 3)


w = 0.0
lr = 0.1
for step in range(1, 3):
    w = w - lr * grad(w)
    print(f"step {step}: w={w:.4f} f={f(w):.4f}")
```

Hand-trace the program and write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

If `w` started at `3.0` the gradient would be 0 and the program would print `step 1: w=3.0000 f=0.0000`.

## After you answer

- Does `w` move towards 3? Does `f` decrease? What would `lr = 1.0` do?
