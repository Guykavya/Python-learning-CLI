## Hint 1

Take the symptoms one by one. Which operator makes a function change its caller's array? What dtype must an array have to hold `x /= ...` results, and what is the dtype of `np.array([3, 5, 9])`? What is `x.max()` after `x -= x.min()` when every value is 7?

## Hint 2

```text
bug 1 + 2: never use -= or /= on the input; build a new array:   (x - lo) / span    (int / int gives float)
bug 3:     span = x.max() - x.min(); if span == 0: return np.zeros(x.shape)
keep:      x.min() of an empty array already raises ValueError
```
