## Approach

Separate the work into **clean**, **compute**, **report**.

1. **Clean.** Delete punctuation with a translate table, casefold, split on whitespace. Now `"Dog!"`, `"dog"` and `"DOG"` are the same word.
2. **Compute.** Every value is one expression. `max(n, 1)` is the trick that avoids a `ZeroDivisionError`: when there are no words, the numerator is 0, so the result is 0 whatever we divide by.
3. **Report.** Every line uses the same two widths, so the columns line up.

## Code

```python
import string

text = input()
target = input().strip().casefold()
table = str.maketrans("", "", string.punctuation)
words = text.translate(table).casefold().split()
n = len(words)
safe = max(n, 1)
average = len("".join(words)) / safe
longest = max(words, key=len, default="-")
count = words.count(target)

print("Text statistics")
print("=" * 26)
print(f"{'Characters':<16}{len(text):>10,}")
print(f"{'Non-space':<16}{len(''.join(text.split())):>10,}")
print(f"{'Words':<16}{n:>10,}")
print(f"{'Average length':<16}{average:>10.2f}")
print(f"{'Longest word':<16}{longest:>10}")
print(f"{'Target word':<16}{target:>10}")
print(f"{'Target count':<16}{count:>10,}")
print(f"{'Target share':<16}{count / safe:>10.1%}")
```

## Where this goes next

After lists, dictionaries and loops you can count **every** word's frequency, print the top ten, and read whole files. The cleaning and reporting parts you wrote here will stay almost the same. Notice also what this version gets wrong: curly quotes and `—` are not in `string.punctuation`, and very long words push the value column out of line, because width never cuts.
