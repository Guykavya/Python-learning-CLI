## Hint 1

Which comes first: filtering or mapping? For `parse_positive`, can you compare a string with 0?

## Hint 2

```
evens = filter(lambda n: n % 2 == 0, numbers)
return list(map(lambda n: n * n, evens))
```
For text: `map(int, text.split())` first, then filter the positives, then `list(...)`.
