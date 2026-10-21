## Hint 1

Which method checks how a string ends? Can it check several endings at once?

## Hint 2

`endswith` accepts a **tuple** of options: `name.endswith((".png", ".jpg"))`. Lowercase the name first for the image check, so `.JPG` matches.

## Hint 3

```
name = input()
print("Image:", name.lower().endswith((".png", ".jpg", ".jpeg", ".gif")))
print("Hidden:", name.startswith("."))
print("Backup:", name.endswith(("~", ".bak")))
```
