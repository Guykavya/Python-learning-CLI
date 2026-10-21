## Hint 1

The table gives you the slice for every field directly. What do you need to do to each slice afterwards?

## Hint 2

`record[0:6]`, `record[6:26]`, `record[26:36]`, `record[36:46]`. Use `int()` for the numbers and `strip()` for the text. Rupees are `paise // 100`, paise are `paise % 100`.

## Hint 3

```
record = input()
acc = int(record[0:6])
name = record[6:26].strip()
city = record[26:36].strip()
paise = int(record[36:46])
print(f"ID: {acc}")
...
print(f"Amount: Rs {paise // 100:,}.{paise % 100:02}")
```
