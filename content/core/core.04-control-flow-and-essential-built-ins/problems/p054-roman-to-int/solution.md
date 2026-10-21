## Approach

Look at each symbol together with the one after it. If it is smaller, subtract; otherwise add.
`zip` with a shifted copy gives the pairs without index arithmetic.

## Code

```python
n = int(input())
for _ in range(n):
    text = input().strip().upper()
    if not text or not all(ch in "IVXLCDM" for ch in text):
        print(f"{text} is not a Roman numeral")
        continue
    total = 0
    for ch, nxt in zip(text, text[1:] + " "):
        values = []
        for symbol in (ch, nxt):
            match symbol:
                case "I":
                    v = 1
                case "V":
                    v = 5
                case "X":
                    v = 10
                case "L":
                    v = 50
                case "C":
                    v = 100
                case "D":
                    v = 500
                case "M":
                    v = 1000
                case _:
                    v = 0
            values += [v]
        if values[0] < values[1]:
            total -= values[0]
        else:
            total += values[0]
    print(f"{text} = {total}")
```

## A simpler value lookup

`"IVXLCDM".index(ch)` gives the position of a symbol; the values `1, 5, 10, 50, 100, 500, 1000`
can then be read from a matching sequence. In the next chapter a dictionary
`{"I": 1, "V": 5, ...}` makes this one line.

## Why the extra space

The last symbol has no next symbol, so `zip` would drop it. Adding `" "` (value 0) gives it a
partner that is never bigger, so it is always added.

## Why the invalid line prints in capitals

The line is upper-cased before checking. `12` has no letters so it looks the same.
