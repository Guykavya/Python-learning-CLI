## Hint 1

Run the tests with the starter. It returns 0 for everything. Which test fails first, and what number did it expect?

## Hint 2

You need a loop over the characters and a counter. How can you make `A` and `a` count the same way without writing ten letters? (Chapter 3: `.lower()`.)

## Hint 3

```
count = 0
for ch in text.lower():
    if ch in "aeiou":
        count += 1
return count
```
