# Which axis is which?

Chapter sections 3.2 and 3.3. Rule: **the axis you name is the axis that disappears from the shape.** Write three
one-line functions:

- `column_means(a)`: for a 2-D table of shape `(rows, cols)`, the mean of each **column**, shape `(cols,)`.
- `row_maxes(a)`: for a 2-D table, the largest value of each **row**, shape `(rows,)`.
- `per_image_mean(stack)`: for a stack of grey images of shape `(n, h, w)`, the mean brightness of each **image**, shape `(n,)`.

Use NumPy reductions with `axis=`, no Python loops.

## Example

```python
marks = np.array([[50, 60, 70],
                  [80, 90, 100]])
column_means(marks)        # array([65., 75., 85.])   shape (3,)
row_maxes(marks)           # array([ 70, 100])        shape (2,)

stack = np.zeros((4, 2, 3)); stack[1] = 10
per_image_mean(stack)      # array([ 0., 10.,  0.,  0.])  shape (4,)
```
