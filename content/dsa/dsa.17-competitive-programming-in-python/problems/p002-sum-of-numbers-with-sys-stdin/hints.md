## Hint 1

How many separate calls to the standard-input machinery does the loop `for _ in range(n): x = int(input())` make for `n = 200000`? What if you could read the whole text with one call?

## Hint 2

`sys.stdin.read()` returns **all** the text as one string. `.split()` cuts it at every whitespace (spaces and newlines) into a list of token strings.

## Hint 3

```text
data = sys.stdin.read().split()
n = int(data[0])
total = sum of int(x) for x in data[1 : 1 + n]
print(total)
```
