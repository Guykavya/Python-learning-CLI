## Hint 1

How do you make a string of 6 `#` characters without typing them? What operator repeats a string?

## Hint 2

`"#" * filled + "-" * (20 - filled)` is always 20 characters. The percent format `:.0%` multiplies by 100 and adds `%`.

## Hint 3

```
done = int(input())
total = int(input())
filled = done * 20 // total
bar = "#" * filled + "-" * (20 - filled)
print(f"[{bar}] {done / total:.0%} ({done}/{total})")
```
