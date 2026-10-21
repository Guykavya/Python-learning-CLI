## Hint 1

First get rid of the spaces and dashes. Then: how do you get the last 4 characters, safely, even if there are fewer than 4?

## Hint 2

`digits[-4:]` is the last four (or fewer). `rjust(len(digits), "*")` pads it back to full length with stars on the left.

## Hint 3

```
digits = input().replace(" ", "").replace("-", "")
print("Digits:", len(digits))
print("Masked:", digits[-4:].rjust(len(digits), "*"))
```
