## Hint 1

Which built-in turns a character into its number, and which turns a number back into a character?

## Hint 2

The format spec `04X` prints a number in uppercase hexadecimal, padded with zeros to at least 4 digits.

## Hint 3

```
ch = input()
code = ord(ch)
print("Code point:", code)
print(f"Unicode: U+{code:04X}")
print("Next:", chr(code + 1))
```
