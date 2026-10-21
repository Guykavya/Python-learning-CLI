## Hint 1

Make the case problem disappear once, at the start. Then which method counts one letter?

## Hint 2

`low = text.casefold()`, then `low.count("a")`, `low.count("e")` and so on. Store the counts so you can add them.

## Hint 3

```
low = input().casefold()
a = low.count("a")
... e, i, o, u ...
print("a:", a)
...
print("total:", a + e + i + o + u)
```
