## Approach

The gcd is associative: fold it over the list. Once `g` is known, the other two answers need a second pass
because `g` is not final until all numbers have been seen.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]

g = 0
for x in a:
    u, v = g, x
    while v:
        u, v = v, u % v
    g = u

print(g)
print(sum(1 for x in a if x == g))
print(sum(x // g for x in a))
```

## Complexity

O(n log max(a)) in the worst case, but after a few elements `g` is small and each step costs one `%`.
Two passes in all. `g` never grows; each step either keeps it or divides it.

## Another way

`functools.reduce(math.gcd, a)` does the fold in one line (`math.gcd` is a built-in Euclid). Writing the loop
yourself once is the point of the exercise.
