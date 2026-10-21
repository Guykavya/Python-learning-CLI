## Hint 1

If two phrases have the same letters, what do you get when you sort the letters of each?

## Hint 2

Clean with one translate table (delete `string.punctuation + string.whitespace`), casefold, then `"".join(sorted(cleaned))`.

## Hint 3

```
import string
table = str.maketrans("", "", string.punctuation + string.whitespace)
key1 = "".join(sorted(input().casefold().translate(table)))
key2 = (same for the second line)
print("Key 1:", key1)
print("Key 2:", key2)
print("Anagrams:", key1 == key2)
```
