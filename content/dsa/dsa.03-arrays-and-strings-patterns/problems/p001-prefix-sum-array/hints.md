## Hint 1

If you already know `p[3]`, the sum of the first 3 elements, how do you get `p[4]` without adding the first 3 again?

## Hint 2

`p[i] = p[i-1] + a[i-1]`. Start the list with the sum of nothing, which is 0, and append one value per element.

## Hint 3

```
p = [0]
for x in a:
    p.append(last value of p + x)
print p separated by spaces
```
