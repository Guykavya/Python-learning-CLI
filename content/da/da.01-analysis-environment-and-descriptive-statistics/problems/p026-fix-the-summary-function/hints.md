## Hint 1

Take the three symptoms one at a time. Which line of the function is responsible for each one? For the median, try the list `[1, 2]` on paper: which two indexes does the even branch read, and which should it read?

## Hint 2

```text
bug 1: values.sort() reorders the caller's list -> ordered = sorted(values) and use `ordered` everywhere
bug 2: variance divides by n -> divide by (n - 1); for n == 1 return sd None
bug 3: even median uses values[n//2] and values[n//2 + 1] -> values[n//2 - 1] and values[n//2]
```
