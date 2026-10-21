## Hint 1

You cannot know how many tries the user needs. That suggests `while True:` and `break`.

## Hint 2

`int("ten")` crashes. How can `and` make sure `int()` only runs when the text is all digits?

## Hint 3

```
attempts += 1
if text.isdigit() and 1 <= int(text) <= 10:
    break
print("Invalid:", text)
```
