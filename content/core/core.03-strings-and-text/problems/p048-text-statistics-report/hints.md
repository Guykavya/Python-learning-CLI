## Hint 1

Break it into three parts: (1) clean the text into words, (2) compute seven values, (3) print nine lines in the same layout. Do each part separately and print intermediate values while you work.

## Hint 2

Words: `text.translate(str.maketrans("", "", string.punctuation)).casefold().split()`. Non-space: `len("".join(text.split()))`. Letters in words: `len("".join(words))`. Safe divisor: `max(len(words), 1)`.

## Hint 3

```
import string
text = input()
target = input().strip().casefold()
words = (clean text into words)
n = len(words)
safe = max(n, 1)
average = len("".join(words)) / safe
longest = max(words, key=len, default="-")
count = words.count(target)
print("Text statistics")
print("=" * 26)
print(f"{'Characters':<16}{len(text):>10,}")
... one line per value, same widths ...
print(f"{'Target share':<16}{count / safe:>10.1%}")
```
