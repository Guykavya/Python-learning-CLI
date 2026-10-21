## Hint 1

Which method cuts a line into words, ignoring however many spaces sit between them?

## Hint 2

`len(text.split())` is the number of words. `text.count(" ")` counts spaces.

## Hint 3

```
text = input()
print("Words:", len(text.split()))
print("Spaces:", text.count(" "))
```
