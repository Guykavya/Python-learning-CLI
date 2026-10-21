## Hint 1

You do not know how many prices there will be. Which loop fits "keep going until something
happens"?

## Hint 2

You need two variables before the loop: a count starting at 0 and a total starting at 0.

## Hint 3

```
while True:
    line = input().strip()
    if line.lower() == "done": break
    count += 1
    total += float(line)
```
