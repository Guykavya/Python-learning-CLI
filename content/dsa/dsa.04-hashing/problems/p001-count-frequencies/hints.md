## Hint 1

For each value, what do you want to remember? A number that changes as you read more values. Which dictionary method gives a default when the key is missing?

## Hint 2

`count[x] = count.get(x, 0) + 1`. A plain `dict` keeps keys in the order they were first inserted, so printing `count.items()` gives first-appearance order for free.

## Hint 3

```
count = {}
for x in a:
    count[x] = count.get(x, 0) + 1
for value, c in count.items():
    print(value, c)
```
