## Hint 1

Which string method counts how many times a piece of text appears?

## Hint 2

For the second line, both the text and the letter must be converted the same way before counting.

## Hint 3

```
text = input()
letter = input()
print("Exact:", text.count(letter))
print("Any case:", text.casefold().count(letter.casefold()))
```
