## Hint 1

Start from a copy of `w0` as floats. What do you append to `history` before the loop, and what inside the loop?

## Hint 2

```text
w = array(w0, float); history = [w.copy()]
repeat steps times: w = w - lr * grad(w); history.append(w.copy())
return w, history
```
Without `.copy()` every entry of `history` would be the same array.
