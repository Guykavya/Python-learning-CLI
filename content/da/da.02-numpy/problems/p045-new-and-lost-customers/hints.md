## Hint 1

"In February but not in January" is a set difference. Which NumPy function computes `a` minus `b` and returns sorted unique values (Ch. 15.5)? In which order do its arguments go?

## Hint 2

```text
new  = setdiff1d(feb, jan)
lost = setdiff1d(jan, feb)
kept = intersect1d(jan, feb)
return new, lost, kept
```
