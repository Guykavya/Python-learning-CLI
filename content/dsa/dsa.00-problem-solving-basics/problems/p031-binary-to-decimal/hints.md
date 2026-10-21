## Hint 1

If you have read `110` so far (value 6) and the next digit is `1`, what is the value of `1101`?
How do you get from 6 to 13 using only the old value and the new digit?

## Hint 2

Keep `value = 0` and a flag `valid = True`. For each character: if it is `"0"`, double the value; if it is `"1"`,
double and add 1; otherwise mark it invalid and stop the loop with `break`. Decide what to print after the loop.

## Hint 3

```
s = read line
value = 0, valid = True
for ch in s:
    if ch == "0": value = value * 2
    elif ch == "1": value = value * 2 + 1
    else: valid = False, break
print value if valid else "invalid"
```
