## Hint 1

Which characters cannot be typed directly inside a string? Look at the escape table in section 2 of the chapter.

## Hint 2

For line 1, surround the text with the quote type that does not cause trouble, and escape the other one with a backslash. For line 2, either double every backslash or use a raw string `r"..."`.

## Hint 3

```
print('She said "It\'s fine"')
print(r"C:\new\table")          # or "C:\\new\\table"
print("Name:\tAsha")
print("Price: \u20b9500")
print("Tab\u2192\t\u2190Tab")
```
