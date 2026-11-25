# Why not `inv`?

Chapter sections 16.3 and 16.4. A colleague solves systems of linear equations `A x = b` like this, because "that is the formula from the maths class":

```python
x = np.linalg.inv(A) @ b
```

Two facts measured in this course (NumPy 2.5.4):

1. On the 10 × 10 Hilbert matrix of Ch. 16.4, whose true solution is all ones, the condition number was about `1.60e+13`; the largest error was `1.69e-04` with `solve` and `5.55e-03` with `inv(A) @ b`.
2. A small, nearly singular system:

```python
A = np.array([[1.0, 1.0], [1.0, 1.0001]])
print(np.linalg.solve(A, np.array([2.0, 2.0001])))   # [1. 1.]
print(np.linalg.solve(A, np.array([2.0, 2.0002])))   # [0. 2.]
print("%.3e" % np.linalg.cond(A))                     # 4.000e+04
```

In `answer.md` write about 200 to 350 words:

1. Explain why `np.linalg.solve(A, b)` is preferred over `inv(A) @ b`: give the reason about **work** and the reason about **accuracy**.
2. Explain what the **condition number** measures, using fact 2: a change of 0.0001 in one number of `b` changed the answer from `[1, 1]` to `[0, 2]`.
3. Say roughly how many correct digits you can expect with a condition number of about `10^13` in `float64` (about 16 digits).
4. Explain what **checking the residual** `A @ x - b` tells you, and what it does **not** tell you for an ill-conditioned matrix.
5. Say when computing the inverse itself is actually justified.

Use the words *condition number*, *residual*, *solve directly* and *singular*.

## Example

"`inv(A) @ b` does two jobs where one is enough: it first computes the whole inverse matrix, then multiplies..."
