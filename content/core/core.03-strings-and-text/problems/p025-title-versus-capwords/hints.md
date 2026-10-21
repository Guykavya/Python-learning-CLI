## Hint 1

`capwords` is not a method of strings. Where does it live, and how do you get access to it?

## Hint 2

`import string` at the top, then `string.capwords(text)`.

## Hint 3

```
import string
text = input()
print("title:", text.title())
print("capwords:", string.capwords(text))
print("capitalize:", text.capitalize())
```
