## Hint 1

The sum of positions 1..r is the prefix total `p[r]`. The sum of positions 1..l-1 is `p[l-1]`. What is left when
you take the second away from the first?

## Hint 2

Build `p` once before reading the questions. With `p[0] = 0` the formula `p[r] - p[l-1]` also works for `l = 1`,
so you need no special case.

## Hint 3

```
p = [0]; for x in a: p.append(p[-1] + x)
q = int(input())
repeat q times:
    l, r = the two numbers
    print(p[r] - p[l - 1])
```
