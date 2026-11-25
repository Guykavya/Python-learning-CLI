## Hint 1

What must stay constant for a bubble to be "proportional by area": `s / value`. So how do you scale every value to the largest one? What happens when the largest value is 0?

## Hint 2

```text
v = np.asarray(values, float)
if (v < 0).any(): raise ValueError("negative value")
top = v.max()
if top == 0: return zeros_like(v)
return max_area * v / top
```
